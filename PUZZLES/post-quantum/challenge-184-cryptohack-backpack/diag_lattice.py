import os, time, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location("sb", os.path.join(HERE, "solve_backpack.py"))
# don't run the whole solver; re-derive data manually
import fpylll
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

out = open(os.path.join(HERE, "output.txt"), encoding="utf-8").read()
pk_line = [l for l in out.splitlines() if l.startswith("Public key")][0]
ct_line = [l for l in out.splitlines() if l.startswith("Encrypted")][0]
a = eval(pk_line.split(":", 1)[1])
ct = int(ct_line.split(":", 1)[1])
n = len(a)

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
print("n_u =", len(a_u), "t bits =", t.bit_length())

N = 1 << (len(a_u) // 2)
B = IntegerMatrix(len(a_u) + 1, len(a_u) + 1)
for i in range(len(a_u)):
    B[i, i] = 1
    B[i, len(a_u)] = N * a_u[i]
B[len(a_u), len(a_u)] = N * t

t0 = time.time()
R = lll_reduction(B)
print("LLL", round(time.time() - t0, 2), "s")
rows = []
for i in range(R.nrows):
    last = int(R[i, len(a_u)])
    xs = [int(R[i, j]) for j in range(len(a_u))]
    nrm2 = sum(e * e for e in xs) + last * last
    rows.append((i, last, nrm2, xs))
rows_sorted = sorted(rows, key=lambda r: r[2])
print("shortest 12 rows (rowidx, last, norm2, first 12 coeffs):")
for i, last, nrm2, xs in rows_sorted[:12]:
    print(f"  row {i:3d} last={last} norm2={nrm2} {xs[:12]}")
# any 0/1 row with last==0?
cand = [r for r in rows if r[1] == 0 and all(e in (0, 1) for e in r[3])]
print("0/1 rows with last==0:", len(cand))
for i, last, nrm2, xs in cand[:5]:
    print("   dot check:", sum(e * w for e, w in zip(xs, a_u)) == t, "norm2", nrm2)
