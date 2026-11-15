# Origami (NNS CTF 2025): NTRU n=512 p=2 q=127 df=dg=35 dr=22
# Attack: BKZ the 1024-dim NTRU lattice {(a,b): b = a*h mod q}; secret (f,g)
# has norm ~8.4 vs Gaussian heuristic ~87 -> recovered directly.
# Decrypt: f*c mod q lifts EXACTLY to 2*g*r + f*m (coeffs <= 44+35=79 < 127),
# so B = (f*c mod q) mod 2 = f*m over GF(2)[x]/(x^n-1); f has odd weight -> unit.
import re, ast, sys
from fpylll import IntegerMatrix, BKZ

n, p, q = 512, 2, 127
txt = open("output.txt").read()
pk = ast.literal_eval(re.search(r"pk = (\[.*?\])", txt).group(1))
ct = ast.literal_eval(re.search(r"ct = (\[.*?\])", txt).group(1))

def rot(h, i):
    return [h[(k - i) % n] for k in range(n)]

d = 2 * n
M = IntegerMatrix(d, d)
for i in range(n):
    row = rot(pk, i)
    for j in range(n):
        M[i, j] = 1 if i == j else 0
        M[i, n + j] = row[j]
        M[n + i, n + j] = q if i == j else 0

print("BKZ start", flush=True)
BKZ.reduction(M, BKZ.EasyParam(40))
print("BKZ done", flush=True)

def cyclic_mul(a, b):
    out = [0] * n
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    out[(i + j) % n] += ai * bj
    return out

def gf2_solve_unit(fbits, B):
    # solve circulant(fbits) * m = B over GF(2) (matrix symmetric), bitmask elim
    rows = []
    for c in range(n):  # row c of circulant M: M[c,i] = f[(c-i) mod n]
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

seen = set()
for i in range(d):
    v = [M[i, j] for j in range(d)]
    if max(map(abs, v)) > 1: continue
    fvec = v[:n]
    s = 1 if sum(fvec) >= 0 else -1
    fpos = [s * c for c in fvec]
    key = tuple(fpos)
    if key in seen: continue
    seen.add(key)
    fc = cyclic_mul(fpos, ct)
    A = [x % q for x in fc]
    if s < 0: A = [(q - a) % q for a in A]
    B = [a & 1 for a in A]
    x = gf2_solve_unit(fpos, B)
    if x is None:
        print("row", i, "singular f", flush=True); continue
    mb = bytearray()
    for b in range(0, n, 8):
        byte = 0
        for k in range(8):
            byte |= ((x >> (b + k)) & 1) << k
        mb.append(byte)
    flag = mb.rstrip(b"\x00")
    print("row", i, "wt", sum(1 for c in fpos if c), "->", flag[:80], flush=True)
    if flag.startswith(b"NNS{") and flag.endswith(b"}"):
        open("flag_origami-nns_ctf_20252025.txt", "w").write(flag.decode())
        print("FLAG:", flag.decode(), flush=True)
        sys.exit(0)
print("no flag from candidates")
