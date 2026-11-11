# Hyper512 solver v2: over-determined CryptoMiniSat + incremental model-exclusion.
# Checkpoints bad-model list to excl_N.json so restarts resume where killed.
# Env overrides: HYP_OUT (default output.txt), HYP_FLAG, HYP_EXCL (self-test mode).
import sys, time, json, os, ctypes
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)  # BELOW_NORMAL
except Exception:
    pass
import pycryptosat
from hashlib import sha256

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2048      # keystream bits used
MAXIT = int(sys.argv[2]) if len(sys.argv) > 2 else 1000000
OUTF = os.environ.get('HYP_OUT', 'output.txt')
FLAGF = os.environ.get('HYP_FLAG', 'flag_hyper512-hitcon_ctf2024.txt')
EXCLF = os.environ.get('HYP_EXCL', 'excl_%d.json' % N)

gift_hex, ct_hex = open(OUTF).read().split()
gift = bytes.fromhex(gift_hex); ct = bytes.fromhex(ct_hex)
MASKS = [0x6D6AC812F52A212D5A0B9F3117801FD5, 0xD736F40E0DED96B603F62CBE394FEF3D,
         0xA55746EF3955B07595ABC13B9EBEED6B, 0xD670201BAC7515352A273372B2A95B23]
TAPS = [[i for i in range(128) if m >> i & 1] for m in MASKS]
TMAX = [3*N+5, N+5, 4*N+5, 2*N+5]

nxt = [0]
def GV():
    nxt[0] += 1; return nxt[0]

bv = [[GV() for t in range(TMAX[r])] for r in range(4)]
statevars = [bv[r][i] for i in range(128) for r in range(4)]  # 512 key-order vars

s = pycryptosat.Solver()
for r in range(4):
    taps = TAPS[r]
    for t in range(TMAX[r]-128):
        s.add_xor_clause([bv[r][t+128]] + [bv[r][t+i] for i in taps], rhs=False)

def andg(a, b_):
    c = GV()
    s.add_clauses([[-a, -b_, c], [-a, b_, -c], [a, -b_, -c], [-c, a], [-c, b_]])
    return c

for n in range(N):
    kb = (gift[n//8] >> (7-(n % 8))) & 1
    x = GV()
    s.add_xor_clause([x] + [bv[0][3*n+i] for i in range(3)], rhs=False)
    y = bv[1][n]
    z = GV()
    s.add_xor_clause([z] + [bv[2][4*n+i] for i in range(4)], rhs=False)
    w = GV()
    s.add_xor_clause([w, bv[3][2*n], bv[3][2*n+1]], rhs=False)
    # VERIFIED ANF: f = y^z^xyz^yw^xyw^xzw = y ^ z ^ (xy)z ^ w*(y^xy^xz)
    pxy = andg(x, y)         # xy
    pxz = andg(x, z)         # xz
    v_ = andg(pxy, z)        # xyz
    s2 = GV()
    s.add_xor_clause([s2, y, pxy, pxz], rhs=False)   # y^xy^xz
    u = andg(w, s2)
    s.add_xor_clause([y, z, v_, u], rhs=bool(kb))

excl = []
if os.path.exists(EXCLF):
    excl = json.load(open(EXCLF))
for st in excl:
    k = int(st, 16)
    s.add_clause([-v if (k >> i) & 1 else v for i, v in enumerate(statevars)])
print(f'vars={nxt[0]} N={N} excl={len(excl)} solving...', flush=True)

class LFSR:
    def __init__(self, n_, key, mask):
        self.n = n_; self.state = key & ((1 << n_)-1); self.mask = mask
    def __call__(self):
        b = self.state & 1
        self.state = (self.state >> 1) | (((self.state & self.mask).bit_count() & 1) << (self.n-1))
        return b

def full_check(k):
    lfs = []; kk = k
    for r in range(4):
        lfs.append(LFSR(128, kk, MASKS[r])); kk >>= 128
    def nbit():
        x = lfs[0]() ^ lfs[0]() ^ lfs[0]()
        y = lfs[1]()
        z = lfs[2]() ^ lfs[2]() ^ lfs[2]() ^ lfs[2]()
        w = lfs[3]() ^ lfs[3]()
        return sha256(str(3*x+y+4*z+2*w+3142).encode()).digest()[0] & 1
    for n in range(len(gift)*8):
        if nbit() != (gift[n//8] >> (7-(n % 8))) & 1:
            return False
    flag = bytearray()
    for by in range(len(ct)):
        bacc = 0
        for i in range(8):
            bacc = (bacc << 1) | nbit()
        flag.append(ct[by] ^ bacc)
    return flag.decode(errors='replace')

t_start = time.time()
it = 0
while it < MAXIT:
    it += 1
    t0 = time.time()
    try:
        res = s.solve(bootstrap_rounds=200, threads=4)
    except TypeError:
        res = s.solve()
    dt = time.time()-t0
    if not res[0]:
        print('UNSAT after %d excl (elapsed %.0fs)' % (len(excl), time.time()-t_start), flush=True)
        sys.exit(2)
    model = res[1]
    def val(v): return model[v] if v > 0 else not model[-v]
    k = 0
    for i, v in enumerate(statevars):
        if val(v): k |= 1 << i
    r_ = full_check(k)
    if r_:
        print('KEY FOUND after %d iters (%.1fs total): %s' % (it, time.time()-t_start, hex(k)), flush=True)
        print('FLAG: %s' % r_.strip(), flush=True)
        open(FLAGF, 'w').write(r_.strip())
        sys.exit(0)
    excl.append(hex(k))
    json.dump(excl, open(EXCLF, 'w'))
    s.add_clause([-v if (k >> i) & 1 else v for i, v in enumerate(statevars)])
    print('iter %d: bad model (%.1fs solve, %.0f total), excl=%d' % (it, dt, time.time()-t_start, len(excl)), flush=True)
