# BKZ-30 on 1024-dim NTRU lattice, then parity decryption of every {0,+-1} row.
import re, ast, sys, time
from fpylll import IntegerMatrix, BKZ

import threading
def main():
    global n, q, t0
    n, q = 512, 127
    t0 = time.time()
    txt = open("output.txt").read()
    pk = ast.literal_eval(re.search(r"pk = (\[.*?\])", txt).group(1))
    ct = ast.literal_eval(re.search(r"ct = (\[.*?\])", txt).group(1))

    d = 2 * n
    M = IntegerMatrix(d, d)
    for i in range(n):
        for j in range(n):
            M[i, j] = 1 if i == j else 0
            M[i, n + j] = pk[(j - i) % n]
            M[n + i, n + j] = q if i == j else 0
    print("built", round(time.time() - t0), flush=True)

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
        if sum(abs(c) for c in fvec) + 2 * sum(abs(c) for c in gvec) >= q: return False
        if sum(1 for c in fvec if c) % 2 == 0: return False
        fc = cyclic_mul(fvec, ct)
        A = [x % q for x in fc]
        B = [a & 1 for a in A]
        x = gf2_solve_unit([abs(c) & 1 for c in fvec], B)
        if x is None: return False
        flag = x.to_bytes(n // 8, "big").lstrip(b"\x00")
        print(tag, "->", flag[:90], flush=True)
        if flag.startswith(b"NNS{") and flag.endswith(b"}"):
            open("flag_origami-nns_ctf_20252025.txt", "w").write(flag.decode())
            print("FLAG:", flag.decode(), flush=True)
            sys.exit(0)
        return False

    def scan(tag):
        for i in range(d):
            v = [M[i, j] for j in range(d)]
            if max(map(abs, v)) > 1: continue
            s1 = sum(1 for c in v if c)
            if s1 > 90: continue
            try_f(v[:n], v[n:], tag + " row" + str(i))
        print(tag + " scan done", round(time.time() - t0), flush=True)

    for k in (25, 30, 40):
        BKZ.reduction(M, BKZ.EasyParam(k))
        print("BKZ", k, "done", round(time.time() - t0), flush=True)
        scan("k" + str(k))
    print("no flag yet")

threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=main)
th.start()
th.join()
print("main thread exited", flush=True)
