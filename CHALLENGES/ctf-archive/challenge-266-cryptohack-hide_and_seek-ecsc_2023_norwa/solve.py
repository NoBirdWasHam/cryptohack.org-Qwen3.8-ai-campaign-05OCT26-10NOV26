# hide_and_seek (ECSC 2023 Norway) — smooth-order EC DLP
# From tuples (a_i,b_i,R_i=a_i*P+b_i*Q), Q=x*P:
#   S=b_i R_j - b_j R_i = (a_j b_i - a_i b_j) P ;  T=a_j R_i - a_i R_j = Delta*x*P
#   P = Delta^-1 S, X = Delta^-1 T, then PH-DLP  X = x P  (n = #E is 9 smooth primes ~34bit)
import re, math
from Crypto.Util.number import long_to_bytes

p = 1789850433742566803999659961102071018708588095996784752439608585988988036381340404632423562593
ac = 62150203092456938230366891668382702110196631396589305390157506915312399058961554609342345998
bc = 1005820216843804918712728918305396768000492821656453232969553225956348680715987662653812284211
t = 16093597302722077219468084775737143208134062101   # trace of Frobenius (PARI ellap)
n = p + 1 - t
facs = [12775224751,13026062843,18511195699,24508446437,25961704469,28450356619,31034521019,31982226581,32337773063]
assert math.prod(facs) == n

INV = None
def add(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1,y1 = P1; x2,y2 = P2
    if x1==x2 and (y1+y2)%p==0: return None
    if P1==P2:
        m = (3*x1*x1+ac)*pow(2*y1,-1,p)%p
    else:
        m = (y2-y1)*pow(x2-x1,-1,p)%p
    x3 = (m*m-x1-x2)%p
    y3 = (m*(x1-x3)-y1)%p
    return (x3,y3)

def mul(k, P1):
    R = None; Q1 = P1
    while k:
        if k&1: R = add(R,Q1)
        Q1 = add(Q1,Q1); k >>= 1
    return R

def bsgs(Q, Y, order):
    # Y = x Q, 0<=x<order
    m = math.isqrt(order)+1
    table = {}
    acc = None
    for j in range(m):
        if acc not in table: table[acc]=j
        acc = add(acc,Q)
    ng = mul(-m,Q)
    cur = Y
    for i in range(m):
        if cur in table:
            x = i*m + table[cur]
            if x < order and mul(x,Q)==Y: return x
        cur = add(cur, ng)
    raise ValueError("bsgs fail")

# parse output.txt
txt = open("output.txt").read()
tri = re.findall(r"\((\d+),\s*(\d+),\s*\((\d+)\s*:\s*(\d+)\s*:\s*1\)\)", txt)
assert len(tri)==42, len(tri)
data = [(int(a),int(b),(int(x),int(y))) for a,b,x,y in tri]

# recover P and X=xP from first non-degenerate pair
P = X = None
for i in range(42):
    for j in range(i+1,42):
        ai,bi,Ri = data[i]; aj,bj,Rj = data[j]
        D = (aj*bi - ai*bj) % n
        if D==0: continue
        S = add(mul(bi,Rj), mul(-bj,Ri))
        T = add(mul(aj,Ri), mul(-ai,Rj))
        if S is None: continue
        Dinv = pow(D,-1,n)
        P = mul(Dinv,S); X = mul(Dinv,T)
        break
    if P: break
assert P and X
assert mul(n,P) is None, "order check failed"
# verify consistency: R_0 = (a0 + b0 x)P unknown x; instead verify each R on curve & subgroup
for _,bi,(x,y) in data[:3]:
    assert (y*y - (x*x*x+ac*x+bc)) % p == 0

res = []
for q in facs:
    h = n//q
    Q2 = mul(h,P); Y2 = mul(h,X)
    res.append((bsgs(Q2,Y2,q), q))
xs = [r for r,_ in res]; qs = [q for _,q in res]
# CRT
x = 0; M = 1
for xi,qi in zip(xs,qs):
    M2 = M
    inv = pow(M,-1,qi)
    x = (x + M*((xi-x)*inv % qi)) % (M*qi)
    M *= qi
assert M == n and mul(x,P)==X
flag = "ECSC{" + long_to_bytes(x).decode() + "}"
print("FLAG:", flag)
open("flag_hide_and_seek-ecsc_2023_norwa.txt","w").write(flag)
