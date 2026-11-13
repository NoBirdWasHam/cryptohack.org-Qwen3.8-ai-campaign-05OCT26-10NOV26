# t280_fold.py — ORIGAMI structural attack: idempotent fold of Z_127[x]/(x^512-1)
# = R+ x R- via (x^256-1)(x^256+1). Two dim-512 lattices M± contain folded
# planted (f±,g±). Recover, align-glue back to (f,g), parity-decrypt (p=2 no-wrap).
import numpy as np, ast, re, sys, json, time

def ringmul(a, b, m, eps):
    # (a*b) in Z[y]/(y^m - eps), eps=+1 or -1; wrap term scaled by eps
    a = np.asarray(a, dtype=np.int64); b = np.asarray(b, dtype=np.int64)
    out = np.zeros(m, dtype=np.int64)
    for i in range(m):
        if a[i]:
            j = np.arange(m)
            k = i + j
            out[k % m] += (np.where(k >= m, eps, 1)) * a[i] * b[j]
    return out

def conv512(a, b, n=512):  # plain cyclic (for ct/decrypt)
    a = np.asarray(a, dtype=np.int64); b = np.asarray(b, dtype=np.int64)
    out = np.zeros(n, dtype=np.int64)
    for i in range(n):
        if a[i]:
            j = np.arange(n)
            out[(i + j) % n] += a[i] * b[j]
    return out

def build_lattice(hf, m, q, eps):
    # dim 2m: rows (e_i | T[:,i]) for i<m ; (0 | q e_j). T[k,i] = epswrap*h[(k-i)%m]
    M = np.zeros((2 * m, 2 * m), dtype=np.int64)
    for i in range(m):
        M[i, i] = 1
        for k in range(m):
            M[i, m + k] = (eps if k < i else 1) * hf[(k - i) % m]
    for j in range(m):
        M[m + j, m + j] = q
    return M

def member(v, hf, m, q, eps):
    u = np.asarray(v[:m], dtype=np.int64) % q
    w = np.asarray(v[m:], dtype=np.int64) % q
    return bool(np.all((ringmul(u, hf, m, eps) - w) % q == 0))

def rotate(v, k, m):
    return np.roll(np.asarray(v, dtype=np.int64), k)  # x^k * v in y^m ± 1 ring

# ---------------- decrypt (scan_cli convention) ----------------
def gf2_solve_unit(fbits, B, n):
    rows = []
    for c in range(n):
        bits = 0
        for i in range(n):
            if fbits[(c - i) % n] & 1: bits |= 1 << i
        rows.append([bits, B[c] & 1])
    piv = {}
    for r in rows:
        while r[0]:
            col = (r[0] & -r[0]).bit_length() - 1
            if col in piv:
                r[0] ^= piv[col][0]; r[1] ^= piv[col][1]
            else:
                piv[col] = r; break
        if not r[0] and r[1]: return None
    x = 0
    for col in range(n - 1, -1, -1):
        if col not in piv: continue
        bits, t = piv[col]
        v = t
        rest = bits & ~(1 << col)
        while rest:
            c2 = (rest & -rest).bit_length() - 1
            v ^= (x >> c2) & 1
            rest &= rest - 1
        if v: x |= 1 << col
    return x

def try_f(fvec, ct, q, n):
    fvec = list(int(x) for x in fvec)
    if max(map(abs, fvec)) > 1: return None
    if sum(abs(c) for c in fvec) % 2 == 0: return None
    fc = conv512(fvec, [int(x) % q for x in ct], n)
    A = [x % q for x in fc]
    B = [a & 1 for a in A]
    x = gf2_solve_unit(fvec, B, n)
    if x is None: return None
    return x.to_bytes(n // 8, "big").lstrip(b"\x00")

def glue_and_decrypt(fp, fm, h, ct, m=256, q=127, n=512, log=print):
    # fp: recovered + part (rotation/± of f+), fm: - part. Try alignments.
    cands = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            P = s1 * np.asarray(fp, dtype=np.int64)
            Mn = s2 * np.asarray(fm, dtype=np.int64)
            supP = (P == 1)
            if Mn[np.abs(Mn) > 1].size: pass
            for k in range(m):
                Pk = rotate(P, k, m)
                sP = (Pk == 1)
                zP = (Pk != 1)
                for l in range(m):
                    Ml = rotate(Mn, l, m)
                    if np.any(Ml[zP] != 0) or np.any(Ml[sP] == 0) or np.any(np.abs(Ml[sP]) != 1):
                        continue
                    a = (Pk + Ml) // 2; b = (Pk - Ml) // 2
                    if np.any((a < 0) | (a > 1)) or np.any((b < 0) | (b > 1)): continue
                    cands.append((k, l, s1, s2, a.copy(), b.copy()))
    log(f"glue: {len(cands)} alignment candidates")
    nshown = 0
    for (k, l, s1, s2, a, b) in cands:
        f = np.concatenate([a, b])
        g = conv512(f, h, n) % q
        if g.max() <= 1 and g.sum() == f.sum():
            flag = try_f(f, ct, q, n)
            if flag and flag.startswith(b"NNS{") and flag.endswith(b"}"):
                log(f"  cand k={k} l={l} signs=({s1},{s2}): FLAG", flag)
                return f, g, flag
            if flag is not None and nshown < 3:
                log(f"  cand k={k} l={l}: decrypts but not NNS-format:", flag[:60]); nshown += 1
        else:
            if nshown < 3:
                log(f"  cand k={k} l={l}: f pattern ok but h*f!=g"); nshown += 1
    return None, None, None

def load_real(dir_="."):
    txt = open(dir_ + "/output.txt").read()
    pk = ast.literal_eval(re.search(r"pk = (\[.*?\])", txt).group(1))
    ct = ast.literal_eval(re.search(r"ct = (\[.*?\])", txt).group(1))
    return [int(x) for x in pk], [int(x) for x in ct]

def make_folds(h, n=512, q=127):
    m = n // 2
    h0 = np.array(h[:m], dtype=np.int64); h1 = np.array(h[m:], dtype=np.int64)
    hp = (h0 + h1) % q      # ring y^m - 1
    hm = (h0 - h1) % q      # ring y^m + 1
    return hp, hm

if __name__ == "__main__":
    h, ct = load_real()
    hp, hm = make_folds(h)
    # sanity: the fold maps must be ring homomorphisms: plant a fake f, check
    rng = np.random.default_rng(1)
    for trial in range(3):
        fv = np.zeros(512, dtype=np.int64); idx = rng.choice(512, 35, replace=False); fv[idx] = 1
        gv = conv512(fv, h) % 127
        f0 = fv[:256]; f1 = fv[256:]
        g0 = gv[:256]; g1 = gv[256:]
        ok_p = np.all((ringmul(f0 + f1, hp, 256, +1) - (g0 + g1)) % 127 == 0)
        ok_m = np.all((ringmul(f0 - f1, hm, 256, -1) - (g0 - g1)) % 127 == 0)
        print(f"homomorphism check {trial}: plus={ok_p} minus={ok_m}")
    print("h_plus sample:", hp[:8].tolist(), " h_minus sample:", hm[:8].tolist())
    print("wt h_plus nonzero:", int((hp != 0).sum()), "sum:", int(hp.sum()))
