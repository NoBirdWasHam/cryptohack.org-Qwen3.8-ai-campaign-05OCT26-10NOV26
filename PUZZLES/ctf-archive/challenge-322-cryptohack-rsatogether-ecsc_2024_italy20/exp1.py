# Experiment: simulate server EXACTLY at NB=1024, test linear-algebra attack candidates.
import random, sys
from math import comb, gcd, isqrt
from Crypto.Util.number import getPrime, bytes_to_long, long_to_bytes
random = random.SystemRandom()

NB = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
p = getPrime(NB//2); q = getPrime(NB//2); n = p*q; phi = (p-1)*(q-1); e = 65537
d = pow(e, -1, phi)
poly = [d] + [random.getrandbits(NB) for _ in range(99)]

def eval_poly(pl, x, nn):
    return sum(pow(x, i, nn)*pl[i] for i in range(len(pl))) % nn

def server_yours(kinp):
    ns = kinp + 1
    pl = poly[:ns]
    ys = [eval_poly(pl, i, phi) for i in range(1, ns+1)]
    coeffs = [(-1)**(i-1)*comb(ns, i) for i in range(1, ns+1)]  # Lagrange-at-0 weights
    shares = [(c*y) % phi for c, y in zip(coeffs, ys)]
    return shares.pop(ns - 2)

ours = {k: server_yours(k) for k in range(1, 102)}  # k = input, x=k share, m=k+1 nodes

# ---- model check: u_k = beta_k * Pk(k) - phi*t_k with beta = (-1)^(k-1)*(k+1), Pk = poly[:k+1]
t = {}
for k in range(1, 102):
    beta = (-1)**(k-1)*(k+1)
    Pk = sum(poly[i]*k**i for i in range(min(k, 99)+1))
    # u = beta*Pk mod phi
    assert ours[k] == (beta*Pk) % phi, k
    t[k] = (beta*Pk - ours[k]) // phi
print("model ok; t_k max bits:", max(abs(t[k]).bit_length() for k in range(1, 102)))

# ---- exact rational nullspace of 101x100 system (cols j=0..99, rows k=1..101), entries beta*k^j (j<=k)
from fractions import Fraction as F
rows = list(range(1, 102))
A = [[ (F((-1)**(k-1)*(k+1)*(k**j)) if j <= k else F(0)) for j in range(100)] for k in rows]
# solve nu A = 0 over Q: use sympy QQ nullspace on A.T
from sympy import Matrix, Rational, lcm as syc_lcm
Mm = Matrix([[A[ii][jj] for jj in range(100)] for ii in range(101)])
ns = Mm.T.nullspace()
print("nullspace dim:", len(ns))
assert len(ns) == 1
v = [x for x in ns[0]]
Dv = 1
from functools import reduce
for x in v:
    Dv = Dv * x.q // gcd(Dv, x.q)
mu = [int(x*Dv) for x in v]
g = reduce(gcd, [abs(x) for x in mu if x])
mu = [x//g for x in mu]
Dv //= g
print("D bits:", Dv.bit_length(), "mu max bits:", max(abs(x).bit_length() for x in mu))

# S0 = sum mu*u  -> should be 0 mod phi (kills d too)
S0 = sum(mu[i]*ours[rows[i]] for i in range(101))
print("S0 multiple of phi:", S0 % phi == 0)
print("T0 bits:", (S0//phi).bit_length())

# ---- now: nullspace killing cols 1..99 only, normalize col0 = D (integer version):
# solve nu A[:,1:] = 0, then scale so col0 coeff = 1 rational.
M2 = Matrix([[A[ii][jj] for jj in range(1, 100)] for ii in range(101)])
ns2 = M2.T.nullspace()
print("dim kill-a only:", len(ns2))
w = ns2[0]
c0 = sum(w[i]*A[i][0] for i in range(101))
print("col0 coeff of raw w:", c0)
# normalize: nu = w / c0 ; denominators
v2 = [x/c0 for x in w]
D = 1
for x in v2:
    D = D * x.q // gcd(D, x.q)
nu = [int(x*D) for x in v2]
g = reduce(gcd, [abs(x) for x in nu if x])
nu = [x//g for x in nu]; D //= g
print("D(bits)=", D.bit_length(), " nu max bits:", max(abs(x).bit_length() for x in nu))
S = sum(nu[i]*ours[rows[i]] for i in range(101))
# S = D*d + phi*T
rhs = S - D*d
print("S - D*d divisible by phi:", rhs % phi == 0)
Tb = (rhs//phi).bit_length()
print("T bits:", Tb, " M = e*(S-?)... M bits est:", (e*abs(S)+D).bit_length(), " (need < 3071 for window trick)")
# window test at THIS small size: M = e*S - D = phi * (D*h + e*T)
Mv = e*S - D
print("M multiple of phi:", Mv % phi == 0)
Cand = round(Mv/n)
found = None
for C in range(max(1, Cand-4), Cand+5):
    if Mv % C: continue
    ph = Mv//C
    ss = n - ph + 1
    Dsc = ss*ss - 4*n
    if Dsc > 0:
        rr = isqrt(Dsc)
        if rr*rr == Dsc and (ss-rr) % 2 == 0:
            pp = (ss-rr)//2
            if pp*(ss-pp) == n:
                found = ph
print("FOUND phi via window:", found == phi)
open("sim_algebra.log", "w").write("done\n")
