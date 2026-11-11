# Kannan embedding on kernel lattice + BKZ ladder (adapted from sibling failproof_revenge solve10.py)
import ast, hashlib, os, sys, time
D = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha256(secret).digest(); pub = []
for _ in range(128):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha256(state).digest()

def pv(s):
    s = s.strip()
    if s.startswith('Vecsmall('):
        s = s[len('Vecsmall('):]
        if s.endswith(')'): s = s[:-1]
    if s[0] == '[' and s[-1] == ']': s = s[1:-1]
    return [int(x) for x in s.split(',')]

variant = sys.argv[1]           # b0 or mid2
blk = 0 if variant == 'b0' else 1
K = [pv(l) for l in open(os.path.join(D, f'K_{variant}.txt')) if l.strip()]
m0 = pv(open(os.path.join(D, f'm0_{variant}.txt')).readline())
keep = pv(open(os.path.join(D, f'keep_{variant}.txt')).readline())
n2 = len(keep); d = len(K)
beta = 23
T = [1 - 2 * x for x in m0]
from fpylll import IntegerMatrix, GSO
from fpylll.fplll.lll import lll_reduction
from fpylll.fplll.bkz import bkz_reduction
from fpylll.fplll.bkz_param import BKZParam
Kmat = IntegerMatrix.from_iterable(d, n2, [2 * v for row in K for v in row])
Kred2 = lll_reduction(Kmat)
def reduce_by_lattice(rows_list, t):
    from fractions import Fraction
    d_ = len(rows_list); n_ = len(t)
    bstar = []; cstar = []
    for i in range(d_):
        v = [Fraction(x) for x in rows_list[i]]
        for k in range(i):
            if cstar[k] == 0: continue
            mu = sum(Fraction(rows_list[i][j]) * bstar[k][j] for j in range(n_)) / cstar[k]
            if mu:
                v = [v[j] - mu * bstar[k][j] for j in range(n_)]
        bstar.append(v)
        cstar.append(sum(x * x for x in v))
    tt = [Fraction(x) for x in t]
    for i in range(d_ - 1, -1, -1):
        c = sum(tt[j] * bstar[i][j] for j in range(n_)) / cstar[i]
        q = int((2 * c.numerator + c.denominator) // (2 * c.denominator)) if c >= 0 else -int(((-2 * c.numerator) + c.denominator) // (2 * c.denominator))
        if q:
            r = rows_list[i]
            tt = [tt[j] - q * Fraction(r[j]) for j in range(n_)]
    return [int(x) for x in tt]
T = reduce_by_lattice([[2 * K[i][j] for j in range(n2)] for i in range(d)], T)
print('T reduced max|T| bits:', max(abs(t).bit_length() for t in T), flush=True)
flat = []
for i in range(d): flat += [2 * K[i][j] for j in range(n2)] + [0]
flat += T + [beta]
t0 = time.time()
M = lll_reduction(IntegerMatrix.from_iterable(d + 1, n2 + 1, flat))
print(f'lll {time.time()-t0:.0f}s dim {d+1}x{n2+1}', flush=True)
target_nm = n2 + beta * beta

def scan(M):
    cands = []
    for i in range(M.nrows):
        if abs(M[i, n2]) == beta:
            nm = sum(M[i, j] * M[i, j] for j in range(n2))
            cands.append((nm, i))
    return sorted(cands)

def try_cands(cands):
    for nm, i in cands:
        if nm != target_nm: continue
        raw = [M[i, j] for j in range(n2)]; last = M[i, n2]
        v = [(T[j] + raw[j]) // 2 if last < 0 else (T[j] - raw[j]) // 2 for j in range(n2)]
        m = [m0[j] + v[j] for j in range(n2)]
        if not all(x in (0, 1) for x in m): continue
        bits = [0] * 256
        if variant == 'b0':
            pos = 0
            for ch in b'crypto{':
                for bit in range(8):
                    bits[pos] = (ch >> (7 - bit)) & 1; pos += 1
        for idx, kpos in enumerate(keep):
            bits[kpos - 1] = m[idx]
        mb = bytes(int(''.join(map(str, bits[8 * t:8 * t + 8])), 2) for t in range(32))
        if all((pub[j] & int.from_bytes(mb, 'big')).bit_count() == enc[blk][j] for j in range(128)):
            return mb
    return None

cands = scan(M)
print('LLL cands:', cands[:3], 'target', target_nm, flush=True)
mb = try_cands(cands)
if mb is None:
    for bs in (15, 20, 25):
        t1 = time.time()
        M = bkz_reduction(M, BKZParam(bs))
        cands = scan(M)
        print(f'bkz{bs} {time.time()-t1:.0f}s cands:', cands[:3], flush=True)
        mb = try_cands(cands)
        if mb is not None: break
if mb is not None:
    print('SOLVED:', mb, flush=True)
    open(os.path.join(D, f'seg_{variant}.txt'), 'wb').write(mb)
else:
    from fpylll import GSO, Enumeration
    import math
    def enum_solve(Mx):
        gso = GSO.Mat(Mx)
        en = Enumeration(gso)
        try:
            sols = en.enumerate(0, d + 1, math.sqrt(target_nm + 1), 0)
            print('enum sols:', len(sols), flush=True)
        except Exception as e:
            print('enum failed:', str(e)[:120], flush=True); return None
        seen = set()
        for coeffs, norm2 in sols:
            key = tuple(int(c) for c in coeffs)
            if key in seen: continue
            seen.add(key)
            v = [sum(c * Mx[i, j] for i, c in enumerate(coeffs) if c) for j in range(n2 + 1)]
            last = v[n2]
            if abs(last) != beta: continue
            raw = v[:n2]
            vv = [(T[j] + raw[j]) // 2 if last < 0 else (T[j] - raw[j]) // 2 for j in range(n2)]
            m = [m0[j] + vv[j] for j in range(n2)]
            if not all(x in (0, 1) for x in m): continue
            bits = [0] * 256
            if variant == 'b0':
                pos = 0
                for ch in b'crypto{':
                    for bit in range(8):
                        bits[pos] = (ch >> (7 - bit)) & 1; pos += 1
            for idx, kpos in enumerate(keep): bits[kpos - 1] = m[idx]
            mb2 = bytes(int(''.join(map(str, bits[8 * t:8 * t + 8])), 2) for t in range(32))
            if all((pub[j] & int.from_bytes(mb2, 'big')).bit_count() == enc[blk][j] for j in range(128)):
                return mb2
        return None
    for bs in (25, 30, 35, 40, 45, 47):
        t1 = time.time()
        M = bkz_reduction(M, BKZParam(bs))
        mb = try_cands(scan(M))
        if mb is None:
            mb = enum_solve(M)
        print(f'bkz{bs} {time.time()-t1:.0f}s done mb={mb is not None}', flush=True)
        if mb is not None: break
    if mb is not None:
        print('SOLVED via enum:', mb, flush=True)
        open(os.path.join(D, f'seg_{variant}.txt'), 'wb').write(mb)
    else:
        print('FAIL', flush=True)
