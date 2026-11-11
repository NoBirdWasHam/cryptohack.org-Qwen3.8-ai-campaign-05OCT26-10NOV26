"""Build the single-file Sage attack script for breaking_sidh from repo sources + instance data."""
import re, ast
base = "~/Practice_runs/cryptohack_org/challenge-223-cryptohack-breaking_sidh/"
src = open(base + "source.sage").read().replace("\r\n", "\n")

P2x, P2y = re.search(r"P2 = E0\(([^,]+),\s*([^)]+)\)", src).groups()
Q2x, Q2y = re.search(r"Q2 = E0\(([^,]+),\s*([^)]+)\)", src).groups()
P3x, P3y = re.search(r"P3 = E0\(([^,]+),\s*([^)]+)\)", src).groups()
Q3x, Q3y = re.search(r"Q3 = E0\(([^,]+),\s*([^)]+)\)", src).groups()
EAa, EAb = re.search(r"EAa = (\d+\*i\+\d+)\nEAb = (\d+\*i\+\d+)", src).groups()
EBa, EBb = re.search(r"EBa = (\d+\*i\+\d+)\nEBb = (\d+\*i\+\d+)", src).groups()
fAP3x, fAP3y = re.search(r"phiA_P3 = EA\(([^,]+),\s*([^)]+)\)", src).groups()
fAQ3x, fAQ3y = re.search(r"phiA_Q3 = EA\(([^,]+),\s*([^)]+)\)", src).groups()
fBP2x, fBP2y = re.search(r"phiB_P2 = EB\(([^,]+),\s*([^)]+)\)", src).groups()
fBQ2x, fBQ2y = re.search(r"phiB_Q2 = EB\(([^,]+),\s*([^)]+)\)", src).groups()

rich = open(base + "cd_repo/richelot_aux.py").read().replace("\r\n", "\n")
uv = open(base + "cd_repo/uvtable.py").read().replace("\r\n", "\n")
rows = ast.literal_eval(re.search(r"uvtable =\s*(\[.*?\])\s*$", uv, re.S).group(1))
rows = [r for r in rows if r[0] <= 71]

