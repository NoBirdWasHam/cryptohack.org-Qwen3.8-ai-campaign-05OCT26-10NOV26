# Decrypt from candidate (f,g) rows exported by PARI (gprows.txt) or pasted rows.
# Each line: 1024 ints = [f | g]. Uses identity: lift(f*ct mod q) == 2*g*r + f*m
# exactly (coeffs < 127), so B = lift mod 2 = f*m over GF(2)[x]/(x^n-1); f unit.
import re, ast, sys

n, q = 512, 127
txt = open("output.txt").read()
pk = ast.literal_eval(re.search(r"pk = (\[.*?\])", txt).group(1))
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
    for c in range(n):  # circulant M[c,i] = f[(c-i) mod n]
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

def try_f(fvec, tag):
    s = 1 if sum(fvec) >= 0 else -1
    fpos = [s * c for c in fvec]
    if max(map(abs, fpos)) > 1:
        return None
    fc = cyclic_mul(fpos, ct)
    A = [x % q for x in fc]
    if s < 0: A = [(q - a) % q for a in A]
    B = [a & 1 for a in A]
    x = gf2_solve_unit(fpos, B)
    if x is None:
        print(tag, "singular f", flush=True); return None
    flag = x.to_bytes(n // 8, "big").lstrip(b"\x00")
    print(tag, "wt", sum(fpos), "->", flag[:90], flush=True)
    if flag.startswith(b"NNS{") and flag.endswith(b"}"):
        open("flag_origami-nns_ctf_20252025.txt", "w").write(flag.decode())
        print("FLAG:", flag.decode(), flush=True)
        sys.exit(0)
    return flag

src = sys.argv[1] if len(sys.argv) > 1 else "gprows.txt"
for ln in open(src):
    ints = [int(v) for v in ln.split()]
    if len(ints) != 1024:
        print("skip line len", len(ints)); continue
    if max(map(abs, ints)) > 1:
        print("row not small, norm²=", sum(v*v for v in ints), flush=True); continue
    try_f(ints[:n], "f-part")
    try_f(ints[n:], "g-part")
print("no flag yet")
