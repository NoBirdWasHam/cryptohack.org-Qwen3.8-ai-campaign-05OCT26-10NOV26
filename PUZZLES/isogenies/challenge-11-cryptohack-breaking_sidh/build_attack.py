"""Build the single-file Sage attack script for breaking_sidh from repo sources + instance data."""
import re
base = "~/Practice_runs/cryptohack_org/challenge-223-cryptohack-breaking_sidh/"
src = open(base + "source.sage").read().replace("\r\n", "\n")

def grab(pat):
    m = re.search(pat, src, re.M)
    assert m, pat
    return m.group(1)

# instance literals
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
iv = grab(r"^iv = '([0-9a-f]+)'", )
ct = grab(r"^ct = '([0-9a-f]+)'")

rich = open(base + "cd_repo/richelot_aux.py").read().replace("\r\n", "\n")
uv = open(base + "cd_repo/uvtable.py").read().replace("\r\n", "\n")
uv_rows = re.search(r"uvtable =\s*(\[.*?\])\s*$", uv, re.S).group(1)
import ast
rows = ast.literal_eval(uv_rows)
rows = [r for r in rows if r[0] <= 71]  # keep rows 1..36 (bi up to 71)

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

# expdata[i] = [ai,u,v] for odd i
expdata = {{}}
for ii in range(1, b-3, 2):
    idx = (b - ii) // 2
    row = uvtable[idx-1]
    assert row[0] == 2*idx - 1
    if row[1] <= a:
        expdata[ii] = row[1:4]
print("expdata rows:", len(expdata), "max ai:", max(e[0] for e in expdata.values()), flush=True)

def oracle(i, ai, u, v, skB_try):
    scalar = sum(3^k*d for k,d in enumerate(skB_try))
    tk = 3^(b-i) * (P3 + scalar*Q3)
    C, Pc, Qc, _ = AuxiliaryIsogeny(i, u, v, E0, P2, Q2, tk, two_i)
    alp = a - ai
    return Does22ChainSplit(C, EB, 2^alp*Pc, 2^alp*Qc, 2^alp*PB, 2^alp*QB, ai)

skB = []
errors = 0
for i in range(1, b-2):
    ai, u, v = expdata[i]
    splits = []
    for j in [0,1,2]:
        try:
            if oracle(i, ai, u, v, skB + [j]):
                splits.append(j)
        except Exception as e:
            errors += 1
            print(f"  i={{i}} j={{j}} EXC: {{type(e).__name__}} {{e}}", flush=True)
    if len(splits) != 1:
        print(f"ABORT i={{i}} splits={{splits}} errors={{errors}} skB={{skB}}", flush=True)
        break
    skB.append(splits[0])
    print(f"digit {{i}}: {{splits[0]}}  skB={{skB}}  t={{round(time.time()-TIM0,1)}}", flush=True)

key = sum(skB[k]*3^k for k in range(len(skB)))
print("recovered", len(skB), "digits, errors:", errors, flush=True)

# last 3 digits by j-invariant brute force
sB = None
for t in range(3^3):
    cand = key + t*3^(b-3)
    C, _ = Pushing3Chain(E0, P3 + cand*Q3, b)
    if C.j_invariant() == EB.j_invariant():
        sB = cand
        print("LAST3:", t, "sB found!", flush=True)
        break
if sB is None:
    print("FAILED last-3 brute force", flush=True)
else:
    print("sB =", sB, flush=True)
    print("sB digits:", Integer(sB).digits(3, padto=b), flush=True)
    ch, _ = Pushing3Chain(EA, phiA_P3 + sB*phiA_Q3, b)
    J = ch.j_invariant()
    print("SHARED_J:", J, flush=True)
    print("SHARED_J_STR:", str(J), flush=True)
    Jp = J^p
    print("SHARED_J_CONJ:", Jp, flush=True)
    print("TOTAL:", time.time()-TIM0, flush=True)
'''

script = rich + "\n# --- driver ---\n" + driver
open(base + "attack.sage", "w").write(script)
print("wrote attack.sage", len(script), "chars; uv rows kept:", len(rows))
print("iv:", iv[:16], "ct:", ct[:16])
