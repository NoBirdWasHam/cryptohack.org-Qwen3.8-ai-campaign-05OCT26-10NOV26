"""Chunked CD-attack runner for breaking_sidh over SageCell.

State = recovered ternary digits skB (LSB first). Each SageCell call does a
few digits within the server's ~40s CPU limit. Phase 1 digits [2,1] were
recovered in run1 (guess [2,1] SPLITS with expdata[1] config).
"""
import re, ast, sys, json, time
import sagecell_client as sc

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

SETUP = rich + f'''
# =================== breaking_sidh CD attack (chunked) ===================
import time
TIM0 = time.time()
f, a, b = 45, 117, 73
p = f * 2^a * 3^b - 1
F.<i> = GF(p^2, modulus=x^2+1)
R.<x> = PolynomialRing(F)
E0 = EllipticCurve(F, [1,0]); E0.set_order((p+1)^2, num_checks=0)
P2 = E0({P2x}, {P2y}); Q2 = E0({Q2x}, {Q2y})
P3 = E0({P3x}, {P3y}); Q3 = E0({Q3x}, {Q3y})
def two_i(P):
    if P.is_zero(): return P
    return 2*E0([-P[0], i*P[1]])
assert two_i(two_i(P2)) == -4*P2
EA = EllipticCurve(F, [{EAa}, {EAb}]); EA.set_order((p+1)^2, num_checks=0)
phiA_P3 = EA({fAP3x}, {fAP3y}); phiA_Q3 = EA({fAQ3x}, {fAQ3y})
EB = EllipticCurve(F, [{EBa}, {EBb}]); EB.set_order((p+1)^2, num_checks=0)
PB = EB({fBP2x}, {fBP2y}); QB = EB({fBQ2x}, {fBQ2y})
uvtable = {rows}
expdata = {{}}
for ii in range(1, b-3, 2):
    idx = (b - ii) // 2
    row = uvtable[idx-1]
    if row[1] <= a:
        expdata[ii] = row[1:4]
def get_exp(k):
    return expdata.get(k, [0,0,0])

# deterministic order-3 points on EB (f=45 breaks the random-loop search)
_n3 = (p+1)//3
def _ord3_points(E, skip):
    pts = []
    t = 1
    while len(pts) < 2 + skip:
        try:
            Rp = E.lift_x(F(t))
        except Exception:
            Rp = None
        t += 1
        if Rp is None: continue
        T = _n3*Rp
        if not T.is_zero():
            pts.append(T)
    return pts
_Ks = _ord3_points(EB, 1)
K = _Ks[0]
alternativeK = _Ks[1]
if K.weil_pairing(alternativeK, 3) == 1:
    alternativeK = _Ks[0] + _Ks[1]
_, EBprolong = Pushing3Chain(EB, K, 1)
_, EBprolong_alt = Pushing3Chain(EB, alternativeK, 1)

def digit_oracle(di, ai, u, v, sk_try, eB, ePB, eQB):
    n = len(sk_try)
    bi = b - n
    scalar = sum(3^k*d for k,d in enumerate(sk_try))
    tk = 3^bi * (P3 + scalar*Q3)
    C, Pc, Qc, _ = AuxiliaryIsogeny(n, u, v, E0, P2, Q2, tk, two_i)
    alp = a - ai
    return Does22ChainSplit(C, eB, 2^alp*Pc, 2^alp*Qc, 2^alp*ePB, 2^alp*eQB, ai) is not None

def do_digit(di, skB, chain):
    if get_exp(di)[0]:
        ai, u, v = get_exp(di); prolong = 0
    else:
        ai, u, v = get_exp(di-1); prolong = 1
    js = [0,1,2] if di == 2 else [0,1]
    hits = []
    for j in js:
        try:
            if prolong > 0:
                endPB = chain[0](PB); endQB = chain[0](QB)
                endEB = chain[0].codomain(); endEB.set_order((p+1)^2, num_checks=0)
            else:
                endPB = PB; endQB = QB; endEB = EB
            if digit_oracle(di, ai, u, v, skB+[j], endEB, endPB, endQB):
                hits.append(j)
        except Exception as e:
            print(f"  EXC di={{di}} j={{j}} {{type(e).__name__}}: {{e}}", flush=True)
    if di == 2 and len(hits) != 1:
        return None            # bad prolongation -> caller retries with alt
    return hits[0] if hits else 2
'''

def digits_block(skB, upto, alt=False):
    """recover digits len(skB)..upto-1 (0-based digit indices)"""
    s = f"skB = {skB!r}\n"
    s += f"chain = EBprolong{'_alt' if alt else ''}\n"
    s += f"for di in range({len(skB)}, {upto}):\n"
    s += "    d = do_digit(di, skB, chain)\n"
    s += "    if d is None:\n"
    s += "        chain = EBprolong_alt\n"
    s += "        d = do_digit(di, skB, chain)\n"
    s += "        print('USED_ALT', flush=True)\n"
    s += "    skB.append(d)\n"
    s += "    print('DIGITS', skB, 't=', round(time.time()-TIM0,1), flush=True)\n"
    return s

FINAL = '''
skB = %s
key = sum(skB[k]*3^k for k in range(len(skB)))
sB = None
for t in range(3^3):
    cand = key + t*3^(b-3)
    C, _ = Pushing3Chain(E0, P3 + cand*Q3, b)
    if C.j_invariant() == EB.j_invariant():
        sB = cand
        print("LAST3:", t, flush=True)
        break
if sB is None:
    print("FAILED last-3; skB =", skB, flush=True)
else:
    print("sB =", sB, flush=True)
    ch, _ = Pushing3Chain(EA, phiA_P3 + sB*phiA_Q3, b)
    J = ch.j_invariant()
    print("SHARED_J_STR:", str(J), flush=True)
    print("SHARED_J_CONJ_STR:", str(J^p), flush=True)
'''

STATE = base + "skB_state.json"

def load_state():
    try:
        d = json.load(open(STATE))
        if isinstance(d, dict):
            return d["skB"], d.get("alt", False)
        return d, False
    except Exception:
        return [2, 1], False   # phase 1 result from run1 (verified split)

def save_state(skB, alt):
    json.dump({"skB": skB, "alt": alt}, open(STATE, "w"))

def call(code, timeout=60, tries=4):
    for k in range(tries):
        out, en, ev = sc.run(code, timeout=timeout, verbose=False)
        if en in (None, "client_exc") or "DIGITS" in out or "SHARED" in out:
            return out, en, ev
        print(f"  retry {k+1}: {en} {str(ev)[:80]}", flush=True)
        time.sleep(10)
    return out, en, ev

def main():
    skB, alt = load_state()
    print("start digits:", len(skB), skB, "alt:", alt, flush=True)
    while len(skB) < 70:
        upto = min(len(skB) + 2, 70)
        out, en, ev = call(SETUP + digits_block(skB, upto, alt))
        print(out[-400:], flush=True)
        if "USED_ALT" in out:
            alt = True
        m = re.findall(r"DIGITS (\[[0-9, ]+\])", out)
        if not m:
            print("NO PROGRESS:", en, str(ev)[:200], flush=True)
            time.sleep(20)
            continue
        new = ast.literal_eval(m[-1].replace(" ", ""))
        if len(new) <= len(skB):
            print("STALLED", new, flush=True); time.sleep(15); continue
        skB = new
        save_state(skB, alt)
        print(f"== {len(skB)}/70 digits: {skB}", flush=True)
    out, en, ev = call(SETUP + (FINAL % (skB,)))
    print(out, flush=True)
    open(base + "final_out.txt", "w").write(out)

if __name__ == "__main__":
    main()
