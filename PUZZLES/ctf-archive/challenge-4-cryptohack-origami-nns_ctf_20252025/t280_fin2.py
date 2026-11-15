# t280_fin2.py — deterministic finisher.
# Needs: real f++/g++ (REAL_FPP_RECOVERED.txt from L3 glue) + reduced real level-2
# MINUS lattice (ring x^128+1) whose relaxed-scan yields (f+-, g+-) row candidates.
# Then: F256 = f mod x^256-1, G256 = g mod x^256-1 (pair sums known); residual is
# 35 split bits sigma in {+-1}; g-pair-sum gives 256 linear equations mod 127 ->
# unique sigma -> verify f*h == g binary -> decrypt via try_f.
import sys, re, json, time
sys.path.insert(0, ".")
import numpy as np
from t280_fold import load_real, ringmul, member, try_f

q = 127; n = 512; m2 = 128
INV2 = 64
h, ct = load_real(); h = np.array(h, dtype=np.int64)
hp = (h[:256] + h[256:]) % q
hpm = (hp[:128] - hp[128:]) % q

def parse(p):
    rows = [[int(t) for t in c.split()] for c in re.findall(r"\[([^\[\]]+)\]", open(p).read()) if c.split()]
    return np.array(rows, dtype=np.int64)

def scan_Bw(rows):
    out = []
    for v in rows:
        if int(v @ v) > 340: continue
        u, w = v[:m2], v[m2:]
        for s in (1, -1):
            uu, ww = s * u, s * w
            if np.abs(uu).max() <= 2 and np.abs(ww).max() <= 2 \
               and 16 <= int(np.abs(uu).sum()) <= 36 and 16 <= int(np.abs(ww).sum()) <= 36 \
               and member(s * v, hpm, m2, q, -1):
                out.append((uu, ww))
    return out

def load_fpp():
    seen = set(); cands = []
    for line in open("REAL_FPP_RECOVERED.txt"):
        a, b = line.strip().split("|")
        p = a.split(",")
        fpp = np.array([int(x) for x in p[3:]], dtype=np.int64)
        gpp = np.array([int(x) for x in b.split(",")], dtype=np.int64)
        key = np.roll(fpp, -int(fpp.argmin())).tobytes()
        if key in seen: continue
        seen.add(key); cands.append((fpp, gpp))
    return cands

def skewrot(B, k):
    r = B.copy()
    for _ in range(k % m2):
        r = np.concatenate([[-r[-1]], r[:-1]])
    return r

def solve_sigma(F, G):
    # F,G in {0,1,2}^256 pair-sums (f,g mod x^256-1). slots: F==1 (a=j,b=j+256).
    # sigma in {+-1} per slot. Use PAIR DIFFERENCES (x^256+1 quotient):
    #   g_k - g_{k+256} = (gb_k - gb_{k+256}) + sum_j (sig_j+1) w_j[k],  mod 127
    # with w_j = (roll(h,j) - roll(h,j+256))[:256]. Rows with G_k in {0,2} force
    # diff=0 (fixed rhs); rows G_k==1 must give +-1.
    slots = np.flatnonzero(F == 1)
    base = np.zeros(n, dtype=np.int64)
    for j in range(256):
        if int(F[j]) >= 1: base[j + 256] = 1
        if int(F[j]) == 2: base[j] = 1
    gb = ringmul(base, h, n, +1) % q
    L = len(slots)
    if L == 0 or L > 40: return None, L
    W = np.zeros((256, L), dtype=np.int64)
    for jj, j in enumerate(slots):
        W[:, jj] = (np.roll(h, j) - np.roll(h, j + 256))[:256] % q
    gbd = (gb[:256] - gb[256:]) % q
    Wsum = W.sum(axis=1) % q
    free = (G == 1)
    rows = np.flatnonzero(~free)
    rhs = (-gbd - Wsum) % q            # diff must be 0 on fixed rows
    M = np.concatenate([W[rows], rhs[rows, None]], axis=1) % q
    nr = M.shape[0]
    piv_cols = []; r = 0
    for col in range(L):
        piv = None
        for rr in range(r, nr):
            if M[rr, col] % q: piv = rr; break
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]
        inv = pow(int(M[r, col]), q - 2, q)
        M[r] = M[r] * inv % q
        for rr in range(nr):
            if rr != r and M[rr, col] % q:
                M[rr] = (M[rr] - M[rr, col] * M[r]) % q
        piv_cols.append(col); r += 1
        if r == nr: break
    for rr in range(r, nr):
        if M[rr, L] % q: return None, L
    d = L - len(piv_cols)
    if d > 6: return None, L
    piv_cols = list(piv_cols)
    free_cols = [c for c in range(L) if c not in piv_cols]
    p0 = np.zeros(L, dtype=np.int64)
    for i, col in enumerate(piv_cols): p0[col] = int(M[i, L]) % q
    ker = []
    for fc in free_cols:
        nv = np.zeros(L, dtype=np.int64)
        nv[fc] = 1
        for i, col in enumerate(piv_cols):
            nv[col] = (-int(M[i, fc])) % q
        ker.append(nv)
    import itertools
    sols = []
    for signs in itertools.product((1, q - 1), repeat=d):
        sig = p0.copy()
        for m, t in enumerate(signs):
            sig = (sig + (t - p0[free_cols[m]]) * ker[m]) % q
        # NOTE: free coord m of ker[m] is 1, others 0 => sig[fc]=t exactly
        if not np.all((sig == 1) | (sig == q - 1)): continue
        pred = (W @ sig + Wsum + gbd) % q
        if not np.all((pred[free] == 1) | (pred[free] == q - 1)): continue
        f = base.copy()
        for jj, j in enumerate(slots):
            if sig[jj] == 1:
                f[j] = 1; f[j + 256] = 0
        if not any(np.array_equal(f, s2) for s2 in sols): sols.append(f)
    return sols, L

