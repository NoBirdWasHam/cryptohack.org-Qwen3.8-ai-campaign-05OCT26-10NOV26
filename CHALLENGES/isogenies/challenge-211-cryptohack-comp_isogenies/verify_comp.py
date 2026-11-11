#!/usr/bin/env python
"""Independent verifications for the comp_isogenies chain (comp_iso.py)."""
import random
from comp_iso import *
from comp_iso import _n

K = (f2(53943911829, 357834818388), f2(267017462655, 46334220304)
)
a, b = ONE, ZERO

def build_chain(K, verbose=False):
    """Run the 13-step chain from K. Returns (js, final_ab, final_a1_b1_of_step1,
    list_of_phis, K13)."""
    a, b = ONE, ZERO
    assert ec_on_curve(K, a, b)
    assert ec_mul(3**13, K, a, b) is None
    Kur = K
    Q = ec_mul(3**12, K, a, b)
    js = [j_invariant(a, b)]
    phis = []
    step1_ab = None
    for k in range(13):
        assert ec_mul(3, Q, a, b) is None and Q is not None
        a, b, phi = velu3(a, b, Q)
        phis.append(phi)
        if k == 0:
            step1_ab = (a, b)
        if k < 12:
            Kur = phi(Kur)
            Q = ec_mul(3**(11-k), Kur, a, b)
            assert ec_mul(3, Q, a, b) is None and Q is not None
        js.append(j_invariant(a, b))
    K13 = phis[-1](Kur)  # phi_12(K_12) must be O (K_12 == Q_12 in kernel)
    return js, (a, b), step1_ab, phis, K13

print("=== V1: chain with K ===")
js, (a13, b13), step1_ab, phis, K13 = build_chain(K)
print("K13 (total map on K) =", K13, "  expect None (O)")
assert K13 is None
print("E_1 codomain a4 =", f2_repr(step1_ab[0]), " a6 =", f2_repr(step1_ab[1]))
print("three_iso codomain: a4 = 417919813652, a6 = 36118389888 (or twist a6 = -36118389888 mod p)")
twist_a6 = (-36118389888) % p
print("  match three_iso:", step1_ab[0][0] == 417919813652 and step1_ab[1][0] == 36118389888)
print("  match twist:    ", step1_ab[0][0] == 417919813652 and step1_ab[1][0] == twist_a6)
j13 = js[-1]
print("j(E_13) =", f2_repr(j13))

print("\n=== V2: conjugate chain (Frobenius symmetry) ===")
Kbar = (f2(K[0][0], -K[0][1]), f2(K[1][0], -K[1][1]))
js2, (a13b, b13b), step1_ab2, phis2, K13b = build_chain(Kbar)
j13b = js2[-1]
print("j(E_13) with Kbar =", f2_repr(j13b))
conj = f2(j13[0], -j13[1])
print("conjugate of j13  =", f2_repr(conj))
assert f2_eq(j13b, conj), "Frobenius symmetry FAILED"
print("Frobenius symmetry OK (j13(Kbar) == conj(j13(K)))")

print("\n=== V3: total map is a homomorphism and lands on E_13 ===")
random.seed(1234)
def rand_point():
    while True:
        x = f2(random.randrange(p), random.randrange(p))
        rhs = f2_add(f2_add(f2_mul(f2_mul(x, x), x), f2_mul(ONE, x)), ZERO)
        y = f2_sqrt(rhs)
        if y is not None:
            return (x, y)

P = rand_point()
R = rand_point()
print("P on E0:", ec_on_curve(P, ONE, ZERO), " R on E0:", ec_on_curve(R, ONE, ZERO))
def total(P):
    for phi in phis:
        P = phi(P)
    return P
tP = total(P); tR = total(R); tPR = total(ec_add(P, R, ONE, ZERO))
print("total(P) on E13:", ec_on_curve(tP, a13, b13))
print("total(R) on E13:", ec_on_curve(tR, a13, b13))
print("total(P+R) on E13:", ec_on_curve(tPR, a13, b13))
lhs = ec_add(tP, tR, a13, b13)
ok = (tPR is None and lhs is None) or (tPR is not None and lhs is not None and f2_eq(tPR[0], lhs[0]) and f2_eq(tPR[1], lhs[1]))
print("homomorphism: total(P+R) == total(P)+total(R):", ok)
assert ok
print("\nALL VERIFICATIONS PASSED")
print("\nFLAG candidates for j(E_13) =", f2_repr(j13), ":")
print("  1:", f"{j13[0]}+{j13[1]}i")
print("  2:", f"{j13[0]} {j13[1]}")
print("  3:", f"{j13[0]},{j13[1]}")
