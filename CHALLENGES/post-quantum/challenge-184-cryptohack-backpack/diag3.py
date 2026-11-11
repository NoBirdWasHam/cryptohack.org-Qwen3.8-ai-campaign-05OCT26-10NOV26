"""Diagnose the 'non-relation' row from try3: inspect every last==0 short row,
check aU.v exactly, and report magnitudes (size-bound sanity check)."""
import os, time
HERE = os.path.dirname(os.path.abspath(__file__))
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction

out = open(os.path.join(HERE, "output.txt"), encoding="utf-8").read()
a_all = eval([l for l in out.splitlines() if l.startswith("Public key")][0].split(":", 1)[1])
ct = int([l for l in out.splitlines() if l.startswith("Encrypted")][0].split(":", 1)[1])
n = len(a_all)
print("n =", n)

m_known = 0x7D
for sh, bval in [(216, 0x7B), (224, 0x6F), (232, 0x74), (240, 0x70), (248, 0x79), (256, 0x72), (264, 0x63)]:
    m_known |= bval << sh
unk_idx = [i for i in range(n) if not ((m_known >> i) & 1)]
print("num unknown:", len(unk_idx))
aU = [a_all[i] for i in unk_idx]
print("aU weight bitlengths: min", min(w.bit_length() for w in aU),
      "max", max(w.bit_length() for w in aU))
known_sum = sum(a_all[i] for i in range(n) if (m_known >> i) & 1)
t = ct - known_sum
print("t bits:", t.bit_length(), "t>0:", t > 0)
print("sum(aU) bits:", sum(aU).bit_length())
print("size bound: max|aU| * sqrt(208)*20 bits ~", max(aU).bit_length() + 12)

m = len(aU)
N = 1 << 104
B = IntegerMatrix(m + 1, m + 1)
for i in range(m):
    B[i, i] = 1
    B[i, m] = N * aU[i]
B[m, m] = N * t
t0 = time.time()
R = lll_reduction(B)
print("LLL:", round(time.time() - t0, 1), "s")

bad = []
cnt = 0
for i in range(R.nrows):
    last = int(R[i, m])
    if last == 0:
        v = [int(R[i, k]) for k in range(m)]
        nrm2 = sum(e * e for e in v)
        if nrm2 > 400:
            continue
        cnt += 1
        S = sum(aU[k] * v[k] for k in range(m))
        if S != 0:
            bad.append((i, nrm2, S))
            print(f"ROW {i}: nrm2={nrm2} |S| bits={S.bit_length()} S==t? {S == t} S==-t? {S == -t} S%t==0? {S % t == 0}")
            print("   v:", v)
print("short last==0 rows:", cnt, " bad (S!=0):", len(bad))
