# RUN#3 engine: LLL -> BKZ ladder (B25->B35->B45) on Kannan embedding (per-block),
# GSO-spread + enum-cost-proxy per chunk, checkpoint every chunk, then enum radius^2 505.
# Single-threaded, self-guarded on RSS. Log: engine3.log ; curve: curve3.csv ; ckpt: basis3_ckpt.json
import os, re, sys, json, time, math, traceback
from fractions import Fraction
D = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(D, f)
LOG = open(P("engine3.log"), "a", buffering=1)
def log(*a): print(*a, flush=True); print(int(time.time()), *a, file=LOG, flush=True)

FPLLL_threads = None
try:
    import fpylll
    from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration, FPLLL, EvaluatorStrategy
    FPLLL.set_threads(1)
    FPLLL.set_random_seed(259)
except Exception as ex:
    log("FATL fpylll import", ex); sys.exit(1)

# ---------- RSS guard (psapi via ctypes) ----------
def rss_bytes():
    try:
        import ctypes, ctypes.wintypes as wt
        class PMC(ctypes.Structure):
            _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        mod = ctypes.windll.psapi
        pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
        h = ctypes.windll.kernel32.GetCurrentProcess()
        if mod.GetProcessMemoryInfo(h, ctypes.byref(pmc), pmc.cb): return int(pmc.WorkingSetSize)
    except Exception:
        pass
    return None

# ---------- load data ----------
keep = [int(x) for x in re.findall(r"\d+", open(P("rev_keep.txt")).readline())]
assert len(keep) == 504
K = []
for l in open(P("rev_K.txt")):
    l = l.strip()
    if l: K.append([int(x) for x in l.strip("[]").split(",")])
assert len(K) == 248 and all(len(r) == 504 for r in K)
txt = open(P("cvecs.gp")).read()
CV = {bi: [int(x) for x in re.search(rf"^c{bi+1} = (.*)$", txt, re.M).group(1).strip(";[] ").split(",")] for bi in range(7)}
assert all(len(CV[bi]) == 256 for bi in range(7))

# A from live secret (same as clean_prep)
lines_l = open(P("live_output.txt")).read().splitlines()
secret = bytes.fromhex(lines_l[0])
state = __import__("hashlib").sha512(secret).digest(); pub = []
for _ in range(256):
    pub.append(int.from_bytes(state, "big")); state = __import__("hashlib").sha512(state).digest()
A = [[(pub[j] >> (511 - k)) & 1 for k in range(512)] for j in range(256)]
A2 = [[A[j][keep[i]-1] for i in range(504)] for j in range(256)]

def load_blk(tag):
    if tag.startswith("toy"):
        bi = int(tag[3:])
        s = open(P(f"toy_b{bi}.gp")).read()
        m0 = [int(x) for x in re.search(r"m0p = \[(.*?)\]", s, re.S).group(1).split(",")]
        cc = [int(x) for x in re.search(r"cc = \[(.*?)\]", s, re.S).group(1).split(",")]
    else:
        bi = int(tag[1:])
        m0 = [int(x) for x in open(P(f"rev_m0_b{bi}.txt")).readline().strip().strip("[]").split(",")]
        cc = CV[bi]
    assert len(m0) == 504 and len(cc) == 256
    return bi, m0, cc

def verify_m(m0, cc):
    return max(abs(sum(A2[j][i]*m0[i] for i in range(504)) - cc[j]) for j in range(256))

def segs_from_m(m):
    bits = [0]*512
    for i in range(504): bits[keep[i]-1] = m[i]
    # byte b (0-idx): positions p=b*8+1..b*8+8, weight 2^(b*8+8-p)
    return bytes(sum(bits[b*8+k] * 2**(7-k) for k in range(1, 9)) for b in range(24, 32))

# ---------- exact target reduction ----------
def greedy_reduce(t, B):  # t: list[int]; B: list[list[int]] integer basis rows
    t = list(t)
    nrm2 = [sum(x*x for x in row) for row in B]
    for _pass in range(60):
        changed = False
        for r, row in enumerate(B):
            dot = sum(ti*bi for ti, bi in zip(t, row))
            if abs(dot)*2 < nrm2[r]: continue
            q = round(Fraction(dot, nrm2[r]))
            if q:
                t = [ti - q*bi for ti, bi in zip(t, row)]; changed = True
        if not changed: break
    return t

