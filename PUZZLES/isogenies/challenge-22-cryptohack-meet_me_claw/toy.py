import sys, random
sys.path.insert(0, ".")
import fp2
from fp2 import *
import solve
from solve import fsqrt, roots3

p = 62207  # 2^8*3^5-1, prime, 3 mod 4
fp2.p = p
solve.p = p
solve.EA_ = 8; solve.F = 5; solve.B = 3
E0 = ((1,0),(0,0))
rnd = random.Random(7)
def rp():
    while True:
        x = (rnd.randrange(p), rnd.randrange(p))
        z = fadd(fmul(x, fmul(x,x)), x)
        if fpow(z, (p*p-1)//2) != (1,0): continue
        y = fsqrt(z)
        if feq(fsq(y), z) and y != (0,0):
            return (x, y)
def basis2():
    while True:
        T1, T2 = rp(), rp()
        P = emul(T1, 3**5, (1,0)); Q = emul(T2, 3**5, (1,0))
        if P is None or Q is None: continue
        if emul(P, 2**7, (1,0)) is None or emul(Q, 2**7, (1,0)) is None: continue
        if emul(P, 2**7, (1,0)) == emul(Q, 2**7, (1,0)): continue
        return P, Q
def basis3():
    while True:
        T1, T2 = rp(), rp()
        P = emul(T1, 2**8, (1,0)); Q = emul(T2, 2**8, (1,0))
        if P is None or Q is None: continue
        if emul(P, 3**4, (1,0)) is None or emul(Q, 3**4, (1,0)) is None: continue
        if emul(P, 3**4, (1,0)) == emul(Q, 3**4, (1,0)): continue
        return P, Q
P2, Q2 = basis2(); P3, Q3 = basis3()
solve.P2, solve.Q2, solve.P3, solve.Q3 = P2, Q2, P3, Q3
a = rnd.randrange(2**8); sB = rnd.randrange(3**5)
print("toy secret a =", a, "sB =", sB)
EA, _ = solve.walk2_full(a, [], ea=8)
solve.EA = EA; solve.jEA = jinv(*EA)
print("j(EA) =", fstr(solve.jEA))

tbl = solve.forward_table()
ms = solve.backward(tbl)
print("matches:", len(ms))
cand = None
for (Em, los) in ms:
    for lo in los:
        for hi in range(2**(8-5)):
            aa = lo | (hi << 5)
            E35, _ = solve.walk2_full(aa, [], ea=8)
            if feq(jinv(*E35), solve.jEA):
                cand = aa
    if cand: break
print("recovered a:", cand, "true:", a, "OK" if cand == a else "MISMATCH")

# shared secret via Alice side
pA3, qA3 = solve.walk2_full(a, [P3, Q3], ea=8)[1]
H = eadd(pA3, emul(qA3, sB, EA[0]), EA[0])
EAB = solve.chain3(EA, H, eb=5)
jA = jinv(*EAB)
# ground truth via Bob side
def chain3_track(E, H, pts, eb=5):
    for k in range(eb):
        Q0 = emul(H, 3**(eb-1-k), E[0])
        E, mp = velu_odd(E, Q0)
        H = mp(H); pts = [mp(x) for x in pts]
    return E, H, pts
EB, _, (bP2, bQ2) = chain3_track(E0, eadd(P3, emul(Q3, sB, (1,0)), (1,0)), [P2, Q2])
def walk2_from(E, p2, q2, a, ea=8):
    pts = [p2, q2]
    for i in range(ea):
        u = emul(eadd(p2, emul(q2, a, E[0]), E[0]), 2**(ea-1-i), E[0])
        E2, xm, ym = velu2(E, u)
        mp = lambda Pt: None if Pt is None else (xm(Pt[0]), ym(Pt[0], Pt[1]))
        p2, q2 = mp(p2), mp(q2); E = E2
    return E
EAB2 = walk2_from(EB, bP2, bQ2, a)
jB = jinv(*EAB2)
print("j shared Alice:", fstr(jA))
print("j shared Bob  :", fstr(jB))
print("MATCH" if feq(jA, jB) else "FAIL")