driver = f'''
# =================== breaking_sidh CD attack ===================
import time
TIM0 = time.time()
f, a, b = 45, 117, 73
p = f * 2^a * 3^b - 1
F.<i> = GF(p^2, modulus=x^2+1)
R.<x> = PolynomialRing(F)

E0 = EllipticCurve(F, [1,0]); E0.set_order((p+1)^2, num_checks=0)
P2 = E0({P2x}, {P2y}); Q2 = E0({Q2x}, {Q2y})
P3 = E0({P3x}, {P3y}); Q3 = E0({Q3x}, {Q3y})
assert 2^(a-1)*P2 != E0(0) and 3^(b-1)*P3 != E0(0)
assert P2.weil_pairing(Q2, 2^a)^(2^(a-1)) != 1
assert P3.weil_pairing(Q3, 3^b)^(3^(b-1)) != 1
print("torsion basis OK", time.time()-TIM0, flush=True)

def two_i(P):
    if P.is_zero(): return P
    return 2*E0([-P[0], i*P[1]])
G = E0.random_point()
assert two_i(two_i(G)) == -4*G
assert two_i(G + two_i(G)) == two_i(G) + two_i(two_i(G))

EA = EllipticCurve(F, [{EAa}, {EAb}]); EA.set_order((p+1)^2, num_checks=0)
phiA_P3 = EA({fAP3x}, {fAP3y}); phiA_Q3 = EA({fAQ3x}, {fAQ3y})
EB = EllipticCurve(F, [{EBa}, {EBb}]); EB.set_order((p+1)^2, num_checks=0)
PB = EB({fBP2x}, {fBP2y}); QB = EB({fBQ2x}, {fBQ2y})
assert 2^(a-1)*PB != EB(0) and 2^(a-1)*QB != EB(0)
print("public keys OK", time.time()-TIM0, flush=True)

uvtable = {rows}
expdata = {{}}
for ii in range(1, b-3, 2):
    idx = (b - ii) // 2
    row = uvtable[idx-1]
    assert row[0] == 2*idx - 1
    if row[1] <= a:
        expdata[ii] = row[1:4]
print("expdata rows:", len(expdata), "max ai:", max(e[0] for e in expdata.values()), flush=True)

skB = []
errors = 0
def get_exp(k):
    return expdata.get(k, [0,0,0])

# ---- Phase 1: first bet1 digits (guessing) ----
bet1 = 1
while not get_exp(bet1)[0]:
    bet1 += 1
ai, u, v = get_exp(bet1)
bet1 += 1
print(f"Phase 1: first {{bet1}} digits, ai={{ai}}", flush=True)
bi = b - bet1
found = None
for g in range(3^bet1 - 1):
    digs = ZZ(g).digits(3, padto=bet1)
    try:
        scalar = sum(3^k*d for k,d in enumerate(digs))
        tk = 3^bi * (P3 + scalar*Q3)
        C, Pc, Qc, _ = AuxiliaryIsogeny(bet1, u, v, E0, P2, Q2, tk, two_i)
        alp = a - ai
        if Does22ChainSplit(C, EB, 2^alp*Pc, 2^alp*Qc, 2^alp*PB, 2^alp*QB, ai) is not None:
            found = digs
            print(f"  guess {{digs}} SPLITS", flush=True)
            break
    except Exception as e:
        errors += 1
        print(f"  guess {{digs}} EXC {{type(e).__name__}}: {{e}}", flush=True)
if found is None:
    found = [2]*bet1
    print("  all guesses failed -> digits all 2", flush=True)
skB += found
print("skB:", skB, "t=", round(time.time()-TIM0,1), flush=True)

# ---- prolongation data ----
length = 1; max_length = 0
for i in range(bet1+1, b-3):
    if get_exp(i)[0]:
        max_length = max(length, max_length); length = 0
    else:
        length += 1
print("max_length:", max_length, flush=True)
while True:
    K = 2^a * 3^(b-max_length) * EB.random_point()
    if K.order() == 3^max_length: break
while True:
    alternativeK = 2^a * 3^(b-max_length) * EB.random_point()
    if K.weil_pairing(alternativeK, 3^max_length)^(3^(max_length-1)) != 1: break
_, EBprolong = Pushing3Chain(EB, K, max_length)

def digit_oracle(i, ai, u, v, sk_try, eB, ePB, eQB):
    bi = b - i
    scalar = sum(3^k*d for k,d in enumerate(sk_try))
    tk = 3^bi * (P3 + scalar*Q3)
    C, Pc, Qc, _ = AuxiliaryIsogeny(i, u, v, E0, P2, Q2, tk, two_i)
    alp = a - ai
    return Does22ChainSplit(C, eB, 2^alp*Pc, 2^alp*Qc, 2^alp*ePB, 2^alp*eQB, ai) is not None

# ---- digit bet1+1 with prolong=1 ----
i = bet1 + 1
endPB = EBprolong[0](PB); endQB = EBprolong[0](QB)
endEB = EBprolong[0].codomain(); endEB.set_order((p+1)^2, num_checks=0)
positives = []
for j in [0,1,2]:
    try:
        if digit_oracle(i, ai, u, v, skB+[j], endEB, endPB, endQB):
            positives.append(j)
            if len(positives) > 1: break
    except Exception as e:
        errors += 1
        print(f"  d{{i}} j={{j}} EXC {{type(e).__name__}}: {{e}}", flush=True)
if len(positives) == 1:
    skB.append(positives[0])
    next_i = i + 1
    prolong = 1
else:
    print("  all splits -> bad prolongation, switching K", flush=True)
    _, EBprolong = Pushing3Chain(EB, alternativeK, max_length)
    next_i = i
    prolong = 0
print(f"digit {{i}} done: skB={{skB}} t={{round(time.time()-TIM0,1)}}", flush=True)

# ---- remaining digits ----
for i in range(next_i, b-2):
    if get_exp(i-1)[0]:
        ai, u, v = get_exp(i-1)
        alp = a - ai
        prolong = 0
    else:
        prolong += 1
    endPB = PB; endQB = QB; endEB = EB
    for jj in range(1, prolong+1):
        endPB = EBprolong[jj-1](endPB); endQB = EBprolong[jj-1](endQB)
    if prolong > 0:
        endEB = EBprolong[prolong-1].codomain()
        endEB.set_order((p+1)^2, num_checks=0)
    hit = None
    for j in [0,1]:
        try:
            if digit_oracle(i, ai, u, v, skB+[j], endEB, endPB, endQB):
                hit = j; break
        except Exception as e:
            errors += 1
            print(f"  d{{i}} j={{j}} EXC {{type(e).__name__}}: {{e}}", flush=True)
    skB.append(2 if hit is None else hit)
    print(f"digit {{i}}: {{skB[-1]}}  n={{len(skB)}}  err={{errors}}  t={{round(time.time()-TIM0,1)}}", flush=True)

key = sum(skB[k]*3^k for k in range(len(skB)))
print("recovered", len(skB), "digits, errors:", errors, flush=True)

sB = None
for t in range(3^3):
    cand = key + t*3^(b-3)
    C, _ = Pushing3Chain(E0, P3 + cand*Q3, b)
    if C.j_invariant() == EB.j_invariant():
        sB = cand
        print("LAST3:", t, "sB found!", flush=True)
        break
if sB is None:
    print("FAILED last-3 brute force; skB =", skB, flush=True)
else:
    print("sB =", sB, flush=True)
    ch, _ = Pushing3Chain(EA, phiA_P3 + sB*phiA_Q3, b)
    J = ch.j_invariant()
    print("SHARED_J_STR:", str(J), flush=True)
    print("SHARED_J_CONJ_STR:", str(J^p), flush=True)
    print("TOTAL:", time.time()-TIM0, flush=True)
'''

script = rich + "\n# --- driver ---\n" + driver
open(base + "attack.sage", "w").write(script)
print("wrote attack.sage", len(script), "chars; uv rows kept:", len(rows))
