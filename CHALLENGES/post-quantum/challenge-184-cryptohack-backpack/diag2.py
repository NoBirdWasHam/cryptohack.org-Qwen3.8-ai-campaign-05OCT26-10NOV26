import os
HERE = os.path.dirname(os.path.abspath(__file__))
import fpylll
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

out = open(os.path.join(HERE, "output.txt"), encoding="utf-8").read()
pk_line = [l for l in out.splitlines() if l.startswith("Public key")][0]
ct_line = [l for l in out.splitlines() if l.startswith("Encrypted")][0]
a = eval(pk_line.split(":", 1)[1])
ct = int(ct_line.split(":", 1)[1])

m_known = 0x7D
m_known |= 0x7B << 216
m_known |= 0x6F << 224
m_known |= 0x74 << 232
m_known |= 0x70 << 240
m_known |= 0x79 << 248
m_known |= 0x72 << 256
m_known |= 0x63 << 264
known_pos = set(range(0, 8)) | set(range(216, 272))
unk_pos = [i for i in range(272) if i not in known_pos]
known_sum = sum(((m_known >> i) & 1) * a[i] for i in known_pos)
t = ct - known_sum
a_u = [a[i] for i in unk_pos]
n = len(a_u)

N = 1 << (n // 2)
B = IntegerMatrix(n + 1, n + 1)
for i in range(n):
    B[i, i] = 1
    B[i, n] = N * a_u[i]
B[n, n] = N * t
R = lll_reduction(B)

# row 13 coefficients
xs = [int(R[13, j]) for j in range(n)]
S = sum(c * w for c, w in zip(xs, a_u))
print("row13 S = sum(c*a) =", S.bit_length(), "bits")
import math
# S should equal -z0 * t
q_, r_ = divmod(abs(S), t)
print("|S| // t =", q_, "  |S| % t == 0 ?", r_ == 0)
print("z0 = S/t =", S // t, "  remainder", S % t)

# check a few more short rows
for ri in (0, 17, 23, 24, 25):
    xs = [int(R[ri, j]) for j in range(n)]
    S = sum(c * w for c, w in zip(xs, a_u))
    print(f"row {ri}: S/t = {S//t}, rem {S % t == 0}, nonzero coeffs {sum(1 for c in xs if c)}, max|c| {max(abs(c) for c in xs)}")
