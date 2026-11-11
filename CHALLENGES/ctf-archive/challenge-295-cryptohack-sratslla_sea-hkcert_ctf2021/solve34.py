import json, sys, re
sys.path.insert(0, '.')
from aes import Sbox, Rcon
import z3
from z3 import BitVec, BitVecVal, BitVecSort, Array, Store, K, Select, Solver, If, Extract, And, Or, Not
from Crypto.Cipher import AES as FULLAES

D = json.load(open('collect.json'))
def hx(t): return bytes.fromhex(re.search(r'[0-9a-f]+', t).group(0))
OBS = {n: hx(D[n]) for n in ('mc_zero','mc_sec','sr_zero','sr_sec')}
K0 = bytes.fromhex(json.load(open('partial.json'))['k8_11_partial'])

SB = K(BitVecSort(8), BitVecVal(0,8))
for i in range(256):
    SB = Store(SB, BitVecVal(i,8), BitVecVal(Sbox[i],8))
def Sb(v): return Select(SB, v)
def xtime(a): return (a << 1) ^ If(Extract(7,7,a)==BitVecVal(0,1), BitVecVal(0,8), BitVecVal(0x1b,8))

# key schedule: 44 words x 4 bytes
k8 = [BitVec('k%d'%i,8) for i in range(8,16)]
rk = []
for i in range(44):
    word = []
    for j in range(4):
        if i < 4:
            word.append(BitVecVal(K0[4*i+j],8) if i<2 else k8[4*(i-2)+j])
        elif i % 4 == 0:
            rc = Rcon[i//4] if j==0 else 0
            word.append(rk[i-4][j] ^ Sb(rk[i-1][(j+1)%4]) ^ BitVecVal(rc,8))
        else:
            word.append(rk[i-4][j] ^ rk[i-1][j])
    rk.append(word)

def mixrow(a):  # a = list of 4 z3 bytes (row i = word i)
    t = a[0]^a[1]^a[2]^a[3]
    return [a[0]^t^xtime(a[0]^a[1]), a[1]^t^xtime(a[1]^a[2]),
            a[2]^t^xtime(a[2]^a[3]), a[3]^t^xtime(a[3]^a[0])]

def sr_perm(st):  # in-place semantics: new[i][j] = old[(i+j)%4][j]
    return [[st[(i+j)%4][j] for j in range(4)] for i in range(4)]

def enc_weak(msgbytes, mode):
    st = [[msgbytes[4*i+j] for j in range(4)] for i in range(4)]
    for i in range(4):
        for j in range(4): st[i][j] ^= rk[0+i][j]
    for r in range(1,10):
        if mode=='sb': pass
        else: st = [[Sb(st[i][j]) for j in range(4)] for i in range(4)]
        if mode!='sr': st = sr_perm(st)
        if mode!='mc': st = [mixrow(st[i]) for i in range(4)]
        for i in range(4):
            for j in range(4): st[i][j] ^= rk[4*r+i][j]
    st = [[Sb(st[i][j]) for j in range(4)] for i in range(4)]
    if mode!='sr': st = sr_perm(st)
    for i in range(4):
        for j in range(4): st[i][j] ^= rk[40+i][j]
    return [st[i][j] for i in range(4) for j in range(4)]

def konst(b): return [BitVecVal(x,8) for x in b]
def secret_slice(keybytes, idx):  # slice idx (0..3): byte 4i+j = keybyte[4*idx+i]... per chall: secret[p]=k[p//4]
    out = []
    for i in range(4):
        for j in range(4):
            p = 4*(idx-2) + i   # index into k8..k15 list
            out.append(keybytes[p])
    return out

Z = konst(b'\x00'*16)
msec = secret_slice(k8, 3)   # uses k12..k15 -> z3 vars
ssec = secret_slice(k8, 2)   # uses k8..k11 -> z3 vars

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    import os, random
    from aes import AES as T_AES
    no_op = lambda *x: None
    tr = os.urandom(16)
    secret = b''.join(tr[i:i+1]*4 for i in range(16))
    def tenc(mode, msg):
        c = T_AES(tr)
        if mode=='mc': c._mix_columns=no_op
        else: c._shift_rows=no_op
        return c.encrypt(msg)
    OBS = {'mc_sec': tenc('mc', secret[48:64]), 'sr_sec': tenc('sr', secret[32:48]),
           'mc_zero': tenc('mc', b'\0'*16), 'sr_zero': tenc('sr', b'\0'*16)}
    K0 = tr[:8]
    TRUEKEY = tr
    print('test key', tr.hex())
    # rebuild schedule with test K0
    rk = []
    for i in range(44):
        word = []
        for j in range(4):
            if i < 4:
                word.append(BitVecVal(K0[4*i+j],8) if i<2 else k8[4*(i-2)+j])
            elif i % 4 == 0:
                rc = Rcon[i//4] if j==0 else 0
                word.append(rk[i-4][j] ^ Sb(rk[i-1][(j+1)%4]) ^ BitVecVal(rc,8))
            else:
                word.append(rk[i-4][j] ^ rk[i-1][j])
        rk.append(word)

s = Solver()
for out, mode, msg, ob in (
    (enc_weak(msec,'mc'), 'mc', None, OBS['mc_sec']),
    (enc_weak(Z,'mc'), 'mc', None, OBS['mc_zero']),
    (enc_weak(ssec,'sr'), 'sr', None, OBS['sr_sec']),
    (enc_weak(Z,'sr'), 'sr', None, OBS['sr_zero']),
):
    for o,v in zip(out, konst(ob)):
        s.add(o==v)

print('solving...', flush=True)
if s.check() == z3.sat:
    m = s.model()
    key = K0 + bytes(m.eval(v).as_long() & 0xff for v in k8)
    print('key:', key.hex())
    # local verify of weak stages
    from aes import AES
    no_op=lambda *x:None
    ok=True
    for name, mode, msgoff, ob in (('mc_sec','mc',3,'mc_sec'),('mc_zero','mc',None,'mc_zero'),('sr_sec','sr',2,'sr_sec'),('sr_zero','sr',None,'sr_zero')):
        c = AES(key)
        if mode=='mc': c._mix_columns=no_op
        else: c._shift_rows=no_op
        if msgoff is None:
            secret=b''.join(key[i:i+1]*4 for i in range(16)); m2=secret[48:64] if mode=='mc' else secret[32:48]
        else:
            secret=b''.join(key[i:i+1]*4 for i in range(16)); m2=secret[16*msgoff:16*msgoff+16]
        if c.encrypt(m2)!=OBS[ob]: ok=False
    print('weak-stage verify:', ok)
    if 'banner' in D and ok:
        pt = FULLAES.new(key, FULLAES.MODE_ECB).decrypt(hx(D['banner']))
        print('flag pt:', pt)
        if pt.startswith(b'hkcert21{') and all(32<=b<127 for b in pt):
            open('flag_sratslla_sea-hkcert_ctf2021.txt','w').write(pt.decode())
            print('FLAG SAVED')
else:
    print('UNSAT/FAIL')
