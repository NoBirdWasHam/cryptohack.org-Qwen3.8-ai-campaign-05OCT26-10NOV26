# Hyper512 solver v3 — linearized attack (KLPP observation from mystiz writeup), no SAT.
# For every keystream bit k_i=1: (y_i+1)(z_i+1)=0  i.e.  y_i z_i + y_i + z_i = 1,
# where y_i = a_i . Y (LFSR2 init bits), z_i = b_i . Z (LFSR3 init bits).
# Linearize u_jk = Y_j*Z_k -> system over GF(2) in 16640 unknowns. Rank/kernel measured here.
import sys, os, time

MASKS = [0x6D6AC812F52A212D5A0B9F3117801FD5, 0xD736F40E0DED96B603F62CBE394FEF3D,
         0xA55746EF3955B07595ABC13B9EBEED6B, 0xD670201BAC7515352A273372B2A95B23]

OUTF = os.environ.get('HYP_OUT', 'output.txt')
gift_hex, ct_hex = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTF)).read().split()
gift = bytes.fromhex(gift_hex)
NB = len(gift) * 8

def state_masks(mask, n):
    """m[t] = 128-bit mask of initial-state bits defining output bit b[t] (LSB-first state)."""
    m = [1 << j for j in range(128)]
    for t in range(n - 128):
        acc = 0
        mm = mask
        while mm:
            lb = mm & -mm
            j = lb.bit_length() - 1
            acc ^= m[t + j]
            mm ^= lb
        m.append(acc)
    return m

t0 = time.time()
mA = state_masks(MASKS[1], NB)          # y_i = mA[i] . Y
m3 = state_masks(MASKS[2], 4 * NB + 3)  # z bits
mB = [m3[4 * i] ^ m3[4 * i + 1] ^ m3[4 * i + 2] ^ m3[4 * i + 3] for i in range(NB)]

# keystream bits of gift (gift = keystream xor zeros -> keystream = gift)
K1 = [i for i in range(NB) if (gift[i // 8] >> (7 - i % 8)) & 1]
print('k=1 positions:', len(K1), 'mask build %.1fs' % (time.time() - t0), flush=True)

NY = 16384           # u_jk at bit j*128+k
UY, UZ = 16384, 16512
RHS = 16640
NC = 16641

rows = []
t1 = time.time()
for i in K1:
    a = mA[i]; b = mB[i]
    r = 1 << RHS
    aa = a
    while aa:
        lb = aa & -aa
        j = lb.bit_length() - 1
        r ^= b << (j * 128)
        aa ^= lb
    r ^= a << UY
    r ^= b << UZ
    rows.append(r)
print('rows built %.1fs' % (time.time() - t1), flush=True)

# [flag — recorded in FLAGS/post-quantum/challenge-168-cryptohack-lwe-intro/flag.txt], pivot = lowest set bit (RHS col excluded from pivoting)
t2 = time.time()
piv = {}
rank = 0
for r in rows:
    while r and r != (1 << RHS):
        c = (r & -r).bit_length() - 1
        if c == RHS:
            break
        p = piv.get(c)
        if p is None:
            piv[c] = r
            rank += 1
            r = 0
        else:
            r ^= p
    if r == (1 << RHS):
        print('INCONSISTENT system!', flush=True)
        sys.exit(1)
print('rank=%d  unknowns=16640  kernel dim=%d  elim %.1fs' % (rank, 16640 - rank, time.time() - t2), flush=True)

# particular solution with free vars = 0 (back-substitute pivots in descending order)
pcols = sorted(piv)
val = 0  # bitset of assigned var values (cols)
for c in reversed(pcols):
    r = piv[c] & ~(1 << c)
    known = r & ((1 << RHS) - 1)
    v = (r >> RHS) & 1
    v ^= (known & val).bit_count() & 1
    if v:
        val |= 1 << c
print('particular solution popcount:', val.bit_count(), flush=True)

# kernel basis structure: for each free col f, basis vector via same back-sub
free = [c for c in range(NC - 1) if c not in piv]
print('free cols:', len(free), 'first:', free[:20], flush=True)

def basis_vec(f):
    v = 1 << f
    for c in reversed(pcols):
        r = piv[c] & ~((1 << (c + 1)))
        if (r & v).bit_count() & 1:
            v |= 1 << c
    return v

# structural probe on a few basis vectors
for f in free[:6] + free[-3:]:
    v = basis_vec(f)
    dY = (v >> UY) & ((1 << 128) - 1)
    dZ = (v >> UZ) & ((1 << 128) - 1)
    dU = v & ((1 << NY) - 1)
    # u support: which j-rows
    js = set()
    uu = dU
    while uu:
        lb = uu & -uu
        js.add((lb.bit_length() - 1) // 128)
        uu ^= lb
    print('free f=%d: wt(dY)=%d wt(dZ)=%d wt(dU)=%d dU-rows=%d' %
          (f, dY.bit_count(), dZ.bit_count(), dU.bit_count(), len(js)), flush=True)

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
import json
json.dump({'piv': {str(k): str(v) for k, v in piv.items()}, 'free': free, 'val': str(val),
           'giftlen': NB}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
           'elim_%s.json' % OUTF), 'w'))
print('saved elimination', 'total %.1fs' % (time.time() - t0), flush=True)
