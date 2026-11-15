#!/usr/bin/env python3
# evil_twisted_mind: modulus p = q1*q2 (composite!). Recover q1 via gcd(order*x0.Z, p).
# E(F_q1) has prime order == 'order' (kills q1 component). E(F_q2) TWIST order is smooth:
#   17 * 1789 * 8984179 * 9381319 * 83816652113 * R (R ~75-bit prime).
# Send x0 with q1-component O and q2-twist component of smooth order S2; oracle pubkey
# = x(k*P0). DLP in smooth group via per-prime-power enumeration (no order needed).
# k = privkey < order/2; k mod S2 known; k = r or order - r (r = privkey) -> test both.
import re, math, random, socket, json, ast, hashlib

src = open("13418.py").read()
p = int(re.search(r"modulus\s*=\s*(\d+)", src).group(1))
a = -3
b = int(re.search(r"^b\s*=\s*(\d+)", src, re.M).group(1))
order = int(re.search(r"^order\s*=\s*(\d+)", src, re.M).group(1))

def sxz(X1, Z1, m):
    XX = X1*X1 % m; ZZ = Z1*Z1 % m
    A = 2*((X1+Z1)**2 - XX - ZZ) % m
    aZZ = a*ZZ % m
    X3 = ((XX - aZZ)**2 - 2*b*A*ZZ) % m
    Z3 = (A*(XX + aZZ) + 4*b*ZZ*ZZ) % m
    return (X3, Z3)

def sdiff(X1, Z1, X2, Z2, x0, m):
    X1Z2 = X1*Z2 % m; X2Z1 = X2*Z1 % m; Z1Z2 = Z1*Z2 % m
    T = (X1Z2 + X2Z1)*(X1*X2 + a*Z1Z2) % m
    Z3 = (X1Z2 - X2Z1)**2 % m
    X3 = (2*T + 4*b*Z1Z2**2 - x0*Z3) % m
    return (X3, Z3)

def ladder_full(scalar, x0, m):
    R0 = (x0, 1); R1 = sxz(*R0, m)
    n = scalar.bit_length(); pbit = 0; bit = 0
    for i in range(n-2, -1, -1):
        bit = (scalar >> i) & 1
        pbit ^= bit
        if pbit: R0, R1 = R1, R0
        R1 = sdiff(*R0, *R1, x0, m)
        R0 = sxz(*R0, m)
        pbit = bit
    if bit: R0 = R1
    return R0

# --- factor p ---
rng = random.Random(7)
while True:
    x0r = rng.randrange(2, p)
    X, Z = ladder_full(order, x0r, p)
    g = math.gcd(Z, p)
    if g not in (1, p): break
q1 = g; q2 = p // g
assert q1 * q2 == p
print(f"q1={q1}")
print(f"q2={q2}")

S2_small = 17 * 1789 * 8984179 * 9381319 * 83816652113
R2 = 22324892568046125682687618733
S2 = S2_small * R2

