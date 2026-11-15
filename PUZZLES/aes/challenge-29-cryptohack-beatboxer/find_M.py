#!/usr/bin/env python3
"""beatboxer — build M (COLUMNS) + verified inverse.  E_key(P) = M.P ^ E_key(0).
  M.e_j (column j) is key-independent.  Store {"M": [M.e_0..M.e_127], "Minv": [Minv.e_0..]}.
  Apply:  f(x) = XOR of f_cols[j] for each set bit j of x.
"""
src = open("13406_provided.py").read()
ns = {}
exec(src[src.index("class AES"):src.index("class Challenge")], ns)
AES = ns["AES"]
import json, random

N = 128
def to_int(b): return int.from_bytes(b, "little")
def e_j(j):
    b = bytearray(16); b[j // 8] = 1 << (j % 8); return bytes(b)

def apply_cols(cols, x):
    y = 0
    for j in range(N):
        if x >> j & 1:
            y ^= cols[j]
    return y

# --- columns of M (zero key; key-independent) ---
a0 = AES(bytes(16))
E0 = to_int(a0.encrypt(bytes(16)))
cols = [to_int(a0.encrypt(e_j(j))) ^ E0 for j in range(N)]

# --- key-independence check ---
random.seed(3)
k2 = bytes(random.randrange(256) for _ in range(16))
a2 = AES(k2); E02 = to_int(a2.encrypt(bytes(16)))
kindep = all((to_int(a2.encrypt(e_j(j))) ^ E02) == cols[j] for j in range(N))
print("M columns key-independent:", kindep)

# --- invert M (GF(2)). Build rows from cols: row i bit j = (cols[j]>>i)&1 ---
rows = []
for i in range(N):
    r = 0
    for j in range(N):
        if cols[j] >> i & 1:
            r |= 1 << j
    rows.append(r)
def invert_rows(rows):
    aug = [rows[i] | (1 << (N + i)) for i in range(N)]
    for col in range(N):
        piv = None
        for r in range(col, N):
            if aug[r] >> col & 1:
                piv = r; break
        if piv is None:
            return None
        aug[col], aug[piv] = aug[piv], aug[col]
        for r in range(N):
            if r != col and (aug[r] >> col & 1):
                aug[r] ^= aug[col]
    return [x >> N & ((1 << N) - 1) for x in aug]
inv_rows = invert_rows(rows)
print("M invertible:", inv_rows is not None)
inv_cols = []
for j in range(N):
    c = 0
    for i in range(N):
        if inv_rows[i] >> j & 1:
            c |= 1 << i
    inv_cols.append(c)

good1 = all(apply_cols(cols, apply_cols(inv_cols, 1 << j)) == (1 << j) for j in range(N))
good2 = all(apply_cols(inv_cols, apply_cols(cols, 1 << j)) == (1 << j) for j in range(N))
print("M . Minv = I :", good1)
print("Minv . M = I :", good2)
random.seed(1)
r = random.getrandbits(N)
print("roundtrip M(Minv(x))==x :", apply_cols(cols, apply_cols(inv_cols, r)) == r)
for tag, a, e0 in [("zero", a0, E0), ("key2", a2, E02)]:
    ok2 = True
    for _ in range(5):
        P = bytes(random.randrange(256) for _ in range(16))
        if to_int(a.encrypt(P)) != (apply_cols(cols, to_int(P)) ^ e0):
            ok2 = False
    print("E(P)==M.P^E0 (%s):" % tag, ok2)

json.dump({"M": cols, "Minv": inv_cols}, open("M_matrix.json", "w"))
print("saved M_matrix.json (columns representation)")
