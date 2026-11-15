import sys, json, re; sys.path.insert(0,'.')
from aes import Sbox, Rcon, AES as PAES
import z3
from z3 import *
no_op=lambda *x:None
D=json.load(open('collect.json'))
def hx(t): return bytes.fromhex(re.search(r'[0-9a-f]+', t).group(0))
K0=bytes.fromhex(json.load(open('partial.json'))['k8_11_partial'])
SB = K(BitVecSort(8), BitVecVal(0,8))
for i in range(256): SB=Store(SB,BitVecVal(i,8),BitVecVal(Sbox[i],8))
def Sb(v): return Select(SB,v)
def xtime(a): return (a<<1)^If(Extract(7,7,a)==BitVecVal(0,1),BitVecVal(0,8),BitVecVal(0x1b,8))
k8=[BitVec('k%d'%i,8) for i in range(8,16)]
rk=[]
for i in range(44):
    w=[]
    for j in range(4):
        if i<4: w.append(BitVecVal(K0[4*i+j],8) if i<2 else k8[4*(i-2)+j])
        elif i%4==0:
            rc=Rcon[i//4] if j==0 else 0
            w.append(rk[i-4][j]^Sb(rk[i-1][(j+1)%4])^BitVecVal(rc,8))
        else: w.append(rk[i-4][j]^rk[i-1][j])
    rk.append(w)
def mixrow(a):
    t=a[0]^a[1]^a[2]^a[3]
    return [a[0]^t^xtime(a[0]^a[1]),a[1]^t^xtime(a[1]^a[2]),a[2]^t^xtime(a[2]^a[3]),a[3]^t^xtime(a[3]^a[0])]
def enc_weak(mode, secidx):
    if secidx is None: st=[[BitVecVal(0,8)]*4 for _ in range(4)]
    else: st=[[k8[4*(secidx-2)+i] for j in range(4)] for i in range(4)]
    for i in range(4):
        for j in range(4): st[i][j]^=rk[i][j]
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
secret_for=lambda key:b''.join(key[i:i+1]*4 for i in range(16))
def check_key(key):
    ok=True
    for name,mode,off in (('mc_zero','mc',None),('mc_sec','mc',48),('sr_zero','sr',None),('sr_sec','sr',32)):
        c=PAES(key)
        if mode=='mc': c._mix_columns=no_op
        else: c._shift_rows=no_op
        m=b'\x00'*16 if off is None else secret_for(key)[off:off+16]
        if c.encrypt(m)!=hx(D[name]): ok=False; break
    return ok
s=Solver()   # sound logic detection (arrays)
s.set('timeout', 300000)
for o,v in zip(enc_weak('mc',None),[BitVecVal(x,8) for x in hx(D['mc_zero'])]): s.add(o==v)
n=0
while n<8:
    r=s.check()
    print('check',n,r,flush=True)
    if r!=z3.sat: break
    m=s.model(); key=K0+bytes(m.eval(v).as_long()&0xff for v in k8)
    print('cand',key.hex(),'fullverify',check_key(key),flush=True)
    if check_key(key):
        print('KEY FOUND',key.hex()); break
    s.add(Or([k8[i]!=m.eval(k8[i]) for i in range(8)]))
    n+=1
