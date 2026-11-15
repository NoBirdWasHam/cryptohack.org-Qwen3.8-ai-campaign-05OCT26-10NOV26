# Tiny end-to-end validation of the dual-isogeny attack on an analogous curve.
import random
from isog_lib import F, EC, build_chain, recover_n

import gmpy2
random.seed(1)
for e_a, e_b in [(8, 5), (10, 3), (12, 4)]:
    p = 2**e_a * 3**e_b - 1
    if not gmpy2.is_prime(p):
        print(f"e_a={e_a}, e_b={e_b}: p={p} not prime, skip"); continue
    Fp2 = F(p)
    E = EC(Fp2, Fp2.zero(), Fp2.one())
    # find two independent generators of E[2^e_a]
    cof = 3**e_b
    def rand_point():
        while True:
            x = (random.randrange(p), random.randrange(p))
            rhs = Fp2.add(Fp2.mul(x, Fp2.mul(x, x)), Fp2.one())
            try:
                y = Fp2.sqrt(rhs)
            except ValueError:
                continue
            if Fp2.eq(Fp2.sq(y), rhs):
                return (x, y)
    G1 = G2 = None
    while True:
        R1 = E.mul(rand_point(), cof)
        R2 = E.mul(rand_point(), cof)
        if R1 is None or R2 is None: continue
        U1, U2 = E.mul(R1, 2**(e_a-1)), E.mul(R2, 2**(e_a-1))
        if U1 is None or U2 is None: continue
        if not Fp2.eq(U1[0], U2[0]):
            G1, G2 = R1, R2; break
    Pa, Qa = G1, G2
    assert E.mul(Pa, 2**e_a) is None and E.mul(Qa, 2**e_a) is None
    n = random.randrange(2**e_a)
    R = E.add(Pa, E.mul(Qa, n))
    steps, EA, _ = build_chain(E, R, e_a)
    # phi(Qa) by applying the step maps
    def apply_step(pt, e, t):
        if pt is None: return None
        x, y = pt
        if Fp2.eq(x, e): return None
        ui = Fp2.inv(Fp2.sub(x, e))
        return (Fp2.add(x, Fp2.mul(t, ui)), Fp2.mul(y, Fp2.sub(Fp2.one(), Fp2.mul(t, Fp2.sq(ui)))))
    Qp = Qa
    for (e, t, *_rest) in steps:
        Qp = apply_step(Qp, e, t)
    assert EA.on(Qp)
    n2 = recover_n(Fp2, EA, Pa, Qa, Qp, e_a)
    print(f"e_a={e_a}, e_b={e_b}, p={p}: n={n}, recovered={n2}, match={n==n2}")
    assert n == n2
print("ALL TESTS PASSED")
