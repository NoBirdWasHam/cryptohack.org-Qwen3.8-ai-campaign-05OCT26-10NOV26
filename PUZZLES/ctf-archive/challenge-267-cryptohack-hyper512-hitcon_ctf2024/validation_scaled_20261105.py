# Scaled VALIDATION of the re-derived intended path for hyper512 (2026-11-05).
# N=24 lanes / 1400 gift bits twin of the real cipher (same sha256 table + combiner).
# Demonstrates, in pure host Python (int-bitset GF2 elimination — the same engine as
# solve4), that:
#   stage 1: k=1-bit equations g=(1^y)(1^z)=0 linearized over y|z|yz monomials, with 3
#            fixed guess bits (y0,z0,z1), uniquely determine the LFSR2/LFSR3 states;
#   stage 2: substituting true y,z, ALL gift bits linearize over x|w|xw and recover
#            LFSR1/LFSR4 states; the reconstructed key reproduces the FULL gift.
# This is NOT the real instance (light validation only; solving the real one = solve6).
import random
from hashlib import sha256
random.seed(1234)
N = 24; NB = 1400
MASKS = [random.getrandbits(N) | 1 | (1 << (N - 1)) for _ in range(4)]

class LFSR:
    def __init__(s, n, key, mask):
        s.n = n; s.state = key & ((1 << n) - 1); s.mask = mask
    def __call__(s):
        b = s.state & 1
        s.state = (s.state >> 1) | (((s.state & s.mask).bit_count() & 1) << (s.n - 1))
        return b

T = [sha256(str(v + 3142).encode()).digest()[0] & 1 for v in range(11)]
def f(x, y, z, w): return T[3 * x + y + 4 * z + 2 * w]

key = random.getrandbits(4 * N)
k4 = [(key >> (r * N)) & ((1 << N) - 1) for r in range(4)]
def keystream(nb, ks):
    lfs = [LFSR(N, ks[r], MASKS[r]) for r in range(4)]; out = []
    for _ in range(nb):
        x = lfs[0]() ^ lfs[0]() ^ lfs[0](); y = lfs[1]()
        z = lfs[2]() ^ lfs[2]() ^ lfs[2]() ^ lfs[2](); w = lfs[3]() ^ lfs[3]()
        out.append(f(x, y, z, w))
    return out
K = keystream(NB, k4)

def smask(mask, n):
    m = [1 << j for j in range(N)]
    for t in range(n - N):
        acc = 0; mm = mask
        while mm:
            lb = mm & -mm; acc ^= m[t + lb.bit_length() - 1]; mm ^= lb
        m.append(acc)
    return m
mA = smask(MASKS[1], NB); m3 = smask(MASKS[2], 4 * NB + 3)
mB = [m3[4 * i] ^ m3[4 * i + 1] ^ m3[4 * i + 2] ^ m3[4 * i + 3] for i in range(NB)]
m1 = smask(MASKS[0], 3 * NB + 2); mX = [m1[3 * i] ^ m1[3 * i + 1] ^ m1[3 * i + 2] for i in range(NB)]
m4 = smask(MASKS[3], 2 * NB + 1); mW = [m4[2 * i] ^ m4[2 * i + 1] for i in range(NB)]
UY, UZ, RHS = N * N, N * N + N, N * N + 2 * N
K1 = [i for i in range(NB) if K[i]]
trueY, trueZ = k4[1], k4[2]

def elim(rows, rhs):
    piv = {}
    for r in rows:
        while r and r != (1 << rhs):
            c = (r & -r).bit_length() - 1
            if c == rhs: break
            p = piv.get(c)
            if p is None: piv[c] = r; r = 0
            else: r ^= p
        if r == (1 << rhs): return piv, True   # INCONSISTENT
    return piv, False

def backsub(piv, rhs):
    val = 0
    for c in sorted(piv, reverse=True):
        rr = piv[c] & ~((1 << c) | (1 << rhs))
        v = ((piv[c] >> rhs) & 1) ^ ((rr & val).bit_count() & 1)
        if v: val |= 1 << c
    return val

