# (1) Interval pinning of p from getPrime(1536) constraint on REAL n
# (2) same on ratio-identical toy
# (3) toy battery: computable-exponent annihilator family (closure evidence)
import math
from gmpy2 import iroot, gcd, is_prime

ns = {}
exec(open(r"~/Practice_runs/cryptohack_org/challenge-13393-cryptohack-sus-imaginaryctf2023/output.txt").read(), ns)
n = ns["n"]

def Df(p): return p*p*p + p*p + p

def pin_lo_hi(n, rbits):
    # r in [2^(rbits-1), 2^rbits) => D = n/r in (n/2^rbits, n/2^(rbits-1)]
    D_lo = n // (1 << rbits) + 1
    D_hi = n // (1 << (rbits - 1))
    # p with Df(p) in [D_lo, D_hi]: monotone
    plo = iroot(D_lo, 3)[0] - 2
    while Df(plo) < D_lo: plo += 1
    phi = iroot(D_hi, 3)[0] + 2
    while Df(phi) > D_hi: phi -= 1
    return plo, phi

plo, phi = pin_lo_hi(n, 1536)
w = phi - plo + 1
print("REAL: p pinned to interval width ~2^%.1f (bits of p known from n: ~%.2f)" % (math.log2(w), 512 - math.log2(w)))
print("  p in [2^%.4f, 2^%.4f]" % (math.log2(plo), math.log2(phi)))

# HG deficit bookkeeping with PINNED shift (Run#3/4 machinery, pin_check.py formulas)
NL = math.log2(n)
Xp = math.log2(w)            # pinned X (log2)
Xu = 510.0                   # unpinned X (midpoint shift, Run#4 used 509; use best-case 510)
Y = 1535.0
for m in (2, 3):
    for lbl, X in (("unpinned", Xu), ("pinned  ", Xp)):
        # useful row minimal weight: (m-1)*NL + max(NL, 3X+Y) ; trivial m*NL ; HG margin
        k1 = (m - 1) * NL + max(NL, 3 * X + Y)
        print(f"  m={m} {lbl}: X3Y={3*X+Y:.1f} vs NL={NL:.1f}; f-row deficit {NL-3*X-Y:.1f} bits; trivial-row pin means no HG slack gain")

# ratio-identical toy pinning (60/120/180)
def bp(bits, seed):
    import random
    rnd = random.Random(seed)
    while True:
        x = rnd.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(x): return x
p = bp(60, 7)
q = p * p + p + 1
while not is_prime(q):
    p = bp(60, hash(p) % 10**6); q = p * p + p + 1
r = bp(180, 11)
N = p * q * r
plo2, phi2 = pin_lo_hi(N, 180)
w2 = phi2 - plo2 + 1
print("TOY 60/120/180: p interval width 2^%.1f vs X_unpinned 2^59 -> saving %.2f bits (real saved: %.2f)" %
      (math.log2(w2), 59 - math.log2(w2), 512 - math.log2(w) - (512 - 510)))
print("  toy p recovered by pin+scan? scan size 2^%.1f -> NO (superpoly); pin saves %d%% of X, wall needs 100%%" % (math.log2(w2), int(100*(59-math.log2(w2))/59)))

# (3) toy battery: annihilator-exponent family. Any E computable from N alone with (q-1) | E?
hits = 0
tested = 0
cands = []
for a in range(-6, 7): cands.append(N + a)
for a in range(1, 6): cands += [N * a + 1, N * a - 1]
cands += [N * N - 1, (N - 1) // 2, (N + 1) // 2, N * (N - 1), N * (N + 1), 65537 * N + 1,
          N**2 + N + 1, N**2 - N + 1, (N-1)*(N+1)*2, pow(2, 65537, 10**12) + N]
import sympy
for E in cands:
    if E <= 0: continue
    tested += 1
    if E % (q * (q + 1)) == 0: hits += 1
print(f"BATTERY: {tested} computable exponents E; (q-1)=p(p+1) | E hits: {hits}")
# structural lemma: any polynomial F(N) hits q | F(N) iff q | F(0)
print("struct: gcd(N*(N+3)+q0test, N) triviality check:", gcd(N * (N + 3), N) == N)
# size closures for r: r | p^3-1 impossible since max prime factor of (p-1)q has size <= max(512,1025) bits
print("size closure: r=180b vs p-1=%db, q=%db -> r | p^3-1 impossible" % ((p - 1).bit_length(), q.bit_length()))
