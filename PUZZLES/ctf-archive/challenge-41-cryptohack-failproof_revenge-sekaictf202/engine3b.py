# RUN#3b: correct kernel extraction from BKZ'd Kannan ckpt + enum + decode + assemble + submit
import os, re, json, time, subprocess, math
from fractions import Fraction
D = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(D, f)
LOG = open(P("engine3b.log"), "a", buffering=1)
def log(*a): print(*a, flush=True); print(int(time.time()), *a, file=LOG, flush=True)
import fpylll
from fpylll import IntegerMatrix, LLL, GSO, Enumeration, FPLLL, EvaluatorStrategy
FPLLL.set_threads(1)

Krows = json.load(open(P("kannan3_ckpt.json")))
assert len(Krows) == 249 and len(Krows[0]) == 505
a = [r[504] for r in Krows]
# pure-python: kernel of the 1x249 form c -> c.a via pair-generators + LLL (GP matkerl removed in 2.17)
import math
g = 0
for x in a: g = math.gcd(g, x)
aa = [x//g for x in a]
gens = []
for i in range(249):
    for j in range(i+1, 249):
        if aa[i] == 0 and aa[j] == 0: continue
        v = [0]*249; v[i] = aa[j]; v[j] = -aa[i]
        gens.append(v)
log("pair generators:", len(gens))
Mg = IntegerMatrix(len(gens), 249)
for i, r_ in enumerate(gens):
    for j, v in enumerate(r_): Mg[i, j] = v
t0 = time.time(); LLL.reduction(Mg, delta=0.99)
log(f"LLL gens {time.time()-t0:.0f}s")
coefs = []
for i in range(len(gens)):
    r_ = [int(Mg[i, j]) for j in range(249)]
    if any(r_): coefs.append(r_)
coefs = [c for c in coefs if sum(ci*ai for ci, ai in zip(c, a)) == 0]
log("kernel vectors after check:", len(coefs))
assert len(coefs) == 248, len(coefs)
K2 = []
for c in coefs:
    v = [0]*505
    for i in range(249):
        if c[i]: v = [x + c[i]*y for x, y in zip(v, Krows[i])]
    assert v[504] == 0
    K2.append(v[:504])

# blocks
keep = [int(x) for x in re.findall(r"\d+", open(P("rev_keep.txt")).readline())]
txt = open(P("cvecs.gp")).read()
CV = {bi: [int(x) for x in re.search(rf"^c{bi+1} = (.*)$", txt, re.M).group(1).strip(";[] ").split(",")] for bi in range(7)}
lines_l = open(P("live_output.txt")).read().splitlines()
secret = bytes.fromhex(lines_l[0])
state = __import__("hashlib").sha512(secret).digest(); pub = []
for _ in range(256):
    pub.append(int.from_bytes(state, "big")); state = __import__("hashlib").sha512(state).digest()
A = [[(pub[j] >> (511-k)) & 1 for k in range(512)] for j in range(256)]
A2 = [[A[j][keep[i]-1] for i in range(504)] for j in range(256)]
def load_blk(tag):
    if tag.startswith("toy"):
        bi = int(tag[3:]); s = open(P(f"toy_b{bi}.gp")).read()
        m0 = [int(x) for x in re.search(r"m0p = \[(.*?)\]", s, re.S).group(1).split(",")]
        cc = [int(x) for x in re.search(r"cc = \[(.*?)\]", s, re.S).group(1).split(",")]
    else:
        bi = int(tag[1:])
        m0 = [int(x) for x in open(P(f"rev_m0_b{bi}.txt")).readline().strip().strip("[]").split(",")]
        cc = CV[bi]
    return m0, cc
def segs_from_m(m):
    bits = [0]*512
    for i in range(504): bits[keep[i]-1] = m[i]
    return bytes(sum(bits[b*8+k] * 2**(7-k) for k in range(1,9)) for b in range(24,32))
def to_IM(rows):
    Mm = IntegerMatrix(len(rows), len(rows[0]))
    for i, row in enumerate(rows):
        for j, v in enumerate(row): Mm[i, j] = v
    return Mm

def try_block(tag):
    if tag != "toy0" and os.path.exists(P(f"SEG3_{tag}.txt")):
        log(f"{tag}: reuse existing SEG"); return bytes.fromhex(open(P(f"SEG3_{tag}.txt")).read())
    m0, cc = load_blk(tag)
    T0 = [1 - 2*v for v in m0]
    rows = [r + [0] for r in K2] + [T0 + [1]]
    Mi = to_IM(rows)
    t0 = time.time(); LLL.reduction(Mi, delta=0.99)
    g = GSO.Mat(Mi, update=True)
    pr = sorted(float(g.get_r(i,i))**2 for i in range(249))
    log(f"{tag}: kannan(raw T0) LLL {time.time()-t0:.0f}s min={pr[0]:.3g} nlev={sum(1 for x in pr if x<=506)}")
    from fpylll import Pruning
    sols = []
    for nexp, prob in ((2**30, 0.95), (2**35, 0.90)):
        try:
            pr = Pruning.run(g.get_r(0, 0), nexp, g.r(), prob)
            e = Enumeration(g, pruning=pr.coefficients)
        except Exception as ex:
            log(f"{tag}: pruning setup failed ({ex}) -> plain enum")
            e = Enumeration(g)
        te = time.time()
        try:
            sols = e.enumerate(0, 249, 506, 0)
        except Exception as ex:
            log(f"{tag}: enum raised {ex}"); sols = []
        log(f"{tag}: enum(nodes<={nexp/1e9:.0f}e9) found={len(sols)} in {time.time()-te:.0f}s")
        if sols: break
    kr = [[int(Mi[i,j]) for j in range(505)] for i in range(249)]
    for s in sols:
        a2, b2 = s
        coeffs, n2 = (a2, b2) if isinstance(a2, (list, tuple)) else (b2, a2)
        if abs(abs(float(coeffs[248])) - 1) > 1e-6: continue
        v = [0]*505
        for i in range(249):
            c = int(round(coeffs[i]))
            if c: v = [x + c*y for x, y in zip(v, kr[i])]
        if abs(v[504]) != 1: continue
        for sgn in (1, -1):
            Tc = [sgn*x for x in v[:504]]
            if not all((T0[j]-Tc[j]) % 2 == 0 for j in range(504)): continue
            m = [m0[j] + (T0[j]-Tc[j])//2 for j in range(504)]
            if all(x in (0,1) for x in m) and all(sum(A2[j][i]*m[i] for i in range(504)) == cc[j] for j in range(256)):
                seg = segs_from_m(m)
                log(f"{tag}: SOLVED seg={seg!r}")
                open(P(f"SEG3_{tag}.txt"), "w").write(seg.hex())
                return seg
    log(f"{tag}: NO verified solution ({len(sols)} sols, last-coords seen: "
        f"{sorted(set(int(round(s[0][248] if isinstance(s[0],(list,tuple)) else s[1][248])) for s in sols[:20]))})")
    return None

try:
    seg0 = try_block("toy0")
    if seg0 is not None:
        exp = open(P("toy_expect.txt")).read().encode()
        log(f"TOY first-8 match: {seg0 == exp[:8]} got {seg0!r} exp {exp[:8]!r}")
    res = {}
    for b in range(7):
        sg = try_block(f"b{b}")
        res[f"b{b}"] = sg.hex() if sg else None
        log(f"b{b} -> {res[f'b{b}']}")
    json.dump(res, open(P("RESULT3.json"), "w"))
    if all(res.values()):
        flag = b"".join(bytes.fromhex(v) for v in res.values()).rstrip(b"\x00").decode("latin-1")
        log(f"FLAG_CANDIDATE {flag!r}")
        if all(32 <= ord(c) < 127 for c in flag):
            rr = subprocess.run(["python3", "submit_flag.py", "failproof_revenge-sekaictf202", flag],
                                cwd=os.path.dirname(D), capture_output=True, text=True, timeout=180)
            log("SUBMIT: " + rr.stdout[-300:] + rr.stderr[-200:])
            if "ok" in rr.stdout and ("true" in rr.stdout or "True" in rr.stdout):
                open(P("flag_failproof_revenge-sekaictf202.txt"), "w").write(flag)
                log("FLAG FILE WRITTEN (submit ok)")
except Exception:
    import traceback; log("FATAL:\n" + traceback.format_exc())
log("3b DONE")
