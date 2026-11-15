# RUN#4 engine: resume BKZ ladder at B35 from kannan3_ckpt.json (BKZ-25 plateau, spread
# 1.0875), 240s-capped chunks (fplll max_time -> per-tour bound), checkpoint kannan4_b{beta}.json
# per chunk, curve4.csv; toy-enum gate (300s, toygate4.py subprocess) at spread levels
# 1.08/1.07/1.06/1.05; on gate pass -> real4.py b0 (600s) -> rest blocks -> assemble3+submit.
# Caps: B35 5400s, B45 7200s (escalate only if spread>1.06 at B35 cap), global 16200s, RSS 1.95GB.
import os, sys, json, time, math, subprocess, traceback
D = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(D, f)
PY = r"~\tools\crypto-ctf\venv\Scripts\python.exe"
LOG = open(P("engine4.log"), "a", buffering=1)
def log(*a): print(*a, flush=True); print(int(time.time()), *a, file=LOG, flush=True)
from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration, FPLLL
FPLLL.set_threads(1); FPLLL.set_random_seed(259)

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

def to_IM(rows):
    Mm = IntegerMatrix(len(rows), len(rows[0]))
    for i, row in enumerate(rows):
        for j, v in enumerate(row): Mm[i, j] = v
    return Mm

def gso_profile(Mi, n):
    g = GSO.Mat(Mi, update=True)
    return [float(g.get_r(i, i))**2 for i in range(n)]

def metrics(pr, R2=505.0):
    p = sorted(x for x in pr if 0 < x < 1e300)
    n = len(p)
    if n == 0: return float("inf"), 0, 0, 0, 0.0
    spread = (p[-1]/p[0])**(1.0/n)
    nlev = sum(1 for x in p if x <= R2)
    best = 0.0; s = 0.0
    for k in range(1, n+1):
        s += math.log(p[k-1])
        gm = math.exp(s/k)
        arg = R2 * 2*math.pi*math.e / (k*gm)
        if arg > 1:
            term = 0.5*k*math.log10(arg)
            if term > best: best = term
    return spread, p[0], p[-1], nlev, best

def run_child(args, timeout, name):
    t0 = time.time()
    try:
        r = subprocess.run([PY]+args, capture_output=True, text=True, timeout=timeout, cwd=D)
        out = (r.stdout or "").strip()
        log(f"{name}: rc={r.returncode} {time.time()-t0:.0f}s | {out[-700:]}")
        if r.stderr and r.stderr.strip(): log(f"{name}: stderr: {r.stderr.strip()[-300:]}")
        return r.returncode, out
    except subprocess.TimeoutExpired:
        log(f"{name}: TIMEOUT >{time.time()-t0:.0f}s"); return -1, ""
    except Exception as ex:
        log(f"{name}: EXC {ex}"); return -2, ""