def profile(B2d, tag):  # list rows int -> sorted ||b*||^2 profile via double GSO
    Mm = IntegerMatrix(len(B2d), len(B2d[0]))
    for i, row in enumerate(B2d):
        for j, v in enumerate(row): Mm[i, j] = v
    g = GSO.Mat(Mm, update=True)
    pr = [float(g.get_r(i, i))**2 for i in range(len(B2d))]
    return pr

def gso_profile_hi(Mi, n):
    # high-precision (mpf) profile to guard against double-precision faking a flat tail
    # (run#2 lesson: insufficient precision fakes small levels; double can also HIDE them
    # under a cancellation floor ~ ||b||^2 * eps at dim 248)
    for kw in ({"float_type": "mpf", "precision": 300}, {"float_type": "mpf"}):
        try:
            g = GSO.Mat(Mi, update=True, **kw)
            return [float(g.get_r(i, i))**2 for i in range(n)], "mpf"
        except TypeError:
            continue
        except Exception:
            break
    g = GSO.Mat(Mi, update=True)
    return [float(g.get_r(i, i))**2 for i in range(n)], "double"

def metrics(pr, R2=505.0):
    p = sorted(x for x in pr if x > 0)
    n = len(p)
    spread = (p[-1]/p[0])**(1.0/n)
    nlev = sum(1 for x in p if x <= R2)
    best = 0.0
    s = 0.0
    for k in range(1, n+1):
        s += math.log(p[k-1])
        gm = math.exp(s/k)
        arg = R2 * 2*math.pi*math.e / (k*gm)
        if arg > 1:
            term = 0.5*k*math.log10(arg)
            if term > best: best = term
    return spread, p[0], p[-1], nlev, best

