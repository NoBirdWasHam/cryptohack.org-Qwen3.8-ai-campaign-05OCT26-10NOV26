import random
from Crypto.Util.number import bytes_to_long
n,q=512,127
def cm(a,b):
    o=[0]*n
    for i,ai in enumerate(a):
        if ai:
            for j,bj in enumerate(b):
                if bj: o[(i+j)%n]+=ai*bj
    return o
def rp(d):
    f=[0]*n
    for i in random.sample(range(n),d): f[i]=1
    return f
flag=b"NNS{selftest_flag_placeholder_for_decrypt_logic_check!!}"
val=bytes_to_long(flag)
m=[(val>>i)&1 for i in range(n)]
f=rp(35);g=rp(35);r=rp(22)
S=[2*x+y for x,y in zip(cm(g,r),cm(f,m))]
print("max S coeff:", max(S), "(must be <127)")
B=[s&1 for s in S]
# gf2 solve reusing solve.py code
import importlib.util
src=open("solve.py").read().split("seen = set()")[0]
src=src.replace("from fpylll import IntegerMatrix, BKZ","")
exec(src[src.index("def cyclic_mul"):])
x=gf2_solve_unit(f,B)
mb=bytearray()
for b in range(0,n,8):
    byte=0
    for k in range(8): byte|=((x>>(b+k))&1)<<k
    mb.append(byte)
print("recovered:", mb.rstrip(b"\x00"))
print("bits match:", sum(((x>>i)&1) != m[i] for i in range(n)))
print("rev match:", sum(((x>>i)&1) != m[511-i] for i in range(n)))
import pickle; pickle.dump((f,B,m),open("dbg.pkl","wb"))
