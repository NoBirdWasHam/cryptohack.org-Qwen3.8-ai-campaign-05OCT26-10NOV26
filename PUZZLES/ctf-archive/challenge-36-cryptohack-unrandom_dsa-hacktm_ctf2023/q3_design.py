#!/usr/bin/env python3
# Design test: 3-prime q = f1*f2*f3, f_i = 1 + t_i*M0 (M0 even), Korselt via
#   t2 = t1 + m1*t1 - m2 , t3 = t1 + m1*t1 + m2*t2   (then t1 | t2,t3 auto)
# Need t1 | M0*(m1^2+m2^2). MR-strong for all bases iff v2(f_i-1) < v2(q-1)=v2(M0).
import random, time, math
from sympy import isprime
from Crypto.Util.number import getPrime
from Crypto.Math.Primality import test_probable_prime, lucas_test, PROBABLY_PRIME
from Crypto.Math.Numbers import Integer

FB = 40  # target factor bits (odd part ~2^39.2)

def find_q(rng, tries=400000):
    # t1: even, ~44 bits (t2,t3 gain ~2^21)
    for _ in range(tries):
        t1 = (rng.getrandbits(43) << 1) | 2
        m1 = rng.randrange(1, 2**21)
        # t1 | M0*(m1^2+m2^2), M0 = 2*t1 -> need m1^2+m2^2 even -> m2 odd if m1 odd
        m2 = (rng.getrandbits(21) << 1) | 1
        t2 = t1 + m1*t1 - m2
        t3 = t1 + m1*t1 + m2*t2
        if min(t1, t2, t3) <= 0: continue
        bl = [t.bit_length() for t in (t1, t2, t3)]
        if not (38 <= min(bl) and max(bl) <= 41): continue
        M0 = 2*t1
        if (M0*(m1*m1 + m2*m2)) % t1: continue
        f1, f2, f3 = M0*t1+1, M0*t2+1, M0*t3+1
        if not (isprime(f1) and isprime(f2)): continue
        if not isprime(f3): continue
        q = f1*f2*f3
        # Korselt: (f_i-1) | (q-1)?
        ok = all((q-1) % (f-1) == 0 for f in (f1, f2, f3))
        if not ok: continue
        # v2(f_i-1) < v2(M0) for all i
        vM = (M0 & -M0).bit_length()-1
        vs = [((f-1) & -(f-1)).bit_length()-1 for f in (f1, f2, f3)]
        if max(vs) >= vM: continue
        # odd parts prime (for smooth order)
        if not all(isprime((f-1) >> ((f-1) & -(f-1)).bit_length()+1... ) for f in ()): pass
        return q, (f1, f2, f3), M0
    return None

# quick structural pass first (no odd-part-primality), then measure accept rate
t0 = time.time()
n_q = 0
for it in range(3000):
    rng = random.Random(1000+it)
    r = find_q(rng, tries=20000)
    if not r: continue
    n_q += 1
    q, facs, M0 = r
    mr = test_probable_prime(q)
    lu = lucas_test(Integer(q))
    print(f"it={it} q={q} bits={q.bit_length()} facs={[f.bit_length() for f in facs]} MR={mr} lucas={lu}", flush=True)
    if n_q >= 8: break
print("done", n_q, round(time.time()-t0,1), "s")
