"""Solve CryptoHack 'backpack' (120 pts): superincreasing knapsack, exact-sum ciphertext.

ct = sum(x_i * a_i)  (exact integer, no mod). a_i = r*b_i mod q, b superincreasing (private).
Flag = 34 bytes = b'crypto{' + 26 bytes + b'}'  ->  272 bits, bit i of int(bytes_to_long(FLAG))
is weight i (LSB-first per encrypt()).

Attack: the 64 known bits (prefix 'crypto{' + suffix '}') are subtracted, leaving a
208-unknown exact subset sum.  CLOS low-density lattice (Coster-Joux-LaMacchia-Odlyzko-
Schnorr-Stern / Lagarias-Odlyzko):  B = [ I   N*a_u ;  0..0   N*t' ].
Lattice = { (c, N*(sum c_i a_i + c_0 t')) }.  Planted short vector: (x', 0) with
norm sqrt(popcount(x')) ~ 10.  With 208 weights of ~378 bits, the expected number of
competing +/-1 zero-sum relations is ~2^-55, so (x',0) is the unique shortest vector
and LLL recovers it.
"""
import os, time

HERE = os.path.dirname(os.path.abspath(__file__))
import fpylll
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

out = open(os.path.join(HERE, "output.txt"), encoding="utf-8").read()
pk_line = [l for l in out.splitlines() if l.startswith("Public key")][0]
ct_line = [l for l in out.splitlines() if l.startswith("Encrypted")][0]
a = eval(pk_line.split(":", 1)[1])
ct = int(ct_line.split(":", 1)[1])
n = len(a)
print("n =", n, "ct bits =", ct.bit_length())
assert n == 272

# ---- known bits from the crypto{...} format (34 bytes) ----
# bit j of m = bit (j mod 8) of byte F[33 - j//8] (bytes_to_long is big-endian)
m_known = 0x7D                      # F[33] = '}'          -> bits   0..7
m_known |= 0x7B << 216              # F[6]  = '{'          -> bits 216..223
m_known |= 0x6F << 224              # F[5]  = 'o'          -> bits 224..231
m_known |= 0x74 << 232              # F[4]  = 't'          -> bits 232..239
m_known |= 0x70 << 240              # F[3]  = 'p'          -> bits 240..247
m_known |= 0x79 << 248              # F[2]  = 'y'          -> bits 248..255
m_known |= 0x72 << 256              # F[1]  = 'r'          -> bits 256..263
m_known |= 0x63 << 264              # F[0]  = 'c'          -> bits 264..271
# unknown bit positions: 8..215 (208 bits = 26 bytes)
known_pos = set(range(0, 8)) | set(range(216, 272))
unk_pos = [i for i in range(272) if i not in known_pos]
assert len(unk_pos) == 208

known_sum = sum(((m_known >> i) & 1) * a[i] for i in known_pos)
t = ct - known_sum
print("t bits =", t.bit_length())
assert t > 0
a_u = [a[i] for i in unk_pos]

# ---- CLOS lattice ----
N = 1 << (len(a_u) // 2)            # 2^104
t0 = time.time()
B = IntegerMatrix(len(a_u) + 1, len(a_u) + 1)
for i in range(len(a_u)):
    B[i, i] = 1
    B[i, len(a_u)] = N * a_u[i]
B[len(a_u), len(a_u)] = N * t
print("lattice built in", round(time.time() - t0, 2), "s")

t0 = time.time()
R = lll_reduction(B)
print("LLL time", round(time.time() - t0, 2), "s")

found = None
for i in range(R.nrows):
    if int(R[i, len(a_u)]) != 0:
        continue
    xs = [int(R[i, j]) for j in range(len(a_u))]
    if all(e in (0, 1) for e in xs) and sum(e * w for e, w in zip(xs, a_u)) == t:
        found = xs
        print("FOUND at reduced-basis row", i)
        break
if found is None:
    print("not in LLL basis; escalating to BKZ")
    from fpylll.fplll.bkz import bkz_reduction
    from fpylll.fplll.bkz_param import BKZParam
    for bs in (40, 60, 80):
        t0 = time.time()
        Rb = bkz_reduction(B, BKZParam(bs))
        print(f"BKZ({bs}) time", round(time.time() - t0, 2), "s")
        for i in range(Rb.nrows):
            if int(Rb[i, len(a_u)]) != 0:
                continue
            xs = [int(Rb[i, j]) for j in range(len(a_u))]
            if all(e in (0, 1) for e in xs) and sum(e * w for e, w in zip(xs, a_u)) == t:
                found = xs
                print("FOUND after BKZ", bs, "at row", i)
                break
        if found is not None:
            break

if found is None:
    print("FAILED to recover the 0/1 vector")
    raise SystemExit(1)

m = m_known
for k, i in enumerate(unk_pos):
    if found[k]:
        m |= 1 << i
flag = m.to_bytes(34, "big")
print("FLAG:", flag)
assert flag.startswith(b"crypto{") and flag.endswith(b"}")
print("all printable:", all(32 < b < 127 for b in flag))
open(os.path.join(HERE, "flag.txt"), "w").write(flag.decode())
