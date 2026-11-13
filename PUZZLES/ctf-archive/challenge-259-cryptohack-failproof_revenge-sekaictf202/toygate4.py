# RUN#4 toy gate: plain Enumeration r2=506 on the CURRENT BKZ'd toy Kannan ckpt (guaranteed
# solution inside). Decodes with ORIGINAL toy T0, verifies binary + all 256 popcount eqs.
# Parent enforces wall timeout; we self-kill on RSS>1.85GB. Print one TOYGATE line.
import os, re, sys, json, time, threading, ctypes
D = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(D, f)
ckpt = sys.argv[1]; lvl = sys.argv[2] if len(sys.argv) > 2 else "?"

def rss_bytes():
    try:
        import ctypes.wintypes as wt
        class PMC(ctypes.Structure):
            _fields_ = [("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("NonPagedPoolUsage" if 0 else "QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        mod = ctypes.windll.psapi
        pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
        h = ctypes.windll.kernel32.GetCurrentProcess()
        if mod.GetProcessMemoryInfo(h, ctypes.byref(pmc), pmc.cb): return int(pmc.WorkingSetSize)
    except Exception:
        pass
    return 0
def watchdog():
    while True:
        time.sleep(2)
        r = rss_bytes()
        if r and r > 1.85e9:
            print("TOYGATE RSS-OOM", flush=True); os._exit(4)
threading.Thread(target=watchdog, daemon=True).start()

from fpylll import IntegerMatrix, GSO, Enumeration, FPLLL
FPLLL.set_threads(1)

Krows = json.load(open(ckpt))
assert len(Krows) == 249 and len(Krows[0]) == 505

# toy0 data
s = open(P("toy_b0.gp")).read()
m0 = [int(x) for x in re.search(r"m0p = \[(.*?)\]", s, re.S).group(1).split(",")]
cc = [int(x) for x in re.search(r"cc = \[(.*?)\]", s, re.S).group(1).split(",")]
keep = [int(x) for x in re.findall(r"\d+", open(P("rev_keep.txt")).readline())]
lines_l = open(P("live_output.txt")).read().splitlines()
secret = bytes.fromhex(lines_l[0])
state = __import__("hashlib").sha512(secret).digest(); pub = []
for _ in range(256):
    pub.append(int.from_bytes(state, "big")); state = __import__("hashlib").sha512(state).digest()
A = [[(pub[j] >> (511 - k)) & 1 for k in range(512)] for j in range(256)]
A2 = [[A[j][keep[i] - 1] for i in range(504)] for j in range(256)]
assert max(abs(sum(A2[j][i]*m0[i] for i in range(504)) - cc[j]) for j in range(256)) == 0
T0 = [1 - 2*v for v in m0]

Mi = IntegerMatrix(249, 505)
for i, row in enumerate(Krows):
    for j, v in enumerate(row): Mi[i, j] = v
g = GSO.Mat(Mi, update=True)
pr = sorted(float(g.get_r(i, i))**2 for i in range(249))
nlev = sum(1 for x in pr if x <= 506)

t0 = time.time()
e = Enumeration(g)
try:
    sols = e.enumerate(0, 249, 506, 0)
except Exception as ex:
    print(f"TOYGATE L={lvl} EXC {ex}", flush=True); sys.exit(0)
nodes = e.get_nodes()
kr = [[int(Mi[i, j]) for j in range(505)] for i in range(249)]
out = {"verified": False, "nodes": nodes, "sols": len(sols), "nlev": nlev,
       "secs": round(time.time()-t0, 1), "spread": round((pr[-1]/pr[0])**(1/249), 4)}
for s_ in list(sols)[:200000]:
    a2, b2 = s_
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
        if all(x in (0, 1) for x in m) and all(sum(A2[j][i]*m[i] for i in range(504)) == cc[j] for j in range(256)):
            bits = [0]*512
            for i in range(504): bits[keep[i]-1] = m[i]
            seg = bytes(sum(bits[b*8+k]*2**(7-k) for k in range(1, 9)) for b in range(24, 32))
            exp = open(P("toy_expect.txt")).read().encode()
            out.update(verified=True, seg=seg.hex(), matches_toy=(seg == exp[:8]))
            break
    if out["verified"]: break
print("TOYGATE L=%s %s" % (lvl, json.dumps(out)), flush=True)
