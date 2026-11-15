#!/usr/bin/env python
"""five_iso_csidh_twist: one BACKWARD step on the 3-isogeny graph from
E_0: y^2 = x^3 + x mod 419.  Flag = Montgomery coefficient A of the result
in the form y^2 = x^3 + A x^2 + x.

Method A (forward cross-check, per the statement's own test):
  k=3 cycle  =>  backward 1 step from E_0 == forward 2 steps from E_0.
Method B (the twist algorithm of the statement):
  E^t = quadratic twist of E_0 (d=2, nonsquare): y^2 = x^3 + 4x
  find P of order 3 on E^t; 3-isogeny E^t -> F (Vélu); untwist F with d=2
  -> G = y^2 = x^3 + d^2 a_F x + d^3 b_F.  G should be the same curve.
Both must give the same Montgomery A (principal-sqrt convention, the
challenge convention verified on special_isogenies (199) and
csidh_secret_exponents (404)).
"""
from velu_engine import (make_ec, find_order_l_points, velu_xmap,
                         reconstruct_codomain, j_short, csidh_walk,
                         montgomery_candidates, montgomery_verify, sqrt_p)

p = 419
d = 2  # nonsquare mod 419 ((2/419) = -1, 419 % 8 == 3)
assert pow(d, (p-1)//2, p) == p-1, "d must be nonsquare"

def montgomery_A(E):
    """Principal-root-convention Montgomery A of short-Weierstrass E, verified."""
    a = E["a"]
    roots = [x for x in range(p) if (x*x*x + a*E["b"] + 0) % p == 0]
    roots = [x for x in range(p) if (x*x*x + a*x + E["b"]) % p == 0]
    Aset = set()
    for v in roots:
        c2 = (3*v*v + a) % p
        w = sqrt_p(c2, p)
        if w is None:
            continue
        A = (3*v) * pow(w, -1, p) % p
        got, cnt = montgomery_verify(E, A)
        if got is not None:
            Aset.add(A)
    assert len(Aset) == 1, f"ambiguous Montgomery A: {Aset}"
    return Aset.pop()

print("=== Method A: forward 3-walk, 2 steps (k-1 forward == 1 backward on 3-cycle) ===")
h = []
E2 = csidh_walk(p, 1, 0, [3, 3], verbose=True, history=h)
a2, b2 = E2["a"], E2["b"]
j2 = j_short(a2, b2, p)
print(f"forward endpoint E2: y^2 = x^3 + {a2} x + {b2}   j = {j2}   #E2 = {E2['count']()}")
A_f = montgomery_A(E2)
print(f"Method A: Montgomery A = {A_f}")

print()
print("=== Method B: twist backward step ===")
Et = make_ec(p, d*d*1 % p, 0)  # twist of y^2 = x^3 + x: a' = d^2 a, b' = d^3 b = 0
print(f"E^t: y^2 = x^3 + {Et['a']} x   #E^t = {Et['count']()}")
pts3 = find_order_l_points(Et, 3)
P = pts3[0]
print(f"order-3 point on E^t: {P}  (3P = O: {Et['mul'](P, 3) is None})")
K = [Et["mul"](P, k) for k in range(1, 3)]
xmap = velu_xmap(Et, K)
AF, BF = reconstruct_codomain(Et, K, xmap, 3)
print(f"3-isogeny E^t -> F: y^2 = x^3 + {AF} x + {BF}   j(F) = {j_short(AF, BF, p)}")
aG, bG = (d*d*AF) % p, (d*d*d*BF) % p  # untwist F: twist again with d
EG = make_ec(p, aG, bG)
jG = j_short(aG, bG, p)
print(f"untwist -> G: y^2 = x^3 + {aG} x + {bG}   j(G) = {jG}   #G = {EG['count']()}")
assert jG == j2, "BACKWARD curve G must have same j as forward endpoint E2"
assert EG["count"]() == E2["count"](), "point counts must match"
A_b = montgomery_A(EG)
print(f"Method B: Montgomery A = {A_b}")

print()
assert A_f == A_b, f"MISMATCH: forward A={A_f} vs twist A={A_b}"
print(f"BOTH METHODS AGREE: FLAG = {A_f}")