# ---------- main ----------
def main():
    t_all = time.time()
    log("== RUN#3 engine start")
    # verify all blocks' m0 (cheap int check) — toy + real
    for tag in ["toy0"] + [f"b{i}" for i in range(7)]:
        bi, m0, cc = load_blk(tag)
        assert verify_m(m0, cc) == 0, f"bad m0 {tag}"
    log("verified: A2*m0 == c for toy0 + b0..b6")

    # LLL the shared kernel basis 2K (ZMP)
    B2 = [[2*v for v in row] for row in K]
    Mb = IntegerMatrix(248, 504)
    for i, row in enumerate(B2):
        for j, v in enumerate(row): Mb[i, j] = v
    t0 = time.time(); LLL.reduction(Mb, delta=0.99)
    log(f"LLL(2K) done in {time.time()-t0:.0f}s")
    Bred = [[int(Mb[i, j]) for j in range(504)] for i in range(248)]
    pr = profile(Bred, "kernel")
    sp, mn, mx, nlev, cost = metrics(pr)
    log(f"LLL kernel: spread/level={sp:.4f} min||b*||2={mn:.3g} max={mx:.3g} nlev<=505={nlev} log10cost={cost:.1f}")
    with open(P("basis3_ckpt.json"), "w") as f: json.dump(Bred, f)

    # per-block exact reduced targets t (store; T0 kept implicit via m0)
    for tag in ["toy0", "toy1"] + [f"b{i}" for i in range(7)]:
        bi, m0, cc = load_blk(tag)
        T0 = [1 - 2*v for v in m0]
        # NOTE: greedy Babai-style reduction stalls (codim-256 lattice; residual dominated by
        # rounding along 248 near-dependent rows). Embed RAW T0 instead: (T|1) is provably in
        # latt[(Bred|0);(T0|1)] and fplll ZMP LLL/BKZ on exactly this huge-row embedding was
        # exercised successfully in run#1. fpylll GSO converts exact ratios -> no precision issue.
        t = T0
        log(f"{tag}: embedded RAW T0 (|T0|^2 ~1e{len(str(abs(sum(x*x for x in T0))))-1})")
        with open(P(f"tred3_{tag}.json"), "w") as f: json.dump(t, f)

    # ---------- Kannan embedding for toy0 (shared lattice; guaranteed solution) ----------
    bi, m0, cc = load_blk("toy0")
    t = json.load(open(P("tred3_toy0.json")))
    def kannan_rows(B2d, tv):
        return [row + [0] for row in B2d] + [tv + [1]]
    def to_IM(rows):
        Mm = IntegerMatrix(len(rows), len(rows[0]))
        for i, row in enumerate(rows):
            for j, v in enumerate(row): Mm[i, j] = v
        return Mm

    Mk = kannan_rows(Bred, t)
    Mki = to_IM(Mk)
    LLL.reduction(Mki, delta=0.99)
    Bk = [[int(Mki[i, j]) for j in range(505)] for i in range(249)]
    prk = profile(Bk, "kannan")
    sp, mn, mx, nlev, cost = metrics(prk)
    log(f"LLL kannan toy0: spread={sp:.4f} min={mn:.3g} nlev={nlev} log10cost={cost:.1f}")

    # ---------- BKZ ladder ----------
    CURVE = open(P("curve3.csv"), "a", buffering=1)
    CURVE.write("t_rel,beta,chunk,spread_kern,spread_kannan,min_kern,min_kannan,nlev_kern,nlev_kannan,log10cost_kannan,rss_MB,phase\n")
    BETAS = [25, 35, 45]
    MAXTOT = 5.2*3600; CHUNK = 240
    bi_idx = 0; chunk = 0; phase_t = time.time(); hist = []
    status = "CURVE"
    B = Bred; Krows = Bk
    while True:
        el = time.time() - t_all
        r = rss_bytes()
        if r and r > 1.95e9:
            log(f"KILL MEM rss={r/1e6:.0f}MB t={el:.0f}s"); status = "MEM"; break
        if el > MAXTOT:
            log(f"KILL BUDGET t={el:.0f}s"); status = "BUDGET"; break
        beta = BETAS[bi_idx]
        try:
            p = BKZ.EasyParam(beta, delta=0.99, max_time=CHUNK)
        except TypeError:
            try:
                p = BKZ.EasyParam(beta, timeout=CHUNK)
            except TypeError:
                p = BKZ.EasyParam(beta)
        tc = time.time()
        try:
            BKZ.reduction(Mki, p)
        except Exception as ex:
            log(f"BKZ error beta={beta}: {ex}"); traceback.print_exc(file=LOG); status = "BKZERR"; break
        chunk += 1
        Krows = [[int(Mki[i, j]) for j in range(505)] for i in range(249)]
        Ksub = [row[:504] for row in Krows]
        # kernel flatness = first 248 GSO levels of kannan (row order after BKZ: use its own profile excluding last GSO value)
        Msub = to_IM(Ksub)
        gk = GSO.Mat(Msub, update=True)
        pr_sub = [float(gk.get_r(i, i))**2 for i in range(248)]
        g = GSO.Mat(Mki, update=True)
        pr_all = [float(g.get_r(i, i))**2 for i in range(249)]
        skp, mnsk, _, nlk, _ = metrics(pr_sub)
        spa, mnk, _, nla, cost = metrics(pr_all)
        rssMB = (r or 0)/1e6
        CURVE.write(f"{el:.0f},{beta},{chunk},{skp:.4f},{spa:.4f},{mnsk:.3g},{mnk:.3g},{nlk},{nla},{cost:.2f},{rssMB:.0f},{beta}\n")
        log(f"t={el:.0f}s beta={beta} chunk={chunk} ({time.time()-tc:.0f}s) kern: spread={skp:.4f} min={mnsk:.3g} nlev={nlk} | kannan: spread={spa:.4f} min={mnk:.3g} nlev={nla} log10cost={cost:.1f} rss={rssMB:.0f}MB")
        with open(P("basis3_ckpt.json"), "w") as f: json.dump(Ksub, f)
        with open(P("kannan3_ckpt.json"), "w") as f: json.dump(Krows, f)
        hist.append((time.time(), skp, cost))
        # gates
        if cost < 9.5:
            pr_hi, kind = gso_profile_hi(Mki, 249)
            spa2, mn2, _, nla2, cost2 = metrics(pr_hi)
            log(f"gate recheck with {kind}: spread={spa2:.4f} min={mn2:.3g} nlev={nla2} log10cost={cost2:.1f}")
            if cost2 < 9.5:
                log("GATE: enum cost acceptable (hi-prec) -> ENUM phase"); status = "ENUM"; break
            else:
                log("double-precision profile was optimistic; continuing ladder")
                hist[-1] = (time.time(), -1.0, cost2)  # block repeat-recheck spam
        # plateau/escalation
        if len(hist) >= 5:
            imp = hist[-5][1] - hist[-1][1]
            if imp < 0.0015 and skp > 1.10 and (time.time()-phase_t) > 1800:
                if bi_idx < 2:
                    bi_idx += 1; phase_t = time.time(); hist = []
                    log(f"PLATEAU beta={BETAS[bi_idx-1]} spread={skp:.4f} -> escalate to {BETAS[bi_idx]}")
                else:
                    log(f"PLATEAU beta=45 spread={skp:.4f} -> stop CURVE"); status = "CURVE"; break

    # ---------- ENUM phase ----------
    if status == "ENUM":
        R2 = 506
        def try_block(tag, Krows, cc, m0):
            tv = json.load(open(P(f"tred3_{tag}.json")))
            rows = kannan_rows([r[:504] for r in Krows], tv)
            Mi = to_IM(rows)
            LLL.reduction(Mi, delta=0.99)
            g = GSO.Mat(Mi, update=True)
            pr_hi, kind = gso_profile_hi(Mi, 249)
            _, _, _, nlev, cost = metrics(pr_hi)
            log(f"{tag}: kannan polish [{kind}] nlev={nlev} log10cost={cost:.1f}")
            if cost > 10.5:
                log(f"{tag}: SKIP enum (cost too high)"); return None
            e = Enumeration(g)
            t_e = time.time()
            sols = e.enumerate(0, 249, R2, 0)
            log(f"{tag}: enum nodes={e.get_nodes()} found={len(sols)} in {time.time()-t_e:.0f}s")
            kr = [[int(Mi[i, j]) for j in range(505)] for i in range(249)]
            T0 = [1 - 2*mo for mo in m0]
            for s in sols:
                a, b = s
                coeffs, n2 = (a, b) if isinstance(a, (list, tuple)) else (b, a)
                if abs(abs(float(coeffs[248])) - 1) > 1e-6: continue
                v = [0]*505
                for i in range(249):
                    c = int(round(coeffs[i]))
                    if c: v = [x + c*y for x, y in zip(v, kr[i])]
                if abs(v[504]) != 1: continue
                # short vector is eps*(T|1) with T in T0+2K, ||T||^2=504; try both signs, verify decides
                for sgn in (1, -1):
                    Tc = [sgn*x for x in v[:504]]
                    if not all((T0[j]-Tc[j]) % 2 == 0 for j in range(504)): continue
                    m = [m0[j] + (T0[j]-Tc[j])//2 for j in range(504)]
                    if all(x in (0, 1) for x in m) and all(sum(A2[j][i]*m[i] for i in range(504)) == cc[j] for j in range(256)):
                        seg = segs_from_m(m)
                        log(f"{tag}: SOLVED seg={seg!r}")
                        with open(P(f"SEG3_{tag}.txt"), "w") as f: f.write(seg.hex())
                        return seg
            log(f"{tag}: no verified solution among {len(sols)} sols")
            return None

        # toy first (guaranteed)
        bi, m0t, cct = load_blk("toy0")
        seg = try_block("toy0", Krows, cct, m0t)
        if seg is not None:
            exp = open(P("toy_expect.txt")).read().encode()
            log(f"TOY match first block? {seg == exp[:8]} (got {seg!r} expect {exp[:8]!r})")
        res = {}
        for b in range(7):
            tag = f"b{b}"
            bi, m0, cc = load_blk(tag)
            sg = try_block(tag, Krows, cc, m0)
            res[tag] = sg.hex() if sg else None
        with open(P("RESULT3.json"), "w") as f: json.dump(res, f)
        log("ENUM phase done")
    log(f"ENGINE FINAL status={status} total={time.time()-t_all:.0f}s")

try:
    main()
except Exception:
    log("FATAL:\n" + traceback.format_exc()); sys.exit(1)
