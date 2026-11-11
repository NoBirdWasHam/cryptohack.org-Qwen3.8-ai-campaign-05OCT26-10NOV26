# solve9.py — Kannan + BKZ(15,20) + pruned SVP
import ast, hashlib, os, sys, time
D = os.path.dirname(os.path.abspath(__file__))

def pv(s):
    s = s.strip()
    if s.startswith('Vecsmall('):
        s = s[len('Vecsmall('):]
        if s.endswith(')'): s = s[:-1]
    if s[0] == '[' and s[-1] == ']': s = s[1:-1]
    return [int(x) for x in s.split(',')]

from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction
from fpylll.fplll.bkz import bkz_reduction
from fpylll.fplll.bkz_param import BKZParam

bi = int(sys.argv[1])
txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha512(secret).digest(); pub = []
for _ in range(256):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha512(state).digest()
variant = 'b0' if bi == 0 else ('b6' if bi == 6 else 'mid')
K = [pv(l) for l in open(os.path.join(D, f'K_{variant}.txt')) if l.strip()]
m0 = pv(open(os.path.join(D, (f'm0_mid{bi+1}.txt' if variant == 'mid' else f'm0_{variant}.txt'))).readline())
keep = pv(open(os.path.join(D, f'keep_{variant}.txt')).readline())
n2 = len(keep); d = len(K)
beta = 23
T = [1 - 2 * x for x in m0]
flat = []
for i in range(d): flat += [2 * K[i][j] for j in range(n2)] + [0]
flat += T + [beta]
t0 = time.time()
M = lll_reduction(IntegerMatrix.from_iterable(d + 1, n2 + 1, flat))
print(f'lll {time.time()-t0:.0f}s', flush=True)
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
        bits = [0] * 512
        if variant == 'b0':
            pos = 192
            for ch in b'crypto{':
                for bit in range(8):
                    bits[pos] = (ch >> (7 - bit)) & 1; pos += 1
        for idx, kpos in enumerate(keep):
            bits[kpos - 1] = m[idx]
        mb = bytes(int(''.join(map(str, bits[8 * t:8 * t + 8])), 2) for t in range(64))
        if all((pub[j] & int.from_bytes(mb, 'big')).bit_count() == enc[bi][j] for j in range(256)):
            return mb
    return None

cands = scan(M)
print('LLL cands:', cands[:3], flush=True)
mb = try_cands(cands)
for bs in (15, 20):
    t1 = time.time()
    M = bkz_reduction(M, BKZParam(bs))
    cands = scan(M)
    print(f'bkz{bs} {time.time()-t1:.0f}s cands:', cands[:3], flush=True)
    mb = try_cands(cands)
if mb is None:
    from fpylll import SVP
    t1 = time.time()
    try:
        sv = SVP.shortest_vector(M, method="fast", pruning=True, preprocess=0)
        nm = sum(x*x for x in sv)
        print('svp fast', time.time()-t1, 'norm2', nm, flush=True)
        mb = try_cands([(nm, None)]) if False else None
        if nm == n2 + beta*beta:
            last = sv[n2]; raw = [sv[j] for j in range(n2)]
            v = [(T[j] + raw[j]) // 2 if last < 0 else (T[j] - raw[j]) // 2 for j in range(n2)]
            m = [m0[j] + v[j] for j in range(n2)]
            if all(x in (0,1) for x in m):
                bits = [0]*512
                if variant == 'b0':
                    pos = 192
                    for ch in b'crypto{':
                        for bit in range(8):
                            bits[pos] = (ch >> (7-bit)) & 1; pos += 1
                for idx, kpos in enumerate(keep): bits[kpos-1] = m[idx]
                mb = bytes(int(''.join(map(str,bits[8*t:8*t+8])),2) for t in range(64))
                if not all((pub[j] & int.from_bytes(mb,'big')).bit_count() == enc[bi][j] for j in range(256)):
                    mb = None
    except Exception as e:
        print('svp failed:', str(e)[:100], flush=True)
if mb is None:
    print('FAIL'); sys.exit(1)
print('SOLVED seg:', mb[24:32])
open(os.path.join(D, f'seg_{bi}.txt'), 'wb').write(mb[24:32])
