import sys, time
sys.path.insert(0, ".")
from fp2 import *

# --- sanity: velu_odd homomorphism + codomain on tiny curve p=1019 (3 mod 4) ---
def tiny_test():
    import fp2
    p0 = fp2.p
    fp2.p = 1019
    p = 1019
    a, b = (1, 0), (0, 0)
    # find order-3 point: #E = 1020
    R = None; Q0 = None
    for x in range(2, 200):
        rhs = (x*x*x + x) % p
        y = pow(rhs, (p+1)//4, p)
        if (y*y) % p != rhs or not y: continue
        cand = emul(((x, 0), (y, 0)), 340, a)
        if cand is not None and emul(cand, 3, a) is None:
            Q0 = cand; break
    assert Q0 is not None
    (A, B), mp = velu_odd((a, b), Q0)
    # homomorphism test
    for _ in range(5):
        x = (hash(str(_)) % 1000, 0)
        rhs = (x[0]**3 + x[0]) % p
        y = pow(rhs, (p+1)//4, p)
        if (y*y) % p != rhs or y == 0: continue
        P = (x, (y, 0))
        xr = ((7 + _*13) % p, 0)
        rr = (xr[0]**3 + xr[0]) % p
        yr = pow(rr, (p+1)//4, p)
        if (yr*yr) % p != rr or yr == 0: continue
        Rr = (xr, (yr, 0))
        lhs = mp(eadd(P, Rr, a)); rhs2 = eadd(mp(P), mp(Rr), A)
        assert lhs == rhs2, ("hom fail", lhs, rhs2)
        assert is_on_curve(mp(P), A, B)
    p = p0
    fp2.p = p0
    print("tiny velu_odd OK")
tiny_test()

# --- main data ---
E0 = ((1, 0), (0, 0))
P2 = ((1761758151759977040301838, 1956194174015565770794336), (203179590296749797202321, 2069089015584979134622338))
Q2 = ((525239361975369850140518, 2307879706216488835068177), (733730165545948547648966, 1834477572646982833868802))
P3 = ((1542032609308508307064948, 2162781291023757368295120), (904285233345649302734471, 1130418491160933565948899))
Q3 = ((1867216057142335172490873, 365294178628988623980343), (1860108401614981479394873, 2141125983272329025279178))
EA = ((63223462935813026254900, 2336060373130772918448023), (525917254309082638166498, 202739861418983960259548))
sB = 495832856

for nm, Pt in [("P2", P2), ("Q2", Q2), ("P3", P3), ("Q3", Q3)]:
    print(nm, "on E0:", is_on_curve(Pt, *E0))
print("j(E0) =", fstr(jinv(*E0)))
print("j(EA) =", fstr(jinv(*EA)))
print("2^35 P2 = O?", emul(P2, 2**35, (1, 0)) is None, " 2^34 P2 = O?", emul(P2, 2**34, (1, 0)) is None)
print("3^29 P3 = O?", emul(P3, 3**29, (1, 0)) is None, " 3^28 P3 = O?", emul(P3, 3**28, (1, 0)) is None)
print("sB base3 digits:", [int(c) for c in np_base3] if False else "")
# base-3 of sB
n = sB; d3 = []
while n: d3.append(n % 3); n //= 3
print("sB base3 (low first):", d3)
print("sB mod small:", sB % 9, sB % 27)
