import json, sys, re
sys.path.insert(0, '.')
from aes import Sbox, Rcon
import z3
from z3 import *
from Crypto.Cipher import AES as FULLAES
D = json.load(open('collect.json'))
def hx(t): return bytes.fromhex(re.search(r'[0-9a-f]+', t).group(0))
OBS = {n: hx(D[n]) for n in ('mc_sec','sr_sec','mc_zero')}
K0 = bytes.fromhex(json.load(open('partial.json'))['k8_11_partial'])
SB = K(BitVecSort(8), BitVecVal(0,8))
for i in range(256): SB = Store(SB, BitVecVal(i,8), BitVecVal(Sbox[i],8))
def Sb(v): return Select(SB, v)
def xtime(a): return (a << 1) ^ If(Extract(7,7,a)==BitVecVal(0,1), BitVecVal(0,8), BitVecVal(0x1b,8))
k8 = [BitVec('k%d'%i,8) for i in range(8,16)]
rk=[]
for i in range(44):
    w=[]
    for j in range(4):
        if i<4: w.append(BitVecVal(K0[4*i+j],8) if i<2 else k8[4*(i-2)+j])
        elif i%4==0:
            rc = Rcon[i//4] if j==0 else 0
            w.append(rk[i-4][j]^Sb(rk[i-1][(j+1)%4])^BitVecVal(rc,8))
        else: w.append(rk[i-4][j]^rk[i-1][j])
    rk.append(w)
def mixrow(a):
    t=a[0]^a[1]^a[2]^a[3]
    return [a[0]^t^xtime(a[0]^a[1]),a[1]^t^xtime(a[1]^a[2]),a[2]^t^xtime(a[2]^a[3]),a[3]^t^xtime(a[3]^a[0])]
def enc_weak(mode, secidx):
    st=[[ (k8[4*(secidx-2)+i] if secidx is not None else BitVecVal(0,8)) for j in range(4)] for i in range(4)]
    if secidx is None: st=[[BitVecVal(0,8)]*4 for i in range(4)]
    for i in range(4):
        for j in range(4): st[i][j]^=rk[0+i][j]
    for r in range(1,10):
        st=[[Sb(st[i][j]) for j in range(4)] for i in range(4)]
        if mode!='sr': st=[[st[(i+j)%4][j] for j in range(4)] for i in range(4)]
        if mode!='mc': st=[mixrow(st[i]) for i in range(4)]
        for i in range(4):
            for j in range(4): st[i][j]^=rk[4*r+i][j]
    st=[[Sb(st[i][j]) for j in range(4)] for i in range(4)]
    if mode!='sr': st=[[st[(i+j)%4][j] for j in range(4)] for i in range(4)]
    for i in range(4):
        for j in range(4): st[i][j]^=rk[40+i][j]
    return [st[i][j] for i in range(4) for j in range(4)]
s = SolverFor('QF_BV')
s.set('timeout', 400000); s.set('random_seed', 3)
for out, ob in ((enc_weak('mc',3),OBS['mc_sec']),(enc_weak('sr',2),OBS['sr_sec']),(enc_weak('mc',None),OBS['mc_zero'])):
    for o,v in zip(out,[BitVecVal(x,8) for x in ob]): s.add(o==v)
print('solving', flush=True)
if s.check()==z3.sat:
    m=s.model(); key=K0+bytes(m.eval(v).as_long()&0xff for v in k8)
    print('key',key.hex())
    from aes import AES
    no_op=lambda *x:None
    ok=True
    for mode,off,obn in (('mc',3,'mc_sec'),('sr',2,'sr_sec')):
        c=AES(key)
        if mode=='mc': c._mix_columns=no_op
        else: c._shift_rows=no_op
        secret=b''.join(key[i:i+1]*4 for i in range(16))
        if c.encrypt(secret[16*off:16*off+16])!=OBS[obn]: ok=False
    print('verify',ok)
    if ok:
        pt=FULLAES.new(key,FULLAES.MODE_ECB).decrypt(hx(D['banner']))
        print('pt',pt)
        if pt.startswith(b'hkcert21{') and all(32<=b<127 for b in pt):
            open('flag_sratslla_sea-hkcert_ctf2021.txt','w').write(pt.decode()); print('FLAG SAVED')
else: print('UNSAT')
