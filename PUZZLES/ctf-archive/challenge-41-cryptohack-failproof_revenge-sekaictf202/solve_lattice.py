# solve_lattice.py — CVP per block: kernel lattice (gp SNF, LLL) + shrink m0 by exact
# greedy rounding, Kannan embedding + BKZ via fpylll.
import ast, hashlib, os, re, sys, time
from fpylll import Matrix, IntegerMatrix, LLL, BKZ, CVP

D = os.path.dirname(os.path.abspath(__file__))

def parse_mat(s):
    s = s.strip()
    assert s[0] == '[' and s[-1] == ']', s[:40]
    s = s[1:-1]
    rows = s.split(';')
    return [[int(x) for x in r.split(',')] for r in rows]

def parse_vec(s):
    s = s.strip()
    if s[0] == '[' and s[-1] == ']': s = s[1:-1]
    return [int(x) for x in s.split(',')]

# --- reload instance ---
txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha512(secret).digest(); pub = []
for _ in range(256):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha512(state).digest()
Aint = pub  # popcount equations with these ints

Kred = parse_mat(open(os.path.join(D, 'Kred.gp')).read())
assert len(Kred) == 256 and len(Kred[0]) == 512
m0s = [parse_vec(line) for line in open(os.path.join(D, 'm0.gp')) if line.strip()]
assert len(m0s) == len(enc), (len(m0s), len(enc))
print('loaded K', len(Kred), 'x', len(Kred[0]), ' maxabs', max(max(map(abs, r)) for r in Kred))

def dot(a, b): return sum(x*y for x, y in zip(a, b))

def shrink(m0, K):
    """subtract lattice combos so m0 becomes small; returns new m0'"""
    r = list(m0)
    kn = [dot(k, k) for k in K]
    for sweep in range(10):
        moved = 0
        for k, nn in zip(K, kn):
            q = dot(r, k)
            q, rem = divmod(q, nn)
            if rem * 2 > nn: q += 1
            elif rem * 2 <= -nn: q -= 1
            if q:
                moved += 1
                for i in range(512): r[i] -= q * k[i]
        mx = max(map(abs, r))
        print(f'  sweep {sweep}: maxabs={mx}')
        if mx <= 64: break
    return r

flag = ''
for bi, (c, m0) in enumerate(zip(enc, m0s)):
    t0 = time.time()
    m0r = shrink(m0, Kred)
    if max(map(abs, m0r)) > 2000:
        print('block', bi, 'WARNING m0 still big')
    T = [1 - 2*x for x in m0r]           # 2*t'
    beta = 23
    M = IntegerMatrix(257, 513)
    for i in range(256):
        for j in range(512): M[i, j] = 2 * Kred[i][j]
    M[256, 512] = beta
    for j in range(512): M[256, j] = T[j]
    BKZ(M, BKZ.BKZ.BKZ_DEFAULT, delta=0.99, blocksizes=[20, 30, 40])
    best = None
    for i in range(257):
        if abs(M[i, 512]) == beta:
            nm = sum(M[i, j] * M[i, j] for j in range(512))
            if best is None or nm < best[0]:
                best = (nm, [M[i, j] for j in range(512)], -1 if M[i, 512] < 0 else 1)
    if best is None:
        print('block', bi, 'no Kannan vector found?!'); sys.exit(1)
    sgn = best[2]; s = best[1]
    if sgn < 0: s = [-x for x in s]
    # s = 2(v* - t')  ->  v* = (T + s)/2
    v = [(T[j] + s[j]) // 2 for j in range(512)]
    m = [m0r[j] + v[j] for j in range(512)]
    ok = all(x in (0, 1) for x in m)
    print(f'block {bi}: bits01={ok} t={time.time()-t0:.1f}s')
    if not ok:
        print('  sample m:', m[:20]); sys.exit(1)
    # verify equations exactly
    mbytes = bytes(m[8*i:8*i+8] for i in range(64))
    for j in range(256):
        assert (Aint[j] & int.from_bytes(mbytes, "big")).bit_count() == c[j], f'block {bi} eq {j}'
    seg = mbytes[24:32]
    print('  segment:', seg)
    flag += seg

print('RAW:', flag)
print('FLAG:', flag.rstrip(b'\x00').decode('latin1'))
