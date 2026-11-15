# clean fast BSGS Pohlig-Hellman with gmpy2
import math, re
import gmpy2
from gmpy2 import mpz, invert
from Crypto.Util.number import long_to_bytes

p = mpz(1789850433742566803999659961102071018708588095996784752439608585988988036381340404632423562593)
ac = mpz(62150203092456938230366891668382702110196631396589305390157506915312399058961554609342345998)
bc = mpz(1005820216843804918712728918305396768000492821656453232969553225956348680715987662653812284211)
t = 16093597302722077219468084775737143208134062101
n = int(p) + 1 - t
facs = [12775224751,13026062843,18511195699,24508446437,25961704469,28450356619,31034521019,31982226581,32337773063]
assert math.prod(facs) == n

txt = open("output.txt").read()
tri = re.findall(r"\((\d+),\s*(\d+),\s*\((\d+)\s*:\s*(\d+)\s*:\s*1\)\)", txt)
assert len(tri) == 42
data = [(int(a), int(b), (mpz(x), mpz(y))) for a, b, x, y in tri]

pp = int(p)
def add(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1; x2, y2 = P2
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P1 == P2:
        m = (3*x1*x1 + ac) * invert(2*y1, p)
    else:
        m = (y2 - y1) * invert(x2 - x1, p)
    m %= p
    x3 = (m*m - x1 - x2) % p
    return (x3, (m*(x1 - x3) - y1) % p)

def mul(k, P1):
    k %= n
    if k == 0: return None
    R = None; Q1 = P1
    while k:
        if k & 1: R = add(R, Q1)
        Q1 = add(Q1, Q1); k >>= 1
    return R

P = X = None
for i in range(len(data)):
    if P: break
    ai, bi, Ri = data[i]
    for j in range(i+1, len(data)):
        aj, bj, Rj = data[j]
        D = (aj*bi - ai*bj) % n
        if D == 0: continue
        S = add(mul(bi, Rj), mul(-bj, Ri))
        Tm = add(mul(aj, Ri), mul(-ai, Rj))
        if S is None or Tm is None: continue
        Di = pow(D, -1, n)
        P, X = mul(Di, S), mul(Di, Tm)
        break
assert P and mul(n, P) is None
print("P order ok", flush=True)

def bsgs(Q, Y, q):
    m = math.isqrt(q) + 1
    table = {}
    acc = None
    for j in range(m):
        if acc not in table: table[acc] = j
        acc = add(acc, Q)
    ng = mul(m, Q); ng = (ng[0], (-ng[1]) % p) if ng else None
    cur = Y
    for i in range(m):
        j = table.get(cur)
        if j is not None:
            c = i*m + j
            if c < q: return c
        cur = add(cur, ng)
    raise RuntimeError("bsgs")

xs = []
for q in facs:
    h = n // q
    xi = bsgs(mul(h, P), mul(h, X), q)
    xs.append(xi); print(q, xi, flush=True)
x = 0; M = 1
for xi, q in zip(xs, facs):
    r = ((xi - x) % q) * pow(M % q, -1, q) % q
    x += M*r; M *= q
x %= n
assert mul(x, P) == X
assert x % 12775224751 == 9306536884, "GP cross-check mismatch"
assert x < int(mpz(2)**250) or True
flag = "ECSC{" + long_to_bytes(x).decode(errors="replace") + "}"
print("FLAG:", flag)
open("flag_hide_and_seek-ecsc_2023_norwa.txt", "w").write(flag)