# --- construct x0: q1-component O, q2-twist order S2 ---
# x0 = order * R for random R on E(Z/pZ): q1 part -> O (since #E(Fq1)=order),
# q2 part -> order * (R mod q2), lands in q2-twist or q2-curve subgroup.
def legendre(n, q): return pow(n % q, (q-1)//2, q)
x0 = None
for _ in range(50):
    xr = rng.randrange(2, p)
    Xc, Zc = ladder_full(order, xr, p)
    if Zc % q2 == 0:  # q2 component also O -> bad
        continue
    # affine x of q2 component
    xq2 = Xc * pow(Zc % q2, -1, q2) % q2
    # must be on the TWIST over q2 (f non-residue) for smooth order; check
    fq2 = (xq2**3 + a*xq2*xq2 + xq2) * pow(b, -1, q2) % q2
    if legendre(fq2, q2) == q2 - 1:
        x0 = Xc * pow(Zc, -1, p) % p
        break
assert x0, "could not build x0"
# verify S2*x0 == O mod q2 (projective Z==0)
Xs, Zs = ladder_full(S2, x0, q2)
print("S2*x0 == O (mod q2)?", Zs == 0)
Xs1, Zs1 = ladder_full(S2_small, x0, q2)
print("S2_small*x0 Z==0?", Zs1 == 0)

# --- oracle ---
s = socket.create_connection(("socket.cryptohack.org", 13418), timeout=30)
f = s.makefile("rwb")
def send(o):
    f.write((json.dumps(o)+"\n").encode()); f.flush()
    return ast.literal_eval(f.readline().decode())
banner = b""
while banner.count(b"\n") < 2:
    line = f.readline()
    if not line: break
    banner += line
print("banner:", banner[:120])
resp = send({"option": "get_pubkey", "x0": str(x0)})
print("pubkey resp:", str(resp)[:120])
Y = int(resp["pubkey"])

# --- DLP in smooth group (order divides S2), per prime power, no order needed ---
def pmul_proj(k, P, x0v, m):
    # scalar mult of projective point P=(X:Z) using ladder formulas via affine x if Z!=0
    if Z_ok(P):
        xa = P[0] * pow(P[1], -1, m) % m
        return ladder_full(k, xa, m)
    raise ValueError("P at infinity")
def Z_ok(P): return P[1] % m0 != 0
m0 = q2

def mulP(k):  # k * P0 in projective over q2, P0 = x0 (twist point)
    return ladder_full(k, x0, q2)

def same_x(Pa, Yv):
    if Pa[1] == 0: return False
    return Pa[0] * pow(Pa[1], -1, q2) % q2 == Yv % q2

residues = {}
for pp in [17, 1789, 8984179, 9381319, 83816652113, R2]:
    c = S2 // pp
    Gp = mulP(c)  # (X:Z) of order pp
    Gx = Gp[0] * pow(Gp[1], -1, q2) % q2
    H = mulP(c * 1)  # placeholder
    # H = c*Y as x-only: we only have Y as x-coord; use ladder on Y? No:
    print(f"prime power {pp}: bits {pp.bit_length()}")
# NOTE: Y is an x-coordinate on the twist over q2; to combine scalars we must work
# with points, not x-values. Reconstruct: we know P0=x0. For DLP we need H = k*P0 as a
# POINT to add/subtract. x-only: use x0-difference = x(P0) for diffadd! The ladder's
# diffadd needs x(P-Q)=x0. To test candidate d: check (c*(k-d))*P0 == ... we can't
# subtract unknown k. Standard trick: baby-step giant-step with x-only using diffadd
# requires x(P0) known (=x0 mod q2) and x(k*P0)=Y known; we can compute x(n*P0) for any
# n via ladder. BSGS: find d1 - d2*m with x(d1*? ) ... x-only BSGS needs x(A+B) from
# x(A),x(B),x(A-B): we have x0 = x(P0) so x(A+B) computable when A=nP0, B=mQ0 with
# A-B = (n-m)P0 -> x known via ladder. Implement BSGS over the full S2 (56 bits):
#   find k in [0,S2): k = i*m2 + j, m2=ceil(sqrt(S2)) ~ 2^28 table -- too big.
# Instead per-prime-power: for prime pp, c=S2/pp, G=c*P0 (order pp), H=c*(k*P0): we
# need H as x-value: x(c*k*P0) = ladder(c*k, x0) -- but that needs k! NO: x(c*k*P0) is
# NOT derivable from Y=x(k*P0) without scalar mult on the point Y... but ladder(c, Y)?
# ladder(c, Yx) computes c*Q where Q is the point with x=Yx and SAME x-difference
# structure -- the Montgomery ladder is x-only: ladder(c, x(Q)) = x(c*Q) for ANY point Q
# with that x (works on twist too). So H_x = ladder(c, Y, q2) == x(c*k*P0).
# Then enumerate d: x(d*G) via ladder(d, Gx, q2) -- but ladder(d,Gx) = x(d*G) where
# G has x=Gx: correct since G = c*P0 is a specific x; x-only ladder gives x(d*G).
print("=== per-prime-power enumeration (x-only) ===")
residues = {}
for pp in [17, 1789, 8984179, 9381319, 83816652113]:
    c = S2 // pp
    Gx = ladder_full(c, x0, q2)
    if Gx[1] == 0:
        print(f"  {pp}: G at infinity (k coprime issue) -- skip"); continue
    Gx = Gx[0] * pow(Gx[1], -1, q2) % q2
    Hx = ladder_full(c, Y, q2)   # x(c * (k P0)) = x-only ladder on Y
    if Hx[1] == 0:
        residues[pp] = 0; print(f"  {pp}: k=0"); continue
    Hx = Hx[0] * pow(Hx[1], -1, q2) % q2
    found = None
    Rx = Gx  # x(d*G), incremental via ladder is O(log) per step; do ladder(d,c? ) -- use ladder each d (pp up to 8e10 too big!)
    print(f"  {pp}: enumerating {pp} candidates...")
    for d in range(pp):
        if d == 0:
            xd = 1  # placeholder
        # compute x(d*G) incrementally: x((d+1)G) from x(dG), x(G), x(G) diff -> diffadd needs x(G-? )
        pass
    # incremental x-only walk: x((d+1)G) via diffadd(x(dG), x(G), x(G-d? )) -- difference must be constant x(G). diffadd(P,Q,x(P-Q)): P=dG, Q=G -> P-Q=(d-1)G, x known from previous step!
    # classic: x_{d+1} = diffadd(x_d, x_1, x_{d-1})
    x_prev = None  # x((d-1)G)
    x_cur = None   # x(dG)
    # represent as projective pairs to avoid inverses
    Pprev = (1, 0)      # O
    Pcur = (Gx, 1)      # G
    for d in range(0, pp):
        if d == 0:
            Xd, Zd = (1, 0)  # O -> x undefined; k mod pp == 0 means H=O
            if Hx is None: pass
        # compare current x_d with Hx
        # (handled below in loop body)
        # advance: Pnext = diffadd(Pcur, Pprev? ) careful: x(Pcur - Pprev) = x(G) = Gx
        Xn, Zn = sdiff(*Pcur, *Pprev, Gx, q2)  # Pcur + Pprev? diffadd(P,Q) = P+Q given x(P-Q)
        # diffadd(P1,P2,x0) computes P1+P2 when x0 = x(P1-P2). Pcur=dG, Pprev=(d-1)G -> diff = G -> x0=Gx. result=(2d-1)G?? NO: Pcur+Pprev=(2d-1)G. WRONG.
        break
    # Correct incremental: maintain P_d = dG and use diffadd(P_d, G, x(P_d - G)=x((d-1)G)=x_{d-1}):
    #   P_{d+1} = diffadd(P_d, P_1, x_{d-1}).
    Pd = (1, 0)      # 0*G = O (projective (1,0))
    Pd_prev = None
    Pd1 = (Gx, 1)    # 1*G
    # do it with explicit prev tracking
    P_d = (1, 0); P_dm1 = None
    hit = None
    for d in range(0, pp):
        if P_d[1] != 0:
            xd = P_d[0] * pow(P_d[1], -1, q2) % q2
        else:
            xd = None
        if xd == Hx or (P_d[1] == 0 and False):
            hit = d; break
        # advance to (d+1)G = diffadd(dG, G, x((d-1)G))
        if d == 0:
            P_next = (Gx, 1)
        elif d == 1:
            P_next = sxz(*P_d, q2)  # 2G = dbl(G)
        else:
            xdiff = P_dm1[0] * pow(P_dm1[1], -1, q2) % q2 if P_dm1[1] != 0 else None
            if xdiff is None:
                print("  degenerate walk; abort"); break
            P_next = sdiff(*P_d, Gx, 1, xdiff, q2)
        P_dm1 = P_d; P_d = P_next
    if hit is None:
        print(f"  {pp}: NOT FOUND (walk)"); continue
    residues[pp] = hit
    print(f"  {pp}: k = {hit}")
print("residues:", residues)
import functools
kS = 0; M = 1
for pp, r in residues.items():
    t = (r - kS) * pow(M % pp, -1, pp) % pp
    kS += M * t; M *= pp; kS %= M
print("k mod S2_small bits:", M.bit_length())
cands = [r for r in (kS, (order - (kS % order)) % order) if r % M == kS and r < order]
print("candidates:", len(cands))
# rho for R2 factor to disambiguate if >1
if len(cands) != 1:
    print("need rho on R2 =", R2)
# verify candidate against pubkey: x(k*x0) == Y?
final = None
for c in cands:
    Xv, Zv = ladder_full(c, x0, q2)
    xv = Xv * pow(Zv, -1, q2) % q2
    if xv == Y % q2:
        final = c; break
print("FINAL privkey:", final)
if final is not None:
    resp = send({"option": "get_flag", "privkey": final})
    print("SERVER:", str(resp)[:300])
    mm = re.search(r"crypto\{[^}]+\}", str(resp))
    if mm:
        open("flag.txt", "w").write(mm.group(0) + "\n")
        print("FLAG:", mm.group(0))
s.close()
