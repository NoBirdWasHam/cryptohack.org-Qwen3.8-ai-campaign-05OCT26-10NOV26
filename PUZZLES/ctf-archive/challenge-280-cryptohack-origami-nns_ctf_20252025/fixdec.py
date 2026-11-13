# Parse "SMALL col ... f-part | g-part END" dumps from gp2.log and decrypt each.
import re, ast, sys

n, q = 512, 127
txt = open("output.txt").read()
ct = ast.literal_eval(re.search(r"ct = (\[.*?\])", txt).group(1))

def cyclic_mul(a, b):
    out = [0] * n
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    out[(i + j) % n] += ai * bj
    return out

def gf2_solve_unit(fbits, B):
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
        if not r[0] and r[1]:
            return None
    x = 0
    for col in range(n - 1, -1, -1):
        if col not in piv: continue
        bits, t = piv[col]
        val = t
        rest = bits & ~(1 << col)
        while rest:
            c = (rest & -rest).bit_length() - 1
            val ^= (x >> c) & 1
            rest &= rest - 1
        if val: x |= 1 << col
    return x

def try_f(fvec, gvec, tag):
    if sum(abs(c) for c in fvec) + 2 * sum(abs(c) for c in gvec) >= q:
        print(tag, "wrap risk, skip"); return False
    if sum(1 for c in fvec if c) % 2 == 0:
        print(tag, "even weight f, non-unit mod2, skip"); return False
    fc = cyclic_mul(fvec, ct)
    A = [x % q for x in fc]
    B = [a & 1 for a in A]
    fbits = [abs(c) & 1 for c in fvec]
    x = gf2_solve_unit(fbits, B)
    if x is None:
        print(tag, "singular"); return False
    flag = x.to_bytes(n // 8, "big").lstrip(b"\x00")
    print(tag, "->", flag[:90], flush=True)
    if flag.startswith(b"NNS{") and flag.endswith(b"}"):
        open("flag_origami-nns_ctf_20252025.txt", "w").write(flag.decode())
        print("FLAG:", flag.decode(), flush=True)
        return True
    return False

found = False
data = open("solo8.log", errors="ignore").read()
for m in re.finditer(r"SMALL col (\d+) norm2=(\d+) wf=(\d+) wg=(\d+) (\S[^|]*)\| ([^ ]+) END", data):
    i, s, wf, wg, fp, gp_ = m.groups()
    fvec = [int(v) for v in fp.split()]
    gvec = [int(v) for v in gp_.split()]
    if len(fvec) != n or len(gvec) != n:
        print("bad len"); continue
    for tag, fv, gv in (("f-part", fvec, gvec), ("g-as-f", gvec, fvec)):
        if try_f(fv, gv, f"col{i} {tag} wf={wf} wg={wg}"):
            found = True
if not found:
    print("no flag from columns")