def main():
    ckpt_file = sys.argv[1] if len(sys.argv) > 1 else "kannan3_ckpt.json"
    start_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    t_all = time.time()
    log(f"== RUN#4 engine start resume={ckpt_file} start_beta_idx={start_idx}")
    Krows = json.load(open(P(ckpt_file)))
    assert len(Krows) == 249 and len(Krows[0]) == 505
    Mki = to_IM(Krows)
    pr = gso_profile(Mki, 249)
    spa0, mn0, _, nlev0, cost0 = metrics(pr)
    log(f"resume profile: spread={spa0:.4f} min={mn0:.3g} nlev<=505={nlev0} log10cost={cost0:.1f}")

    CURVE = open(P("curve4.csv"), "a", buffering=1)
    CURVE.write("t_rel,phase_wall,beta,chunk,spread_kannan,min_kannan,nlev_kannan,log10cost,rss_MB,note\n")
    BETAS = [35, 45]; CAPS = {35: 5400, 45: 7200}
    MAXTOT = 16200; CHUNK = 240
    GATES = [1.08, 1.07, 1.06, 1.05]; gates_done = set()
    bi = start_idx; chunk = 0
    phase_t = time.time(); status = "CURVE"; solved = False
    best_spread = spa0; best_file = P(ckpt_file)

    def full_solve(ck, note):
        # returns True iff flag file appeared
        rc, out = run_child([P("real4.py"), ck, "b0"], 600, f"REAL b0 ({note})")
        if "SOLVED" not in out: return False
        for b in range(1, 7):
            if os.path.exists(P(f"SEG3_b{b}.txt")): continue
            if time.time() - t_all + 700 > MAXTOT: log("budget stop before rest blocks"); return False
            rc, out = run_child([P("real4.py"), ck, f"b{b}"], 600, f"REAL b{b} ({note})")
            if "SOLVED" not in out: log(f"b{b} failed mid-rest; abort assemble"); return False
        rc, out = run_child([P("assemble3.py")], 300, f"ASSEMBLE+SUBMIT ({note})")
        return os.path.exists(P("flag_failproof_revenge-sekaictf202.txt"))

    while True:
        el = time.time() - t_all; pel = time.time() - phase_t
        r = rss_bytes()
        if r and r > 1.95e9: log(f"KILL MEM rss={r/1e6:.0f}MB t={el:.0f}s"); status = "MEM"; break
        if el > MAXTOT: log(f"KILL GLOBAL BUDGET t={el:.0f}s"); status = "BUDGET"; break
        beta = BETAS[bi]
        if pel > CAPS[beta]:
            if beta == 35 and best_spread > 1.06:
                bi += 1; phase_t = time.time()
                log(f"B35 cap reached (spread best {best_spread:.4f} > 1.06) -> escalate B45")
                continue
            log(f"B{beta} cap reached best_spread={best_spread:.4f} -> stop ladder"); status = "CURVE"; break
        try:
            p = BKZ.EasyParam(beta, delta=0.99, max_time=CHUNK, flags=BKZ.AUTO_ABORT)
        except TypeError:
            try: p = BKZ.EasyParam(beta, timeout=CHUNK, flags=BKZ.AUTO_ABORT)
            except TypeError: p = BKZ.EasyParam(beta)
        tc = time.time()
        try:
            BKZ.reduction(Mki, p)
        except Exception as ex:
            log(f"BKZ error beta={beta}: {ex}"); status = "BKZERR"; break
        chunk += 1
        Krows = [[int(Mki[i, j]) for j in range(505)] for i in range(249)]
        pr = gso_profile(Mki, 249)
        spa, mn, mx, nlev, cost = metrics(pr)
        rssMB = (r or 0)/1e6
        CURVE.write(f"{el:.0f},{pel:.0f},{beta},{chunk},{spa:.4f},{mn:.3g},{nlev},{cost:.2f},{rssMB:.0f},chunk\n")
        log(f"t={el:.0f}s beta={beta} chunk={chunk} ({time.time()-tc:.0f}s) spread={spa:.4f} min={mn:.3g} nlev={nlev} log10cost={cost:.1f} rss={rssMB:.0f}MB")
        ck = P(f"kannan4_b{beta}.json")
        with open(ck, "w") as f: json.dump(Krows, f)
        if spa < best_spread: best_spread = spa; best_file = ck
        if spa < spa0 - 0.0495 or True:
            pass
        # ---- toy gates at spread levels ----
        for L in GATES:
            if L in gates_done or spa > L: continue
            gates_done.add(L)
            if time.time() - t_all + 400 > MAXTOT: log("no budget for remaining gates"); break
            rc, out = run_child([P("toygate4.py"), ck, str(L)], 300, f"TOYGATE@{L}")
            CURVE.write(f"{time.time()-t_all:.0f},{time.time()-phase_t:.0f},{beta},{chunk},{spa:.4f},{mn:.3g},{nlev},{cost:.2f},{rssMB:.0f},gate{L}:{'PASS' if '\"verified\": true' in out else 'fail/timeout'}\n")
            if rc == 0 and '"verified": true' in out:
                log(f"*** TOY GATE PASSED at L={L} spread={spa:.4f} ***")
                if full_solve(ck, f"L={L}"):
                    solved = True; status = "SOLVED"; break
                log("gate passed but real solve incomplete; continue ladder")
        if solved: break

    # final extended gate if ladder ended unsolved with budget left
    if not solved:
        rem = MAXTOT - (time.time() - t_all)
        if rem > 1000 and 1.05 not in gates_done:
            log(f"final extended toy gate at best ckpt ({os.path.basename(best_file)}, spread {best_spread:.4f}), budget left {rem:.0f}s")
            rc, out = run_child([P("toygate4.py"), best_file, "final"], int(min(900, rem - 60)), "TOYGATE-FINAL")
            if rc == 0 and '"verified": true' in out:
                if full_solve(best_file, "final"):
                    solved = True; status = "SOLVED"
    log(f"ENGINE FINAL status={status} best_spread={best_spread:.4f} total={time.time()-t_all:.0f}s")
    CURVE.close(); LOG.close()

try:
    main()
except Exception:
    log("FATAL:\n" + traceback.format_exc()); sys.exit(1)
