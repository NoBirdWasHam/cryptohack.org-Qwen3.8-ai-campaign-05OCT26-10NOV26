# solve2.py — FaILProof Revenge: per-block unique-solution CVP.
# Kernel lattice from gp matsnf (Kred.txt, LLL'd by qflll), particular solutions m0.txt,
# Kannan embedding (2-scaled, half-integer target) + fpylll BKZ.
import ast, hashlib, os, sys
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction
from fpylll.fplll.bkz import bkz_reduction
from fpylll.fplll.bkz_param import BKZParam

D = os.path.dirname(os.path.abspath(__file__))

def pv(s):
    s = s.strip()
    if s[0] == '[' and s[-1] == ']': s = s[1:-1]
    return [int(x) for x in s.split(',')]

txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha512(secret).digest(); pub = []
for _ in range(256):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha512(state).digest()

K = [pv(l) for l in open(os.path.join(D, 'Kred.txt')) if l.strip()]
m0s = [pv(l) for l in open(os.path.join(D, 'm0.txt')) if l.strip()]
assert len(K) == 256 and len(m0s) == len(enc)
print('K', len(K), 'maxabs', max(max(map(abs, r)) for r in K),
      'm0 digits', max(len(str(abs(x))) for x in m0s[0]))

flag = b''
beta = 23
for bi, (c, m0) in enumerate(zip(enc, m0s)):
    T = [1 - 2 * x for x in m0]
    flat = []
    for i in range(256): flat += [2 * K[i][j] for j in range(512)] + [0]
    flat += T + [beta]
    MM = IntegerMatrix.from_iterable(257, 513, flat)
    M = lll_reduction(MM)
    cands = [(sum(M[i, j] * M[i, j] for j in range(512)), i)
             for i in range(M.nrows) if abs(M[i, 512]) == beta]
    print(f'block {bi}: after LLL, {len(cands)} |last|=beta rows', flush=True)
    if not cands or min(c for c, _ in cands) != 512:
        print(f'block {bi}: escalating BKZ on reduced lattice', flush=True)
        M = bkz_reduction(M, BKZParam(20))
        cands = [(sum(M[i, j] * M[i, j] for j in range(512)), i)
                 for i in range(M.nrows) if abs(M[i, 512]) == beta]
    done = False
    for nm, i in sorted(cands):
        raw = [M[i, j] for j in range(512)]
        last = M[i, 512]
        v = [(T[j] + raw[j]) // 2 if last < 0 else (T[j] - raw[j]) // 2 for j in range(512)]
        m = [m0[j] + v[j] for j in range(512)]
        if not all(x in (0, 1) for x in m): continue
        mb = bytes(m[8 * i2:8 * i2 + 8] for i2 in range(64))
        if all((pub[j] & int.from_bytes(mb, 'big')).bit_count() == c[j] for j in range(256)):
            seg = mb[24:32]
            print(f'block {bi}: SOLUTION seg={seg}')
            flag += seg; done = True; break
    if not done:
        print(f'block {bi}: candidates failed verification'); sys.exit(1)

flag_str = flag.rstrip(b'\x00').decode('latin1')
print('FLAG:', flag_str)
open(os.path.join(D, 'flag_failproof_revenge-sekaictf202.txt'), 'w').write(flag_str)
