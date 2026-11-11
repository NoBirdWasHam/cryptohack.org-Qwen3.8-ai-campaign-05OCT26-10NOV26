# Deterministic ground-truth end-to-end test (digits need not be prime).
import random, sys, time
sys.path.insert(0, ".")
from Crypto.Util.number import getPrime
from attack import solve_instance, _solve_with_pairs, recover_stream

def run(seed, qbits=120, Ts=(5, 183, 344, 736, 1080, 1106, 1445, 1602)):
    random.seed(seed)
    q = getPrime(qbits)
    a2 = random.randrange(1, q); x2 = random.randrange(1, q); b2 = random.randrange(1, q)
    a3 = random.randrange(1, q); x3 = random.randrange(1, q); b3 = random.randrange(1, q)
    def val(a, x, b, j):
        if a == 1: return (x + (j-1)*b) % q
        D = (-b) * pow(a-1, q-2, q) % q
        C = (x - D) % q
        return (C*pow(a, j-1, q) + D) % q
    p = {j: val(a3, x3, b3, j)*q*q + val(a2, x2, b2, j)*q + j for j in Ts}
    pairs = [(Ts[2*i], Ts[2*i+1]) for i in range(4)]
    ns = [p[Ts[2*i]] * p[Ts[2*i+1]] for i in range(4)]
    out = _solve_with_pairs(q, ns, pairs, verbose=False)
    return out is not None

ok = 0
tries = 10
for s in range(tries):
    t0 = time.time()
    r = run(1000 + s)
    ok += r
    print("seed", 1000+s, "OK" if r else "FAIL", "%.1fs" % (time.time()-t0), flush=True)
print("%d/%d" % (ok, tries))
