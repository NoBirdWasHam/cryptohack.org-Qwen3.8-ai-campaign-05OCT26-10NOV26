# Diagnose why the c-scan yields nothing: x_true known, check every a in [val, 2^128)
# with these digits for structural signal (hex-strict vs fully-printable).
from ast import literal_eval
import json
from Crypto.Util.Padding import pad
from fpylll import IntegerMatrix
from fpylll.algorithms.bkz2 import BKZReduction
from fpylll import BKZ as BKZParams

A = literal_eval(open("u-turn/A.txt").read())
h = bytes.fromhex(open("u-turn/output.txt").read().strip())
k, l = 48, 50
xp = json.load(open("xp.json"))
P = 5 ** l
cs = [-2, -1, 0, 1, 2]

def f2_basis_of_kernel(Mx, ncols):
    M2 = [row[:] for row in Mx]
    pv = {}
    r = 0
    for col in range(ncols):
        sel = next((i for i in range(r, len(M2)) if M2[i][col]), -1)
        if sel < 0:
            continue
        M2[r], M2[sel] = M2[sel], M2[r]
        for i in range(len(M2)):
            if i != r and M2[i][col]:
                M2[i] = [a ^ b for a, b in zip(M2[i], M2[r])]
        pv[col] = r
        r += 1
    free = [c for c in range(ncols) if c not in pv]
    basis = []
    for fc in free:
        v = [0] * ncols
        v[fc] = 1
        for col, rr in pv.items():
            if M2[rr][fc]:
                v[col] = 1
        basis.append(v)
    for j in range(ncols):
        if j in pv:
            basis.append([2 if i == j else 0 for i in range(ncols)])
    return basis

A2 = [[a & 1 for a in row] for row in A]
B = f2_basis_of_kernel(A2, l)
jj = 1
while jj < 8:
    AB = [[sum(A[ii][t] * B[q][t] for t in range(l)) for q in range(l)] for ii in range(k)]
    Mj = [[(v >> jj) & 1 for v in row] for row in AB]
    K = f2_basis_of_kernel(Mj, l)
    B = [[sum(K[p][t] * B[t][c] for t in range(l)) for c in range(l)] for p in range(l)]
    jj += 1

W = 3
E = IntegerMatrix(l + 1, l + 1)
for i in range(l):
    for c in range(l):
        E[i, c] = B[i][c] * W
    E[i, l] = 0
for c in range(l):
    E[l, c] = xp[c] * W
E[l, l] = 1
BKZReduction(E)(BKZParams.Param(block_size=60))

best = None
for i in range(E.nrows):
    if abs(int(E[i, l])) == 1:
        row = [int(E[i, c]) for c in range(l)]
        nrm = sum(z * z for z in row)
        if best is None or nrm < best[0]:
            best = (nrm, row, int(E[i, l]))
nrm, row, last = best
x = [last * z // W for z in row]
print("norm2 x:", nrm // 9)
print("A*x==h:", all(sum(A[ii][c] * x[c] for c in range(l)) % 256 == h[ii] for ii in range(k)))

val = sum(x[i] * 5 ** i for i in range(l)) + (P - 1) // 2
print("val bit_length:", val.bit_length(), " P bits:", P.bit_length())
known = b"BZHCTF{"
n_tail = n_mid = n_print = 0
cands = []
c = 0
while True:
    outv = val + c * P
    if outv >= 1 << 128:
        break
    o = outv.to_bytes(16, "little")
    tail = bytes(t ^ b for t, b in zip(o[:7], known))
    ok_t = all(48 <= y <= 57 or 97 <= y <= 102 for y in tail)
    n_tail += ok_t
    mid = bytes(o[ii] ^ (0x7d if ii == 7 else 0x08) for ii in range(7, 16))
    ok_m = all(48 <= y <= 57 or 97 <= y <= 102 for y in mid)
    n_mid += ok_m
    if ok_t and ok_m:
        cands.append((c, "BZHCTF{" + mid.decode() + tail.decode() + "}"))
    # fully-printable relaxed: full message "BZHCTF{...}" printable via inverse fold
    # reconstruct msg bytes: b1 = o ^ b2 requires knowing split; relaxed check:
    # treat flag content as printable: mid2 = all bytes in 32..126
    mid2 = bytes(o[ii] ^ (0x7d if ii == 7 else 0x08) for ii in range(7, 16))
    tail2 = bytes(t ^ b for t, b in zip(o[:7], known))
    if all(32 <= y <= 126 for y in mid2 + tail2):
        n_print += 1
        if n_print <= 12:
            print(" printable c=%d: BZHCTF{%s%s}" % (c, mid2.decode(), tail2.decode()))
    c += 1
print("c scanned:", c, " tail-hex:", n_tail, " mid-hex:", n_mid, " printable-any:", n_print)
print("strict cands:", cands)
