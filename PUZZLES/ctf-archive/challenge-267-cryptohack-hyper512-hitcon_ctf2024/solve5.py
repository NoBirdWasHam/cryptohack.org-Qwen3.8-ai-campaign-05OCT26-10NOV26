# Hyper512 solver v5 (2026-11-02 SAT run): native-XOR CryptoMiniSat via pycryptosat 5.17.
# FIXES vs solve2.py: key-bit mapping was lane-INTERLEAVED (pos=i*4+r) while chall.py and
# full_check use lane-CONCATENATED keys (bits 128r+i) -> true model could never pass gift
# check. Now lane-major: bit 128*r+i of k = lane r state bit i. Adds confl_limit-chunked
# solve with conflicts/s logging, UNSAT-vs-budget discrimination, time cap.
import sys, time, json, os, ctypes
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
except Exception:
    pass
import pycryptosat
from hashlib import sha256

N    = int(os.environ.get('HYP_N', '8192'))
CAP  = float(os.environ.get('CAP', '10500'))
CHUNK = int(os.environ.get('CHUNK', '2000000'))
OUTF = os.environ.get('HYP_OUT', 'output.txt')
FLAGF = os.environ.get('HYP_FLAG', 'flag_hyper512-hitcon_ctf2024.txt')
EXCLF = os.environ.get('HYP_EXCL', 'excl5_%d.json' % N)
LOGF  = os.environ.get('LOG', 'solve5_%d.log' % N)

def L(msg):
    print(msg, flush=True)
    with open(LOGF, 'a') as f:
        f.write(msg + '\n')

gift_hex, ct_hex = open(OUTF).read().split()
gift = bytes.fromhex(gift_hex); ct = bytes.fromhex(ct_hex)
MASKS = [0x6D6AC812F52A212D5A0B9F3117801FD5, 0xD736F40E0DED96B603F62CBE394FEF3D,
         0xA55746EF3955B07595ABC13B9EBEED6B, 0xD670201BAC7515352A273372B2A95B23]
TAPS = [[i for i in range(128) if m >> i & 1] for m in MASKS]
TMAX = [3*N+3, N+1, 4*N+4, 2*N+2]

nxt = [0]
def GV():
    nxt[0] += 1; return nxt[0]

bv = [[GV() for t in range(TMAX[r])] for r in range(4)]
# LANE-MAJOR key mapping: position 128*r+i <-> lane r initial-state bit i (chall.py order)
statevars = [bv[r][i] for r in range(4) for i in range(128)]

s = pycryptosat.Solver()
for opt in (('mem', '3800'),):
    try:
        s.set_option(*opt); L('set_option %s ok' % (opt,))
    except Exception as e:
        L('set_option %s failed: %s' % (opt, e))

t_build = time.time()
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
    pxy = andg(x, y)
    pxz = andg(x, z)
    v_ = andg(pxy, z)
    s2 = GV()
    s.add_xor_clause([s2, y, pxy, pxz], rhs=False)
    u = andg(w, s2)
    s.add_xor_clause([y, z, v_, u], rhs=bool(kb))
L('build done: vars=%d N=%d in %.1fs' % (nxt[0], N, time.time()-t_build))

excl = []
if os.path.exists(EXCLF):
    excl = json.load(open(EXCLF))
for st in excl:
    k = int(st, 16)
    s.add_clause([-v if (k >> i) & 1 else v for i, v in enumerate(statevars)])
L('excl resumed: %d' % len(excl))

VK = os.environ.get('VERIFY_KEY')
if VK:
    k = int(open(VK).read().strip(), 16)
    assumps = [statevars[pos] if (k >> pos) & 1 else -statevars[pos] for pos in range(512)]
    rv = s.solve(assumptions=assumps)
    L('VERIFY_KEY solve under true-key assumptions -> %s %s' % (rv[0] if rv else None, 'OK-encoding-consistent' if rv and rv[0] else 'ENCODING-BUG'))
    sys.exit(0 if (rv and rv[0]) else (5 if rv and rv[0] is False else 6))

class LFSR:
    def __init__(self, n_, key, mask):
        self.n = n_; self.state = key & ((1 << n_)-1); self.mask = mask
    def __call__(self):
        b = self.state & 1
        self.state = (self.state >> 1) | (((self.state & self.mask).bit_count() & 1) << (self.n-1))
        return b

def full_check2(k):
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
    return flag

def conflicts():
    try:
        c = s.get_conflict()
        if isinstance(c, (list, tuple)):
            c = c[-1] if c else -1
        return int(c)
    except Exception:
        return -1

def conflicts():
    try:
        c = s.get_conflict()
        if isinstance(c, (list, tuple)):
            c = c[-1] if c else -1
        return int(c)
    except Exception:
        return -1

t_start = time.time(); prev_conf = conflicts(); it = 0
while time.time() - t_start < CAP:
    it += 1
    t0 = time.time()
    try:
        res = s.solve(confl_limit=CHUNK)
    except TypeError:
        res = s.solve()
    dt = time.time() - t0
    conf = conflicts()
    if conf >= 0 and prev_conf >= 0:
        L('chunk %d: %.1fs conf=%d rate=%.0f/s sat=%s' % (it, dt, conf, (conf-prev_conf)/max(dt,1e-9), res[0]))
    else:
        L('chunk %d: %.1fs sat=%s (no conf stat)' % (it, dt, res[0]))
    prev_conf = conf
    if res is None or res[0] is None:
        continue  # budget-limited UNKNOWN
    if res[0] is True:
        model = res[1]
        def val(v): return model[v] if v > 0 else not model[-v]
        k = 0
        for pos, v in enumerate(statevars):
            if val(v): k |= 1 << pos
        r_ = full_check2(k)
        if r_:
            L('KEY FOUND after %d chunks (%.1fs): %s' % (it, time.time()-t_start, hex(k)))
            flag = bytes(r_).decode(errors='replace')
            L('FLAG: %s' % flag)
            open(FLAGF, 'w').write(flag.strip())
            sys.exit(0)
        excl.append(hex(k))
        json.dump(excl, open(EXCLF, 'w'))
        s.add_clause([-v if (k >> i) & 1 else v for i, v in enumerate(statevars)])
        L('iter %d: bad model excluded, excl=%d' % (it, len(excl)))
    else:
        L('UNSAT proved after %d excl (%.0fs total)' % (len(excl), time.time()-t_start))
        sys.exit(2)
L('CAP reached %.0fs, %d chunks, UNKNOWN. conf=%s' % (time.time()-t_start, it, conflicts()))
sys.exit(3)
