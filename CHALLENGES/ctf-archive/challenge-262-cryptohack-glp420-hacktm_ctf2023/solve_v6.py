# GLP420 (HackTM 2023) solver v5 — 4 components, inverse-form lattices, lll5.exe
import os, sys, json, random, subprocess, threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
Q = 8383489
N = 420
B_ = 16383
W = 3
MSG = b"sign me!"

def centered(v):
    v %= Q
    return v - Q if v > Q // 2 else v

# ---- ring Z[x]/(x^420-1) ----
def mul420(u, v):
    tmp = [0] * (2 * N - 1)
    for i in range(N):
        if u[i]:
            ui = u[i]
            for j in range(N):
                tmp[i + j] = (tmp[i + j] + ui * v[j]) % Q
    r = tmp[:N]
    for i in range(N, 2 * N - 1):
        r[i - N] = (r[i - N] + tmp[i]) % Q
    return r

# ---- component rings: g monic integer poly, deg m ----
# g represented as dict exp->coef (int). reduction: x^D = -(g - x^D) evaluated
class Comp:
    def __init__(self, gpoly):
        # gpoly: list of (exp, coef) highest first, monic
        self.g = {e: c for e, c in gpoly}
        self.D = max(self.g)
        self.m = self.D

    def red_int(self, j):
        # x^j mod g over Z -> dict exp->coef
        terms = {j: 1}
        while True:
            e = max(terms)
            if e < self.D:
                break
            c = terms.pop(e)
            for ee, cc in self.g.items():
                if ee == self.D:
                    continue
                terms[ee + (e - self.D)] = terms.get(ee + (e - self.D), 0) - c * cc
        return {k: v for k, v in terms.items() if v}

    def red_poly(self, u):
        # u: list coeffs (any ints), reduce mod g over Z -> list len m
        tmp = list(u) + [0] * (2 * self.D)
        for i in range(len(tmp) - 1, self.D - 1, -1):
            c = tmp[i]
            if c:
                for ee, cc in self.g.items():
                    if ee == self.D:
                        continue
                    tmp[ee + (i - self.D)] += c * (-cc)
                tmp[i] = 0
        return tmp[:self.m]

    def fold(self, vec, mod=None):
        # residue of sum vec[j] x^j mod g ; mod=None -> ints, else mod Q
        out = [0] * self.m
        for j in range(N):
            if not vec[j]:
                continue
            for e, c in self.red_int(j).items():
                out[e] += c * vec[j]
        if mod:
            out = [x % Q for x in out]
        return out

    def ringmul(self, u, v):
        tmp = [0] * (2 * self.D)
        for i in range(self.m):
            if u[i]:
                ui = u[i]
                for j in range(self.m):
                    tmp[i + j] += ui * v[j]
        r = self.red_poly([x % Q for x in tmp])
        return [x % Q for x in r]

    def multmat(self, u):
        # matrix of mult by u (columns)
        M = [[0] * self.m for _ in range(self.m)]
        for k in range(self.m):
            col = self.ringmul(u, [1 if i == k else 0 for i in range(self.m)])
            for rr in range(self.m):
                M[rr][k] = centered(col[rr])
        return M

# components: x^105-1, x^105+1, x^70+1, Phi12*Phi60*Phi84, Phi420  (all lattices <= 210)
def _gp(p):
    from sympy import Poly
    P = Poly(p)
    d = P.degree()
    return [(i, int(P.nth(i))) for i in range(d + 1) if P.nth(i)]

def _make_comps():
    from sympy import symbols, cyclotomic_poly, expand
    x = symbols("x")
    g3 = expand(cyclotomic_poly(12, x) * cyclotomic_poly(60, x) * cyclotomic_poly(84, x))
    g4 = expand(cyclotomic_poly(420, x))
    return [
        Comp([(105, 1), (0, -1)]),
        Comp([(105, 1), (0, 1)]),
        Comp([(70, 1), (0, 1)]),
        Comp(_gp(g3)),
        Comp(_gp(g4)),
    ]

COMPS = _make_comps()

# ---- poly inverse mod g over F_q via sympy (cached) ----
def polyinv_modq(f, comp):
    from sympy import Poly, symbols, invert, GF
    x = symbols("x")
    gp = sum(c * x ** e for e, c in comp.g.items())
    fp = sum(c * x ** e for e, c in enumerate(f) if c % Q)
    ip = invert(Poly(fp, x, domain=GF(Q)), Poly(gp, x, domain=GF(Q)), x)
    d = ip.as_dict()
    return [int(ip.nth(i)) % Q for i in range(comp.m)]