def pilot_mode():
    T = json.load(open("t280_ctl_truth.json"))
    hh = np.array(T["h"], dtype=np.int64)
    A = np.array(T["fpp"], dtype=np.int64)[:128]
    Bc = np.array(T["fpm"], dtype=np.int64)[:128]; Bc = np.where(Bc > 63, Bc - 127, Bc)
    gA = np.array(T["gpp"], dtype=np.int64)[:128]
    gB = np.array(T["gpm"], dtype=np.int64)[:128]; gB = np.where(gB > 63, gB - 127, gB)
    hits = complete_pair(A, Bc)
    print("pilot F-completions:", len(hits))
    for (s, k, F) in hits[:4]:
        # g side uses the SAME (s,k) transform (same scan row / same secret rotation)
        gBr = skewrot(s * gB, k)
        if np.any((gA + gBr) % 2) or np.any((gA - gBr) % 2):
            print("  g parity fail"); continue
        G = np.concatenate([(gA + gBr) // 2, (gA - gBr) // 2])
        if int(G.sum()) != 35 or G.min() < 0 or G.max() > 2:
            print("  G range/weight fail"); continue
        f_, L = solve_sigma_global(F, G, hh)
        sols = f_ if isinstance(f_, list) else ([] if f_ is None else [f_])
        print(f"  solve_sigma slots={L} -> {len(sols)} sols")
        f_true_np = np.array(T['f'], dtype=np.int64)
        for fv in sols:
            g_ = ringmul_g(fv, hh)
            txt = try_f(fv, np.array(T["ct"], dtype=np.int64), q, n)
            print("  matches planted:", bool(np.array_equal(fv, f_true_np)),
                  "g-binary:", int(g_.max()) <= 1 and int(g_.sum()) == 35,
                  "toy-decrypt:", txt)

def ringmul_g(fv, hh):
    return np.array([sum(int(fv[j]) * int(hh[(k - j) % n]) for j in range(n) if fv[j]) % q for k in range(n)], dtype=np.int64)

def solve_sigma_global(F, G, hh):
    global h
    oldh, ring_h = h, None
    h = hh
    f_, L = solve_sigma(F, G)
    h = oldh
    return f_, L

def complete_pair(A, B):
    hits = []
    for s in (1, -1):
        Bs = s * B
        for k in range(m2):
            Br = skewrot(Bs, k)
            if np.any((A + Br) % 2) or np.any((A - Br) % 2): continue
            u = (A + Br) // 2; v = (A - Br) // 2
            if np.any(u < 0) or np.any(u > 2) or np.any(v < 0) or np.any(v > 2): continue
            F = np.concatenate([u, v])
            if int(F.sum()) != 35: continue
            hits.append((s, k, F))
    return hits

if __name__ == "__main__":
    if sys.argv[1:2] == ["pilot"]:
        pilot_mode(); sys.exit(0)
    path = sys.argv[1] if len(sys.argv) > 1 else "t280_fpm_h.cur.fplll"
    R = parse(path)
    cands = scan_Bw(R)
    print(json.dumps({"file": path, "Bw_cands": len(cands)}), flush=True)
    fpps = load_fpp()
    print("f++ canonicals:", len(fpps), flush=True)
    done = False
    for bi, (B, gB) in enumerate(cands):
        for ai, (A, gA) in enumerate(fpps):
            hits = complete_pair(A, B)
            for (s, k, F) in hits:
                gBr = skewrot(s * gB, k)
                if np.any((gA + gBr) % 2) or np.any((gA - gBr) % 2): continue
                G = np.concatenate([(gA + gBr) // 2, (gA - gBr) // 2])
                if int(G.sum()) != 35 or G.min() < 0 or G.max() > 2: continue
                f_, L = solve_sigma(F, G)
                if not f_:
                    print(f"pair B{bi}xA{ai} s{k}: sigma no (slots {L})", flush=True); continue
                for fsol in f_:
                    g_ = ringmul(fsol, h, n, +1) % q
                    ok = bool(g_.max() <= 1 and int(g_.sum()) == 35)
                    print(f"pair B{bi}xA{ai}: SIGMA-FOUND slots={L} g-binary={ok}", flush=True)
                    if not ok: continue
                    txt = try_f(fsol, ct, q, n)
                    np.save("t280_valid_f.npy", fsol)
                    if txt:
                        print("FLAG-CANDIDATE:", txt, flush=True)
                        open("FLAG_FOUND.txt", "wb").write(bytes(txt))
                        done = True
                    else:
                        print("valid f, decrypt no NNS hit", flush=True)
        if done or bi >= 20: break
    print("FIN2 DONE", flush=True)
