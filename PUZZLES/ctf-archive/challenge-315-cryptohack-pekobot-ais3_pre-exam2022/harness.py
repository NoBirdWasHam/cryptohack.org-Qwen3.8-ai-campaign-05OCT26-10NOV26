# In-process replica of server logic; validates the C1->rP oracle trick on provided code.
import os, sys
sys.path.insert(0, '.')
from elliptic_curve import Curve, Point
from random import choice, randrange
from Crypto.Util.number import bytes_to_long
a=-3; b=41058363725152142129326129780047268409114441015993725554835256314039467401291
p=2**256-2**224+2**192+2**96-1
E=Curve(p,a,b)
n=115792089210356248762697446949407573529996955224135760342422259061068512044369
G=Point(E,48439561293906451759052585252797914202762949526041747995844080717082404635286,36134250956749795798585127919587881956611106672985015071877198253568414405109)
d=randrange(1,n); P=G*d
def point_to_bytes(Pt): return Pt.x.to_bytes(32,"big")+Pt.y.to_bytes(32,"big")
def encrypt(Pt,m): return bytes([x^y for x,y in zip(m.ljust(64,b"\0"),point_to_bytes(Pt))])
QUOTES=[q.encode() for q in ["Konpeko, konpeko, konpeko! Hololive san-kisei no Usada Pekora-peko! domo, domo!","Bun bun cha! Bun bun cha!","kitira!","usopeko deshou","HA↑HA↑HA↓HA↓HA↓","HA↑HA↑HA↑HA↑","it's me pekora!","ok peko"]]
flag=b"AIS3{test_flag_local}"; flag+=os.urandom(64-len(flag))
r=randrange(1,n); C1=r*G; C2=encrypt(r*P,flag)
Q=Point(E,int.from_bytes(point_to_bytes(C1)[:32],'big'),int.from_bytes(point_to_bytes(C1)[32:],'big'))
assert Q==C1
q=choice(QUOTES); ct=encrypt(Q*d,q)
cands=[]
for qq in QUOTES:
    key=bytes(A^B for A,B in zip(ct,qq.ljust(64,b"\0")[:64]))
    f=bytes(A^B for A,B in zip(C2,key))
    i=f.find(b"}")
    if 4<i<40 and f.startswith(b"AIS3{") and all(32<=c<127 for c in f[:i+1]): cands.append(f[:i+1])
print("recovered:", cands); assert cands==[b"AIS3{test_flag_local}"], cands
print("HARNESS OK")