# ---- fixed fold matrix inverse ----
def build_finv(cache=True):
    cpath = os.path.join(HERE, "_finv6.json")
    if cache and os.path.exists(cpath):
        return json.load(open(cpath))
    from sympy import Matrix, GF, invert as syminvert
    F = Matrix(N, N, lambda r, c: 0)
    rows = []
    off = 0
    for comp in COMPS:
        for k in range(comp.m):
            row = [0] * N
            for j in range(N):
                for e, c in comp.red_int(j).items():
                    if e == k:
                        row[j] += c
            rows.append([x % Q for x in row])
    from sympy import Matrix as Mx
    Fm = Mx([[Q and (x % Q) for x in r] for r in rows])
    Finv = Fm.inv_mod(Q) if hasattr(Fm, "inv_mod") else None
    if Finv is None:
        Finv = Fm.inv_mod(Q)
    data = [[int(x) % Q for x in Finv.row(i)] for i in range(N)]
    if cache:
        json.dump(data, open(cpath, "w"))
    return data

# ---- lattice run ----
def run_lll(comp_idx, lat_rows, target):
    m = comp_idx  # placeholder
    tag = f"{os.getpid()}_{id(lat_rows) % 10**6}"
    fin = os.path.join(HERE, f"_L{tag}.in")
    ftg = os.path.join(HERE, f"_T{tag}.in")
    with open(fin, "w") as f:
        f.write(f"{len(lat_rows)}\n")
        for r in lat_rows:
            f.write(" ".join(map(str, r)) + "\n")
    with open(ftg, "w") as f:
        f.write(" ".join(map(str, target)) + "\n")
    out = subprocess.check_output([os.path.join(HERE, "lll5.exe"), fin, ftg])
    os.remove(fin); os.remove(ftg)
    return [int(x) for x in out.split()]

def solve_all(a, t):
    """returns s list or None"""
    Ffinv = build_finv()
    results = [None] * len(COMPS)

    def work(ci):
        comp = COMPS[ci]
        m = comp.m
        ag = comp.fold(a, mod=True)
        # check invertible: gcd(a,g)=1 — ring mult by ag must be bijective; test via matrix rank cheap: try inverse of multmat? use sympy polyinv
        ainv = polyinv_modq_cached(ag, comp, ci)
        Bm = comp.multmat(ainv)
        ft = comp.fold(t, mod=True)
        Fv = comp.ringmul(ft, ainv)  # F = ft * ainv mod g
        rows = []
        for k in range(m):
            r = [0] * (2 * m); r[k] = 1
            for rr in range(m):
                r[m + rr] = Bm[rr][k]
            rows.append(r)
        for k in range(m):
            r = [0] * (2 * m); r[m + k] = Q
            rows.append(r)
        tgt = [0] * m + [centered(x) for x in Fv]
        diff = run_lll(ci, rows, tgt)
        efold = [centered(-x) for x in diff[:m]]
        sfold = [centered(x) for x in diff[m:]]
        results[ci] = (efold, sfold)
        # sfold should be residue of s mod g: verify smallness
        if max(abs(x) for x in efold + sfold) > 30:
            print(f"comp{ci}: LARGE max {max(abs(x) for x in efold+sfold)}", flush=True)

    with ThreadPoolExecutor(max_workers=5) as ex:
        list(ex.map(work, range(len(COMPS))))

    sfolds = [results[ci][1] for ci in range(len(COMPS))]
    efolds = [results[ci][0] for ci in range(len(COMPS))]
    flat = []
    for ci in range(len(COMPS)):
        flat += sfolds[ci]
    s = [sum(Ffinv[i][j] * flat[j] for j in range(N)) % Q for i in range(N)]
    sc = [centered(x) for x in s]
    if max(abs(x) for x in sc) > 1:
        print("s not ternary, max", max(abs(x) for x in sc), flush=True)
        return None
    e = [(t[i] - ms) % Q for i, ms in enumerate(mul420(a, sc))]
    ec = [centered(x) for x in e]
    if max(abs(x) for x in ec) > 1:
        print("e not ternary", flush=True)
        return None
    return sc, ec

_ainv_cache = {}
_pio_lock = threading.Lock()

def polyinv_modq_cached(ag, comp, ci):
    with _pio_lock:
        key = ci
        return polyinv_modq(ag, comp)

# ---- hash / encode ----
import hashlib

def polyhash_bytes(poly_vals):
    h = hashlib.sha256()
    for i in range(N):
        h.update((poly_vals[i] % Q).to_bytes(3, "big"))
    h.update(MSG)
    return h.digest()

def hash2poly(digest):
    val = int.from_bytes(digest, "big")
    c = [(val >> i) & 1 for i in range(256)]
    return c + [0] * (N - 256)

def poly_to_hex3(poly):
    return "".join((x % Q).to_bytes(3, "big").hex() for x in poly)

