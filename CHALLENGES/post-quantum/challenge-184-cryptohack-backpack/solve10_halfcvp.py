"""Backpack v10: half-integer-target CVP.
Lattice L = {(2x, 2 a.x) : x in Z^182} in Z^183, target T = (1^182, 2t).
For any lattice point (2x, 2a.x): dist^2 = sum(2x_i-1)^2 + (2(a.x-t))^2.
 - 0/1 x with a.x=t (the message): dist^2 = 182 exactly.
 - any other integer x: some coord outside {0,1} adds >= +8, or a.x!=t adds >= 4.
So the message is the UNIQUE closest lattice point (0/1 solution unique at density 0.48).
try5 failed because target 1^m is biased toward non-0/1 solutions; half-integer is symmetric.
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction
from fpylll.fplll.bkz import bkz_reduction
from fpylll.fplll.bkz_param import BKZParam
from fpylll.fplll.svpcvp import closest_vector, babai

out = open(os.path.join(HERE, "output.txt"), encoding="utf-8").read()
a_all = eval([l for l in out.splitlines() if l.startswith("Public key")][0].split(":", 1)[1])
ct = int([l for l in out.splitlines() if l.startswith("Encrypted")][0].split(":", 1)[1])
n = len(a_all)
assert n == 272

m_one = 0x7D
for sh, bval in [(216, 0x7B), (224, 0x6F), (232, 0x74), (240, 0x70), (248, 0x79), (256, 0x72), (264, 0x63)]:
    m_one |= bval << sh
msb_zero = {8 * (33 - b) + 7 for b in range(7, 33)}
known_pos = set(range(0, 8)) | set(range(216, 272)) | msb_zero
unk = [i for i in range(n) if i not in known_pos]
aU = [a_all[i] for i in unk]
m = len(aU)
known_sum = sum(a_all[i] for i in range(n) if (m_one >> i) & 1)
t = ct - known_sum
print(f"unknowns={m} t bits={t.bit_length()}", flush=True)


def check_point(cv):
    """cv = ambient coords (2x_1..2x_m, 2a.x). Return flag bytes if valid."""
    cv = [int(e) for e in cv]
    if len(cv) != m + 1:
        return None
    if cv[m] != 2 * t:
        return None
    if any(c % 2 for c in cv[:m]):
        return None
    x = [c // 2 for c in cv[:m]]
    if not all(e in (0, 1) for e in x):
        return None
    if sum(aU[k] * x[k] for k in range(m)) != t:
        return None
    msg = m_one
    for k, i in enumerate(unk):
        if x[k]:
            msg |= 1 << i
    flag = msg.to_bytes(34, "big")
    m_int = int.from_bytes(flag, "big")
    if sum(((m_int >> i) & 1) * a_all[i] for i in range(n)) != ct:
        return None
    return flag


def finish(flag):
    print("FLAG:", flag.decode(), flush=True)
    with open(os.path.join(HERE, "flag_backpack.txt"), "wb") as fh:
        fh.write(flag)
    sys.exit(0)


B = IntegerMatrix(m, m + 1)
for i in range(m):
    B[i, i] = 2
    B[i, m] = 2 * aU[i]
T = [1] * m + [2 * t]

t0 = time.time()
RL = lll_reduction(B)
print(f"LLL: {time.time()-t0:.1f}s", flush=True)

# Babai on LLL basis
try:
    bb = babai(RL, T)
    f = check_point(bb)
    print(f"babai(LLl): flag={f}", flush=True)
    if f:
        finish(f)
except Exception as e:
    print("babai raised:", e, flush=True)

for bs in (20, 30, 40):
    t0 = time.time()
    RB = bkz_reduction(RL, BKZParam(bs))
    print(f"BKZ-{bs}: {time.time()-t0:.1f}s", flush=True)
    try:
        bb = babai(RB, T)
        f = check_point(bb)
        print(f"babai(BKZ{bs}): flag={f}", flush=True)
        if f:
            finish(f)
    except SystemExit:
        raise
    except Exception as e:
        print(f"babai(BKZ{bs}) raised: {e}", flush=True)
    for meth in ("fast", "proved"):
        t0 = time.time()
        try:
            cv = closest_vector(RB, T, meth)
            f = check_point(cv)
            cvl = [int(e) for e in cv]
            d2 = sum((c - 1) ** 2 for c in cvl[:m]) + (cvl[m] - 2 * t) ** 2
            print(f"CVP-{meth}(BKZ{bs}): {time.time()-t0:.1f}s dist2={d2} flag={f}", flush=True)
            if f:
                finish(f)
        except SystemExit:
            raise
        except Exception as e:
            print(f"CVP-{meth}(BKZ{bs}) raised after {time.time()-t0:.1f}s: {e}", flush=True)

print("FAILED")
