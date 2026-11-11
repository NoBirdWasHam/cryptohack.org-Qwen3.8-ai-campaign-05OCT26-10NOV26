# Ground-truth probe at 342-bit scale: is true a2 in gcd and intersection?
import sys, random, time
sys.path.insert(0, ".")
from Crypto.Util.number import getPrime
from attack import poly_from_terms, eval_poly, p_gcd, roots_general, p_powmod, p_strip
random.seed(4242)
q = getPrime(342)
a2 = random.randrange(1, q); x2 = random.randrange(1, q); b2 = random.randrange(1, q)
D2 = b2*pow(a2-1, q-2, q) % q
C2 = (x2 - D2) % q
L2 = lambda j: (C2*pow(a2, j-1, q) + D2) % q
Ts = [50, 1300, 1700, 3600, 4100, 4700, 5200, 5900]
pairs = [(Ts[2*i], Ts[2*i+1]) for i in range(4)]
R2 = [(L2(u)*v + L2(v)*u) % q for u, v in pairs]
P = []; Qs = []; Rs = []
for (u, v), R in zip(pairs, R2):
    P.append({u: v % q, v: u % q}); Qs.append((u+v) % q); Rs.append(R % q)
def det3(i, j, k):
    ci = (Qs[j]*Rs[k] - Qs[k]*Rs[j]) % q
    cj = -(Qs[i]*Rs[k] - Qs[k]*Rs[i]) % q
    ck = (Qs[i]*Rs[j] - Qs[j]*Rs[i]) % q
    terms = {}
    for idx, c in ((i, ci), (j, cj), (k, ck)):
        if c == 0: continue
        for e, cc in P[idx].items():
            terms[e] = (terms.get(e, 0) + c*cc) % q
    return poly_from_terms(terms, q)
t0 = time.time()
d1 = det3(0, 1, 2); d2 = det3(0, 1, 3)
print("deg d1,d2:", len(d1)-1, len(d2)-1)
print("d1(a2):", eval_poly(d1, a2, q), " d2(a2):", eval_poly(d2, a2, q))
h = p_gcd(d1[:], d2[:], q)
print("deg h:", len(h)-1, " h(a2):", eval_poly(h, a2, q), "%.1fs" % (time.time()-t0))
t0 = time.time()
xq = p_powmod([0, 1], q, h[:], q) if len(h)-1 <= 60 else None
from attack import p_powmod_fast
if xq is None:
    xq = p_powmod_fast([0, 1], q, h[:], q)
while len(xq) < 2: xq.append(0)
xq[1] = (xq[1]-1) % q
p_strip(xq)
inter = p_gcd(h[:], xq, q, stop_deg=10**9)
print("deg inter:", len(inter)-1, " inter(a2):", eval_poly(inter, a2, q), "%.1fs" % (time.time()-t0))
t0 = time.time()
rts = roots_general(h[:], q)
print("roots_general(h):", len(rts), " a2 in:", a2 in rts, "%.1fs" % (time.time()-t0))
