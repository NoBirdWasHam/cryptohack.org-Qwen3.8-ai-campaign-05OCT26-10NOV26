# Hyper512 solver v4 — linearized attack (KLPP observation), no SAT.
# Stage 1: every k=1 bit forces y_i z_i + y_i + z_i = 1 (y=LFSR2 window, z=LFSR3 window of
#          initial states). Linearize u_jk=Y_j*Z_k -> GF(2) system, 16640 unknowns.
#          (y,z)-ambiguity = projection of kernel onto y,z blocks -> enumerate + filter.
# Stage 2: with (y,z,k) known, truth table gives exact LINEAR constraints on x,w (LFSR1/4).
# Verify full gift, decrypt flag. Env: HYP_OUT, HYP_FLAG.
import sys, os, time, pickle
sys.set_int_max_str_digits(2000000)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MASKS = [0x6D6AC812F52A212D5A0B9F3117801FD5, 0xD736F40E0DED96B603F62CBE394FEF3D,
         0xA55746EF3955B07595ABC13B9EBEED6B, 0xD670201BAC7515352A273372B2A95B23]
OUTF = os.environ.get('HYP_OUT', 'output.txt')
FLAGF = os.environ.get('HYP_FLAG', 'flag_hyper512-hitcon_ctf2024.txt')

