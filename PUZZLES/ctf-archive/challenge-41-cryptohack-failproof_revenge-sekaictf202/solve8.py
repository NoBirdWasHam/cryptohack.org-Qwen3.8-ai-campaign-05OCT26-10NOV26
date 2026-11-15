# solve8.py — block CLI: Kannan + fixed-radius raw Enumeration (tiny ball => cheap nodes)
import ast, hashlib, os, sys, time
D = os.path.dirname(os.path.abspath(__file__))

def pv(s):
    s = s.strip()
    if s.startswith('Vecsmall('):
        s = s[len('Vecsmall('):]
        if s.endswith(')'): s = s[:-1]
    if s[0] == '[' and s[-1] == ']': s = s[1:-1]
    return [int(x) for x in s.split(',')]

from fpylll import IntegerMatrix, GSO, Enumeration
from fpylll.fplll.lll import lll_reduction

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

def check(v):
    last = v[n2]
    if abs(last) != beta: return None
    raw = [v[j] for j in range(n2)]
    vv = [(T[j] + raw[j]) // 2 if last < 0 else (T[j] - raw[j]) // 2 for j in range(n2)]
    m = [m0[j] + vv[j] for j in range(n2)]
    if not all(x in (0, 1) for x in m): return None
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

gso = GSO.Mat(M)
gso.update_gso()
en = Enumeration(gso)
try:
    sols = en.enumerate(0, d + 1, float(target_nm) + 0.5, 0)
except Exception as e:
    print('enum failed:', str(e)[:120]); sys.exit(2)
print('enum', time.time() - t0, 'solutions:', len(sols), flush=True)
seen = set()
mb = None
for coeffs, norm2 in sols:
    if int(norm2) in seen: continue
    seen.add(int(norm2))
    v = [sum(c * M[i, j] for i, c in enumerate(coeffs) if c) for j in range(n2 + 1)]
    mb = check(v)
    if mb: break
if mb is None:
    print('FAIL; norms:', sorted(set(int(n2v) for _, n2v in sols))[:5]); sys.exit(1)
print('SOLVED seg:', mb[24:32])
open(os.path.join(D, f'seg_{bi}.txt'), 'wb').write(mb[24:32])
