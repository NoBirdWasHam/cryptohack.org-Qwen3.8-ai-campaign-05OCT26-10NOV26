# toy end-to-end check of the EXACT scan_cli decrypt math on n=64 planted data
import json, sys
truth = json.load(open("toy64_truth.json"))
n, q, p = 64, 127, 2
f, g = truth["f"], truth["g"]

def cm(a, b, nn=n, qq=q):
    o = [0]*nn
    nz = [(j, bj) for j, bj in enumerate(b) if bj]
    for i, ai in enumerate(a):
        if ai:
            for j, bj in nz: o[(i+j) % nn] += ai*bj
    return [x % qq for x in o]

def gf2_solve_unit(fbits, B):
    rows = []
    for c in range(n):
        bits = 0
        for i in range(n):
            if fbits[(c-i) % n] & 1: bits |= 1 << i
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
    for col in range(n-1, -1, -1):
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

msg = b"NNS{toy}"
def encode(val, nn=n):
    poly = [0]*nn
    for i in range(nn):
        poly[i] = val & 1
        val >>= 1
    return poly
val = int.from_bytes(msg, "big")
m = encode(val)
import random
rng = random.Random(7)
r = [0]*n
for i in rng.sample(range(n), 22): r[i] = 1
h = truth["h"] if "h" in truth else None
if h is None:
    # h = g/f mod q: solve T(f) h = g mod q
    import itertools
    T = [[f[(c-i) % n] for i in range(n)] for c in range(n)]
    # gaussian elim mod q
    M = [row[:] + [g[c]] for c, row in enumerate(T)]
    piv = []
    row_i = 0
    for col in range(n):
        sel = None
        for rr in range(row_i, n):
            if M[rr][col] % q: sel = rr; break
        if sel is None: continue
        M[row_i], M[sel] = M[sel], M[row_i]
        inv = pow(M[row_i][col], -1, q)
        M[row_i] = [x*inv % q for x in M[row_i]]
        for rr in range(n):
            if rr != row_i and M[rr][col]:
                fac = M[rr][col]
                M[rr] = [(a - fac*b) % q for a, b in zip(M[rr], M[row_i])]
        row_i += 1
    h = [M[i][n] for i in range(n)]
# ct = p*h*r + m mod q
hr = cm(h, r)
ct = [(p*x + y) % q for x, y in zip(hr, m)]
# decrypt exactly as scan_cli try_f
A = cm(f, ct)
B = [a & 1 for a in A]
x = gf2_solve_unit([abs(c) & 1 for c in f], B)
rec = x.to_bytes(n//8, "big").lstrip(b"\x00")
print("toy ct:", sum(ct) % 997, "recovered:", rec)
print("TOY DECRYPT MATCH:", rec == msg)
