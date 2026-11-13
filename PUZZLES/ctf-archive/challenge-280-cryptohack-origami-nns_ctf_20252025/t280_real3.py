# t280_real3.py — build REAL level-3 fold lattices M+++ (x^64-1) and M++- (x^64+1)
# from the real pk, LLL-seed, then (via --scan) relaxed-scan + glue to f++,g++.
import sys, re, json, time
sys.path.insert(0, ".")
import numpy as np
from t280_fold import load_real, build_lattice, ringmul, member, make_folds

q = 127; m3 = 64
h, ct = load_real()
h = np.array(h, dtype=np.int64)
hp = (h[:256] + h[256:]) % q
hpp = (hp[:128] + hp[128:]) % q
hpm = (hp[:128] - hp[128:]) % q
hppp = (hpp[:m3] + hpp[m3:]) % q   # ring y^64-1
hppm = (hpp[:m3] - hpp[m3:]) % q   # ring y^64+1

def centered(v):
    w = np.array(v, dtype=np.int64) % q
    return w - q * (w > 63)

if sys.argv[1:2] == ["mk"]:
    from fpylll import IntegerMatrix
    from fpylll.fplll.lll import lll_reduction
    def to_intmat(M):
        d = M.shape[0]; B = IntegerMatrix(d, d)
        for i in range(d):
            for j in range(d): B[i, j] = int(M[i, j])
        return B
    def write_fplll(B, path):
        with open(path, "w") as fp:
            fp.write("[")
            for i in range(B.nrows):
                fp.write("[ " + " ".join(str(int(B[i, j])) for j in range(B.ncols)) + " ]")
            fp.write(" ]\n")
    for name, hf, eps in (("r3ppp", hppp, +1), ("r3ppm", hppm, -1)):
        Lat = build_lattice(hf, m3, q, eps)
        B = to_intmat(Lat)
        t1 = time.time(); lll_reduction(B)
        mn = min(sum(int(B[i, j])**2 for j in range(B.ncols)) for i in range(B.nrows))
        write_fplll(B, f"t280_{name}.fplll")
        print(name, f"LLL {time.time()-t1:.1f}s minnorm2 {mn}", flush=True)
    print("REAL3_MK DONE")
    sys.exit(0)

def parse(path):
    rows = [[int(t) for t in ch.split()] for ch in re.findall(r"\[([^\[\]]+)\]", open(path).read()) if ch.split()]
    return np.array(rows, dtype=np.int64)

def scan_plus(rows, hf, mm, maxc):
    out = []
    for v in rows:
        if int(v @ v) > 300: continue
        u, w = v[:mm], v[mm:]
        for s in (1, -1):
            uu, ww = s * u, s * w
            if uu.min() >= 0 and uu.max() <= maxc and ww.min() >= 0 and ww.max() <= maxc \
               and int(uu.sum()) == 35 and int(ww.sum()) == 35 and member(s * v, hf, mm, q, +1):
                out.append((uu, ww))
    return out

def scan_minus(rows, hf, mm, maxc):
    out = []
    for v in rows:
        if int(v @ v) > 300: continue
        u, w = v[:mm], v[mm:]
        for s in (1, -1):
            uu, ww = s * u, s * w
            if np.abs(uu).max() <= maxc and np.abs(ww).max() <= maxc \
               and 20 <= int(np.abs(uu).sum()) <= 35 and 20 <= int(np.abs(ww).sum()) <= 35 \
               and member(s * v, hf, mm, q, -1):
                out.append((uu, ww))
    return out

pp, pm = parse("t280_r3ppp.fplll"), parse("t280_r3ppm.fplll")
st = {}
for nm, R in (("r3ppp", pp), ("r3ppm", pm)):
    nr = np.array([int(r @ r) for r in R])
    st[nm] = {"min": int(nr.min()), "subq": int((nr < 16129).sum()), "le300": int((nr <= 300).sum())}
cpp = scan_plus(pp, hppp, m3, 9)
cpm = scan_minus(pm, hppm, m3, 9)
print(json.dumps({"stats": st, "cands_ppp": len(cpp), "cands_ppm": len(cpm)}), flush=True)
def bits64(v):
    return int(sum((int(x) & 1) << i for i, x in enumerate(v)))
def rol64(x, k):
    k %= 64
    return ((x << k) | (x >> (64 - k))) & ((1 << 64) - 1) if k else x

def glue_L3(cpp, cpm, limit=6):
    found = []
    for (a, ag) in cpp[:20]:
        abits = bits64(a); agbits = bits64(ag)
        for (b0, bg0) in cpm[:40]:
            bbits0 = bits64(b0); bgbits0 = bits64(bg0)
            for s2 in (1, -1):
                for l in range(m3):
                    lb = rol64(bbits0, -l); lg = rol64(bgbits0, -l)
                    for k in range(m3):
                        if rol64(abits, -k) != lb or rol64(agbits, -k) != lg: continue
                        ak = np.roll(a, -k); agk = np.roll(ag, -k)
                        bl = np.roll(b0, -l) * s2; bg = np.roll(bg0, -l) * s2
                        Sf, Df = ak + bl, ak - bl
                        if np.any(Sf % 2) or np.any(Df % 2): continue
                        Sg, Dg = agk + bg, agk - bg
                        if np.any(Sg % 2) or np.any(Dg % 2): continue
                        F0, F1 = Sf // 2, Df // 2
                        G0, G1 = Sg // 2, Dg // 2
                        if F0.min() < 0 or F0.max() > 4 or F1.min() < 0 or F1.max() > 4: continue
                        if G0.min() < 0 or G0.max() > 4 or G1.min() < 0 or G1.max() > 4: continue
                        if int(F0.sum()) + int(F1.sum()) != 35 or int(G0.sum()) + int(G1.sum()) != 35: continue
                        fpp_ = np.concatenate([F0, F1]); gpp_ = np.concatenate([G0, G1])
                        if not np.all(ringmul(fpp_, hpp, 128, +1) % q == gpp_ % q): continue
                        found.append((k, l, s2, fpp_, gpp_))
                        if len(found) > 200: return found
    return found

found = glue_L3(cpp, cpm)
print("GLUE-VALID f++ count:", len(found), flush=True)
seen = set()
uniq = []
for (k, l, s2, fpp_, gpp_) in found:
    key = tuple(fpp_.tolist())
    if key in seen: continue
    seen.add(key); uniq.append((k, l, s2, fpp_, gpp_))
print("unique f++ candidates:", len(uniq), flush=True)
for (k, l, s2, fpp_, gpp_) in uniq[:5]:
    print("f++ cdist:", np.bincount(fpp_).tolist(), " k,l,s:", k, l, s2, flush=True)
if uniq:
    with open("REAL_FPP_RECOVERED.txt", "w") as fp:
        for (k, l, s2, fpp_, gpp_) in uniq:
            fp.write(f"{k},{l},{s2}," + ",".join(map(str, fpp_.tolist())) + "|" + ",".join(map(str, gpp_.tolist())) + "\n")
    print("wrote REAL_FPP_RECOVERED.txt", flush=True)
print("REAL3_SCAN DONE", flush=True)