def make_forgery(a, t, s, e):
    # y1 = y2 = 0 => c = hash2poly(H(0...0 || m)); z1 = s*c; z2 = e*c
    c = hash2poly(polyhash_bytes([0] * N))
    z1 = mul420(s, c)
    z2 = mul420(e, c)
    z1c = [centered(x) for x in z1]
    z2c = [centered(x) for x in z2]
    # bounds
    for v in z1c + z2c:
        if abs(v) > B_ - W:
            print("FORGERY OUT OF BOUNDS", flush=True)
            return None
    # verify identity a*z1 + z2 - t*c == 0 (ring product)
    chk = mul420(a, [x % Q for x in z1c])
    tc = mul420(t, c)
    for i in range(N):
        if (chk[i] + (z2c[i] % Q) - tc[i]) % Q != 0:
            print("IDENTITY FAIL at", i, flush=True)
            return None
    return z1c, z2c, c

def selftest():
    random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    s = [random.choice((-1, 0, 1)) for _ in range(N)]
    e = [random.choice((-1, 0, 1)) for _ in range(N)]
    a = [random.randrange(Q) for _ in range(N)]
    t = mul420(a, s)
    t = [(t[i] + e[i]) % Q for i in range(N)]
    import time
    st = time.time()
    res = solve_all(a, t)
    print(f"time {time.time()-st:.1f}s", flush=True)
    if res is None:
        print("SELFTEST FAIL", flush=True)
        return 1
    sr, er = res
    print("s ok:", sr == s, "e ok:", er == e, flush=True)
    if sr != s:
        return 1
    z = make_forgery(a, t, sr, er)
    print("forgery:", "OK" if z else "FAIL", flush=True)
    if not z:
        return 1
    if not verify_server_side(a, t, z):
        print("SERVER-SIDE VERIFY FAILED", flush=True)
        return 1
    print("FULL LOCAL VERIFY PASS", flush=True)
    return 0

def verify_server_side(a, t, sig):
    # faithful port of server verify() incl. polyhash on centered ints
    z1, z2, c = sig
    z1 = [x % Q for x in z1]; z2 = [x % Q for x in z2]
    for i in range(N):
        if min(z1[i], Q - z1[i]) > B_ - W: return False
        if min(z2[i], Q - z2[i]) > B_ - W: return False
    tc = mul420(t, c)
    az = mul420(a, z1)
    d = [(az[i] + z2[i] - tc[i]) % Q for i in range(N)]
    dc = [centered(x) for x in d]
    import hashlib
    h = hashlib.sha256()
    for i in range(N):
        h.update(int(dc[i]).to_bytes(3, "big", signed=True))
    h.update(MSG)
    d2 = hash2poly(h.digest())
    return d2 == c

def live(host="archive.cryptohack.org", port=26931):
    import socket, time
    st = time.time()
    for attempt in range(3):
        try:
            sk = socket.create_connection((host, port), timeout=300)
            f = sk.makefile("rwb")
            def rdline():
                return f.readline().decode().strip()
            line1 = rdline(); line2 = rdline()
            a_hex = line1.split("=")[1].strip()
            t_hex = line2.split("=")[1].strip()
            print("got a,t", len(a_hex), len(t_hex), flush=True)
            a = [int(a_hex[i:i+6], 16) for i in range(0, len(a_hex), 6)]
            t = [int(t_hex[i:i+6], 16) for i in range(0, len(t_hex), 6)]
            res = solve_all(a, t)
            if res is None:
                print("attempt", attempt, "solve failed", flush=True)
                sk.close(); continue
            sr, er = res
            z = make_forgery(a, t, sr, er)
            if not z:
                sk.close(); continue
            z1, z2, c = z
            f.write((poly_to_hex3([x % Q for x in z1]) + "\n").encode())
            f.write((poly_to_hex3([x % Q for x in z2]) + "\n").encode())
            f.write((poly_to_hex3(c) + "\n").encode())
            f.flush()
            resp = ""
            try:
                while True:
                    ln = f.readline()
                    if not ln:
                        break
                    resp += ln.decode()
                    if "flag" in resp.lower():
                        break
            except Exception as ex2:
                print("read end", repr(ex2), flush=True)
            print("RESP:", resp, flush=True)
            sk.close()
            if "flag" in resp.lower() or "cryptohack" in resp.lower():
                open(os.path.join(HERE, "FLAG.txt"), "w").write(resp)
                return 0
            print(f"total {time.time()-st:.1f}s", flush=True)
        except Exception as ex:
            print("ERR", repr(ex), f"t={time.time()-st:.1f}s", flush=True)
    return 1

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        sys.exit(live())
    else:
        sys.exit(selftest())
