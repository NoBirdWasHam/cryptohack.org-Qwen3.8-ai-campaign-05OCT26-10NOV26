# RUN#4 real-block leg: exact kernel extraction from BKZ'd Kannan ckpt (engine3b method)
# + Kannan(raw ORIGINAL T0) + LLL + plain enum r2=506 + decode + 256-popcount verify.
# usage: real4.py <kannan_ckpt.json> <b0..b6>   -> writes SEG3_<tag>.txt on success
import os, re, sys, json, time, math, threading, ctypes
D = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(D, f)
ckpt, tag = sys.argv[1], sys.argv[2]
assert re.fullmatch(r"b[0-6]", tag)
if os.path.exists(P(f"SEG3_{tag}.txt")):
    print("SOLVED reuse", tag, open(P(f"SEG3_{tag}.txt")).read().strip(), flush=True); sys.exit(0)

def rss_bytes():
    try:
        import ctypes.wintypes as wt
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
    return 0
def watchdog():
    while True:
        time.sleep(2)
        r = rss_bytes()
        if r and r > 1.85e9:
            print("RSS-OOM", flush=True); os._exit(4)
threading.Thread(target=watchdog, daemon=True).start()

from fpylll import IntegerMatrix, LLL, GSO, Enumeration, FPLLL
FPLLL.set_threads(1)

Krows = json.load(open(ckpt))
assert len(Krows) == 249 and len(Krows[0]) == 505
a = [r[504] for r in Krows]
gg = 0
for x in a: gg = math.gcd(gg, x)
aa = [x//gg for x in a]
gens = []
for i in range(249):
    for j in range(i+1, 249):
        if aa[i] == 0 and aa[j] == 0: continue
        v = [0]*249; v[i] = aa[j]; v[j] = -aa[i]
        gens.append(v)
Mg = IntegerMatrix(len(gens), 249)
for i, r_ in enumerate(gens):
    for j, v in enumerate(r_): Mg[i, j] = v
LLL.reduction(Mg, delta=0.99)
coefs = []
for i in range(len(gens)):
    r_ = [int(Mg[i, j]) for j in range(249)]
    if any(r_) and sum(ci*ai for ci, ai in zip(r_, a)) == 0: coefs.append(r_)
assert len(coefs) == 248, f"kernel dim {len(coefs)}"
K2 = []
for c in coefs:
    v = [0]*505
    for i in range(249):
        if c[i]: v = [x + c[i]*y for x, y in zip(v, Krows[i])]
    assert v[504] == 0
    K2.append(v[:504])

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
bi = int(tag[1:])
m0 = [int(x) for x in open(P(f"rev_m0_b{bi}.txt")).readline().strip().strip("[]").split(",")]
cc = CV[bi]
assert max(abs(sum(A2[j][i]*m0[i] for i in range(504)) - cc[j]) for j in range(256)) == 0, f"bad m0 {tag}"
T0 = [1 - 2*v for v in m0]

rows = [r + [0] for r in K2] + [T0 + [1]]
Mi = IntegerMatrix(249, 505)
for i, row in enumerate(rows):
    for j, v in enumerate(row): Mi[i, j] = v
t0 = time.time(); LLL.reduction(Mi, delta=0.99)
g = GSO.Mat(Mi, update=True)
pr = sorted(float(g.get_r(i, i))**2 for i in range(249))
fin = [x for x in pr if x < 1e300]
nlev = sum(1 for x in fin if x <= 506)
print(f"{tag}: kernel {time.time()-t0:.0f}s kannan LLL min={fin[0]:.3g} nlev<=506={nlev} inflevels={len(pr)-len(fin)}", flush=True)
t0 = time.time()
e = Enumeration(g)
try:
    sols = e.enumerate(0, 249, 506, 0)
except Exception as ex:
    print(f"NOSOLV enum-exc {ex}", flush=True); sys.exit(0)
nodes = e.get_nodes()
print(f"{tag}: enum nodes={nodes} sols={len(sols)} in {time.time()-t0:.0f}s", flush=True)
kr = [[int(Mi[i, j]) for j in range(505)] for i in range(249)]
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
            open(P(f"SEG3_{tag}.txt"), "w").write(seg.hex())
            print(f"SOLVED {tag} {seg.hex()} seg={seg!r}", flush=True)
            sys.exit(0)
print(f"NOSOLV sols={len(sols)} nodes={nodes}", flush=True)
