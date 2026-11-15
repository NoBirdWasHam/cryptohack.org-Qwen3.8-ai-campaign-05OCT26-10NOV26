"""Backpack: low-density subset-sum on 182 unknown bits, solved via BKZ on the
Coster-style lattice. Rows (e_i, W*a_i) plus (0, W*t): since a.eps == t over Z,
the vector (eps, 0) lies in the lattice and is the shortest vector. LLL alone
(prior attempts) only got norm2=234; BKZ should find the true 0/1 message."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
from fpylll import IntegerMatrix, BKZ
from fpylll.fplll.bkz import bkz_reduction

out = open(os.path.join(HERE, "output.txt"), encoding="utf-8").read()
a_all = eval([l for l in out.splitlines() if l.startswith("Public key")][0].split(":", 1)[1])
ct = int([l for l in out.splitlines() if l.startswith("Encrypted")][0].split(":", 1)[1])
n = len(a_all)

# known bits: "crypto{" (bytes 0..6, big-endian) + "}" (byte 33) + ASCII MSB=0 for bytes 7..32
m_one = 0x7D
for sh, bval in [(216, 0x7B), (224, 0x6F), (232, 0x74), (240, 0x70), (248, 0x79), (256, 0x72), (264, 0x63)]:
    m_one |= bval << sh
msb_zero = {8 * (33 - b) + 7 for b in range(7, 33)}
known_pos = set(range(0, 8)) | set(range(216, 272)) | msb_zero
known_sum = sum(a_all[i] for i in range(n) if (m_one >> i) & 1)
t = ct - known_sum
unk = [i for i in range(n) if i not in known_pos]
aU = [a_all[i] for i in unk]
m = len(aU)
print("unknowns:", m, "t bits:", t.bit_length())


def check(v):
    if sum(aU[k] * v[k] for k in range(m)) != t:
        return None
    msg = m_one
    for k, i in enumerate(unk):
        if v[k]:
            msg |= 1 << i
    flag = msg.to_bytes(34, "big")
    calc = sum(((int.from_bytes(flag, "big") >> i) & 1) * a_all[i] for i in range(n))
    return flag if calc == ct else None


for Nbits in (104, 95, 110):
    W = 1 << Nbits
    B = IntegerMatrix(m + 1, m + 1)
    for i in range(m):
        B[i, i] = 1
        B[i, m] = W * aU[i]
    B[m, m] = W * t
    t0 = time.time()
    for bs in (40, 60):
        bb = IntegerMatrix(B)
        bb.bkz(BKZ(bs, flags=BKZ.GH_BND))
        found = False
        for i in range(bb.nrows):
            v = [int(bb[i, k]) for k in range(m)]
            if all(e in (0, 1) for e in v):
                flag = check(v)
                print(f"N=2^{Nbits} bkz{bs} row{i}: 0/1 row, flag={flag} ({time.time()-t0:.1f}s)")
                if flag:
                    with open(os.path.join(HERE, "flag_backpack.txt"), "wb") as f:
                        f.write(flag)
                    print("FLAG:", flag.decode())
                    sys.exit(0)
                found = True
        print(f"N=2^{Nbits} bkz{bs}: no 0/1 msg row ({time.time()-t0:.1f}s)")
print("FAILED")