sols = []
for g in range(8):                       # guess y0, z0, z1 (tl2cents' 3-bit move)
    v1 = g & 1; v2 = (g >> 1) & 1; v3 = (g >> 2) & 1
    rows = []
    for i in K1:
        a = mA[i]; b = mB[i]
        a0 = a & 1; b0 = b & 1; b1 = (b >> 1) & 1
        p = a0 & v1; q = (b0 & v2) ^ (b1 & v3)   # removed parts of y and z linear forms
        rhs = 1 ^ p ^ q ^ (p & q)                # (1^y)(1^z)=0 with fixed bits moved out
        r = 0
        aa = a & ~1
        while aa:
            lb = aa & -aa; j = lb.bit_length() - 1
            if 1 ^ q: r ^= 1 << (UY + j)         # y_j coeff = a_j*(1^q)
            bb = b & ~3
            while bb:
                lb2 = bb & -bb; r ^= 1 << (j * N + lb2.bit_length() - 1)  # u_jk = a_j*b_k
                bb ^= lb2
            aa ^= lb
        if 1 ^ p:
            bb = b & ~3
            while bb:
                lb2 = bb & -bb; r ^= 1 << (UZ + lb2.bit_length() - 1)     # z_k coeff
                bb ^= lb2
        if rhs: r ^= 1 << RHS
        rows.append(r)
    piv, bad = elim(rows, RHS)
    if bad:
        print(f"guess {g}: INCONSISTENT"); continue
    val = backsub(piv, RHS)
    free_lin = [c for c in list(range(UY, UY + N)) + list(range(UZ, UZ + N)) if c not in piv]
    recY = sum(((val >> (UY + j)) & 1) << j for j in range(1, N)) | (v1 << 0)
    recZ = sum(((val >> (UZ + k2)) & 1) << k2 for k2 in range(2, N)) | v2 | (v3 << 1)
    ok = (recY == trueY and recZ == trueZ)
    print(f"guess {g}: rank={len(piv)} free_lin={len(free_lin)} yz_match={ok}")
    if ok: sols.append((recY, recZ))
print("consistent+matching guesses:", len(sols))
recY, recZ = sols[0]

# stage 2: ALL rows, linearize over x | w | xw with y,z substituted
RHS2 = 3 * N + N * N
rows = []
for i in range(NB):
    Y = (mA[i] & trueY).bit_count() & 1; Z = (mB[i] & trueZ).bit_count() & 1
    cx = Y & Z; cw = Y; cww = Y ^ Z
    r = 0
    if cww:
        a = mX[i]
        while a:
            lb = a & -a; j = lb.bit_length() - 1
            bb = mW[i]
            while bb:
                lb2 = bb & -bb; r ^= 1 << (3 * N + j * N + lb2.bit_length() - 1); bb ^= lb2
            a ^= lb
    if cx:
        a = mX[i]
        while a:
            lb = a & -a; r ^= 1 << (lb.bit_length() - 1); a ^= lb
    if cw:
        b = mW[i]
        while b:
            lb = b & -b; r ^= 1 << (2 * N + lb.bit_length() - 1); b ^= lb
    if Y ^ Z ^ K[i]: r ^= 1 << RHS2
    rows.append(r)
piv, bad = elim(rows, RHS2)
print("stage2 rows:", len(rows), "rank:", len(piv), "inconsistent:", bad)
val = backsub(piv, RHS2)
recX = sum(((val >> j) & 1) << j for j in range(N))
recW = sum(((val >> (2 * N + j)) & 1) << j for j in range(N))
print("x match:", recX == k4[0], " w match:", recW == k4[3])
rec = k4[0] | (recY << N) | (recZ << (2 * N)) | (recW << (3 * N))
K2 = keystream(NB, [(rec >> (r * N)) & ((1 << N) - 1) for r in range(4)])
print("FULL GIFT REPRODUCES:", K2 == K)
assert K2 == K
print("VALIDATION OK")