gift_hex, ct_hex = open(os.path.join(HERE, OUTF)).read().split()
gift = bytes.fromhex(gift_hex)
ct = bytes.fromhex(ct_hex)
NB = len(gift) * 8
gift_bits = [(gift[i // 8] >> (7 - i % 8)) & 1 for i in range(NB)]
K1 = [i for i in range(NB) if gift_bits[i]]

def state_masks(mask, n):
    m = [1 << j for j in range(128)]
    for t in range(n - 128):
        acc = 0
        mm = mask
        while mm:
            lb = mm & -mm
            acc ^= m[t + lb.bit_length() - 1]
            mm ^= lb
        m.append(acc)
    return m

UY, UZ, RHS = 16384, 16512, 16640
t0 = time.time()
mA = state_masks(MASKS[1], NB)
m3 = state_masks(MASKS[2], 4 * NB + 3)
mB = [m3[4 * i] ^ m3[4 * i + 1] ^ m3[4 * i + 2] ^ m3[4 * i + 3] for i in range(NB)]

CACHE = os.path.join(HERE, 'elim_%s.pkl' % OUTF)
if os.path.exists(CACHE):
    piv, free, val = pickle.load(open(CACHE, 'rb'))
    print('cached elim: rank=%d free=%d' % (len(piv), len(free)), flush=True)
else:
    rows = []
    for i in K1:
        a = mA[i]; b = mB[i]
        r = (1 << RHS) | (a << UY) | (b << UZ)
        aa = a
        while aa:
            lb = aa & -aa
            r ^= b << ((lb.bit_length() - 1) * 128)
            aa ^= lb
        rows.append(r)
    K0N = [i for i in range(NB) if not gift_bits[i]]
    for i in K0N:
        a = mA[i]; b = mB[i]
        r = 0
        aa = a
        while aa:
            lb = aa & -aa
            r ^= b << ((lb.bit_length() - 1) * 128)
            aa ^= lb
        rows.append(r)  # exact annihilator at k=0: u_block = 0 (no linear, no const)
    print('rows built %.1fs' % (time.time() - t0), flush=True)
    piv = {}
    for r in rows:
        while r and r != (1 << RHS):
            c = (r & -r).bit_length() - 1
            p = piv.get(c)
            if p is None:
                piv[c] = r; r = 0
            else:
                r ^= p
        if r == (1 << RHS):
            print('INCONSISTENT!', flush=True); sys.exit(1)
    free = [c for c in range(RHS) if c not in piv]
    val = 0
    for c in sorted(piv, reverse=True):
        rr = piv[c] & ((1 << RHS) - 1)
        v = (piv[c] >> RHS) & 1
        v ^= (rr & ~(1 << c) & val).bit_count() & 1
        if v:
            val |= 1 << c
    print('rank=%d kernel dim=%d elim %.1fs' % (len(piv), len(free), time.time() - t0), flush=True)
    pickle.dump((piv, free, val), open(CACHE, 'wb'))

pcols = sorted(piv)

def basis_vec(f):
    v = 1 << f
    for c in reversed(pcols):
        hi = piv[c] & ~((1 << (c + 1)) - 1)   # bits strictly above pivot c (RHS bit never in v)
        if (hi & v).bit_count() & 1:
            v |= 1 << c
    return v

proj = []
for f in free:
    v = basis_vec(f)
    dYZ = (v >> UY) & ((1 << 256) - 1)
    if dYZ:
        proj.append(dYZ)
pb = {}
for p in proj:
    r = p
    while r:
        c = (r & -r).bit_length() - 1
        if c in pb:
            r ^= pb[c]
        else:
            pb[c] = r
            break
proj_basis = [pb[c] for c in sorted(pb)]
print('kernel vecs with yz-part: %d independent: %d' % (len(proj), len(proj_basis)), flush=True)

Y0 = (val >> UY) & ((1 << 128) - 1)
Z0 = (val >> UZ) & ((1 << 128) - 1)

def testYZ(Y, Z):
    for i in K1:
        if ((mA[i] & Y).bit_count() | (mB[i] & Z).bit_count()) & 1 == 0:
            return False
    return True

d = len(proj_basis)
print('(y,z) ambiguity dim = %d' % d, flush=True)
while d > 20:
    # guess one free yz var = 0 (true w.p. 1/2): re-eliminate with unit row.
    # Wrong guess -> inconsistent (cheap reject). Keeps half-space containing truth.
    f = free_yz_last
    unit = (1 << f) | (1 << RHS)
    rp = unit
    bad = False
    while rp:
        c = (rp & -rp).bit_length() - 1
        if c == RHS:
            bad = True; break
        p = piv.get(c)
        if p is None:
            piv[c] = rp; rp = 0
        else:
            rp ^= p
    if bad:
        print('guess %d=0 inconsistent -> truth has it 1: set val bit, drop free col' % f, flush=True)
        val |= 1 << f
    else:
        free.remove(f)
        print('guess %d=0 consistent (kept halfspace)' % f, flush=True)
    val &= ~(1 << f)  # recompute particular below anyway
    # recompute particular solution
    pcols = sorted(piv)
    val = 0
    for c in reversed(pcols):
        rr = piv[c] & ((1 << RHS) - 1)
        vv = (piv[c] >> RHS) & 1
        vv ^= (rr & ~(1 << c) & val).bit_count() & 1
        if vv:
            val |= 1 << c
    def basis_vec(f):
        v = 1 << f
        for c in reversed(pcols):
            hi = piv[c] & ~((1 << (c + 1)) - 1)
            if (hi & v).bit_count() & 1:
                v |= 1 << c
        return v
    proj = []
    for f_ in free:
        v = basis_vec(f_)
        dYZ = (v >> UY) & ((1 << 256) - 1)
        if dYZ:
            proj.append(dYZ)
    pb = {}
    for p in proj:
        r_ = p
        while r_:
            c = (r_ & -r_).bit_length() - 1
            if c in pb:
                r_ ^= pb[c]
            else:
                pb[c] = r_; break
    proj_basis = [pb[c] for c in sorted(pb)]
    Y0 = (val >> UY) & ((1 << 128) - 1)
    Z0 = (val >> UZ) & ((1 << 128) - 1)
    d = len(proj_basis)
    free_yz_last = max([f_ for f_ in free if ((1 << f_) & (0 if False else (1 << 256))) and f_ >= UY] or [max(free)])
    print('after guess: dim=%d' % d, flush=True)
    if d == len(proj_basis) and piv.get(f) is not None:
        pass
sols = []
cur = Y0 | (Z0 << 128)
prev = 0
for t in range(1 << d):
    if t:
        g = t ^ (t >> 1)
        diff = g ^ prev; prev = g
        cur ^= proj_basis[diff.bit_length() - 1]
    Y = cur & ((1 << 128) - 1); Z = cur >> 128
    if testYZ(Y, Z):
        sols.append((Y, Z))
print('YZ survivors: %d (%.1fs)' % (len(sols), time.time() - t0), flush=True)
if not sols:
    sys.exit(4)

# stage 2: linear constraints on X (LFSR1) and W (LFSR4)
m0 = state_masks(MASKS[0], 3 * NB + 2)
m4 = state_masks(MASKS[3], 2 * NB + 1)
xmask = [m0[3 * i] ^ m0[3 * i + 1] ^ m0[3 * i + 2] for i in range(NB)]
wmask = [m4[2 * i] ^ m4[2 * i + 1] for i in range(NB)]

class LFSR:
    def __init__(self, n_, key, mask):
        self.n = n_; self.state = key & ((1 << n_) - 1); self.mask = mask
    def __call__(self):
        b = self.state & 1
        self.state = (self.state >> 1) | (((self.state & self.mask).bit_count() & 1) << (self.n - 1))
        return b

def full_check(k):
    from hashlib import sha256
    lfs = []; kk = k
    for r in range(4):
        lfs.append(LFSR(128, kk, MASKS[r])); kk >>= 128
    def nbit():
        x = lfs[0]() ^ lfs[0]() ^ lfs[0]()
        y = lfs[1]()
        z = lfs[2]() ^ lfs[2]() ^ lfs[2]() ^ lfs[2]()
        w = lfs[3]() ^ lfs[3]()
        return sha256(str(3 * x + y + 4 * z + 2 * w + 3142).encode()).digest()[0] & 1
    for n in range(NB):
        if nbit() != gift_bits[n]:
            return None
    flag = bytearray()
    for by in range(len(ct)):
        bacc = 0
        for _ in range(8):
            bacc = (bacc << 1) | nbit()
        flag.append(ct[by] ^ bacc)
    return bytes(flag)

def solve_xw(Y, Z):
    piv2 = {}
    for i in range(NB):
        yb = (mA[i] & Y).bit_count() & 1
        zb = (mB[i] & Z).bit_count() & 1
        kb = gift_bits[i]
        eqs = []
        if (yb, zb) == (0, 1):
            if kb == 0: eqs = [(xmask[i], 0, 1), (0, wmask[i], 1)]   # x=1, w=1
            else:       eqs = [(xmask[i], 0, 0)]                      # x=0
        elif (yb, zb) == (1, 0):
            if kb == 0: eqs = [(xmask[i], 0, 0), (0, wmask[i], 1)]   # x=0, w=1
            else:       eqs = [(0, wmask[i], 0)]                      # w=0
        elif (yb, zb) == (1, 1):
            if kb == 0: eqs = [(xmask[i], wmask[i], 0)]              # x+w=0
            else:       eqs = [(xmask[i], wmask[i], 1)]              # x+w=1
        for mx, mw, rhs in eqs:
            r = mx | (mw << 128) | (rhs << 256)
            while r and r != (1 << 256):
                c = (r & -r).bit_length() - 1
                p = piv2.get(c)
                if p is None:
                    piv2[c] = r; r = 0
                else:
                    r ^= p
            if r == (1 << 256):
                return None
    vals = 0
    for c in sorted(piv2, reverse=True):
        rr = piv2[c] & ((1 << 256) - 1)
        v = (piv2[c] >> 256) & 1
        v ^= (rr & ~(1 << c) & vals).bit_count() & 1
        if v:
            vals |= 1 << c
    return vals

for (Y, Z) in sols:
    vals = solve_xw(Y, Z)
    if vals is None:
        print('xw inconsistent for a survivor', flush=True); continue
    X = vals & ((1 << 128) - 1); W = (vals >> 128) & ((1 << 128) - 1)
    k = X | (Y << 128) | (Z << 256) | (W << 384)
    fl = full_check(k)
    if fl:
        print('KEY:', hex(k), flush=True)
        print('FLAG:', fl.decode(errors='replace'), flush=True)
        open(os.path.join(HERE, FLAGF), 'w').write(fl.decode(errors='replace'))
        sys.exit(0)
print('no survivor passed full check', flush=True)
sys.exit(5)
