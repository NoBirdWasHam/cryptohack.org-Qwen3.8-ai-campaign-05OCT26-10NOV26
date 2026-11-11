import sys; sys.path.insert(0,'.')
from aes import Sbox, Rcon, AES as PAES
import z3
from z3 import *
no_op=lambda *x:None
import os
tr=os.urandom(16)
secret=b''.join(tr[i:i+1]*4 for i in range(16))
def pycipher(mode,msg):
    c=PAES(tr)
    if mode=='mc': c._mix_columns=no_op
    else: c._shift_rows=no_op
    return c.encrypt(msg)
OBS_MC = pycipher('mc', secret[48:64])
SB = K(BitVecSort(8), BitVecVal(0,8))
for i in range(256): SB = Store(SB, BitVecVal(i,8), BitVecVal(Sbox[i],8))
def Sb(v): return Select(SB, v)
def xtime(a): return (a << 1) ^ If(Extract(7,7,a)==BitVecVal(0,1), BitVecVal(0,8), BitVecVal(0x1b,8))
k8 = [BitVec('k%d'%i,8) for i in range(8,16)]
K0 = tr[:8]
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
    if secidx is None:
        st=[[BitVecVal(0,8)]*4 for _ in range(4)]
    else:
        st=[[k8[4*(secidx-2)+i] for j in range(4)] for i in range(4)]
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
# FIX k8 to true values, add constraint, check SAT + evaluate
s=SolverFor('QF_BV')
for i in range(8): s.add(k8[i]==tr[8+i])
out=enc_weak('mc',3)
for o,v in zip(out,[BitVecVal(x,8) for x in OBS_MC]): s.add(o==v)
print('check:', s.check())
m=s.model()
print('model out:', [m.eval(o).as_long() for o in out])
print('py cipher :', list(OBS_MC))
