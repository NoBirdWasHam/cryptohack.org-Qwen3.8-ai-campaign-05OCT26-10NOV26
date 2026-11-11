#!/usr/bin/env python
# solve6.py — hyper512 (nn=267) via the PUBLISHED TWO-STAGE LINEARIZATION (tl2cents path),
# host-validated on a scaled twin by validation_scaled_20261105.py (FULL GIFT REPRODUCES).
# Stage 1: every k=1 gift bit forces (1^y_i)(1^z_i)=0; linearize u_jk=Y_j*Z_k over the
#   restricted columns (guessing y_0,z_0,z_1 removes linear cols y0,z0,z1 and monomials
#   touching them: 16255 active cols < ~16.3k rows -> overdetermined + unique for the
#   true guess). 8 independent guesses run in a multiprocessing pool (the row linear
#   forms depend per-row on the guess, so no shared elimination is possible).
# Stage 2: substitute y,z; every gift bit linearizes over x | w | xw -> raw lane1+lane4
#   states. Full key = X | Y<<128 | Z<<256 | W<<384 (lane-concatenated, chall.py order).
#   Full-gift check with the exact sha256 combiner, then decrypt ct.
# Provenance (cited): tl2cents.github.io HITCON-CTF-2024-Qual writeup +
#   github tl2cents/CTF-Writeups/2024/HITCON-Qual/hyper512; author solution
#   github maple3142/My-CTF-Challenges HITCON CTF 2024/Hyper512 (README + solution).
# Usage: python solve6.py [output_file] [key_test.txt-to-compare]
import sys, os, time
sys.set_int_max_str_digits(2000000)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hashlib import sha256

MASKS = [0x6D6AC812F52A212D5A0B9F3117801FD5, 0xD736F40E0DED96B603F62CBE394FEF3D,
         0xA55746EF3955B07595ABC13B9EBEED6B, 0xD670201BAC7515352A273372B2A95B23]
N = 128
UY, UZ, RHS = N * N, N * N + N, N * N + 2 * N     # stage-1 layout (RHS col = 16640)
RHS2 = 3 * N + N * N                               # stage-2 RHS col
_M = {}

def state_masks(mask, n):
    m = [1 << j for j in range(N)]
    for t in range(n - N):
        acc = 0
        mm = mask
        while mm:
            lb = mm & -mm
            acc ^= m[t + lb.bit_length() - 1]
            mm ^= lb
        m.append(acc)
    return m

def init_worker(K1, NB):
    _M['K1'] = K1; _M['NB'] = NB
    _M['mA'] = state_masks(MASKS[1], NB)
    m3 = state_masks(MASKS[2], 4 * NB + 3)
    _M['mB'] = [m3[4 * i] ^ m3[4 * i + 1] ^ m3[4 * i + 2] ^ m3[4 * i + 3] for i in range(NB)]

def elim(rows):
    piv = {}
    for r in rows:
        while r and r != (1 << RHS):
            c = (r & -r).bit_length() - 1
            if c == RHS:
                break
            p = piv.get(c)
            if p is None:
                piv[c] = r; r = 0
            else:
                r ^= p
        if r == (1 << RHS):
            return piv, True
    return piv, False

def backsub(piv):
    val = 0
    for c in sorted(piv, reverse=True):
        rr = piv[c] & ~((1 << c) | (1 << RHS))
        v = ((piv[c] >> RHS) & 1) ^ ((rr & val).bit_count() & 1)
        if v:
            val |= 1 << c
    return val

def stage1_guess(g):
    t0 = time.time()
    K1 = _M['K1']; mA = _M['mA']; mB = _M['mB']
    v1 = g & 1; v2 = (g >> 1) & 1; v3 = (g >> 2) & 1
    rows = []
    for i in K1:
        a = mA[i]; b = mB[i]
        a0 = a & 1; b0 = b & 1; b1 = (b >> 1) & 1
        p = a0 & v1
        q = (b0 & v2) ^ (b1 & v3)
        rhs = 1 ^ p ^ q ^ (p & q)
        bb = b & ~3
        r = 0
        aa = a & ~1
        while aa:
            lb = aa & -aa
            r ^= bb << ((lb.bit_length() - 1) * N)
            aa ^= lb
        if 1 ^ q:
            r ^= (a & ~1) << UY
        if 1 ^ p:
            r ^= bb << UZ
        if rhs:
            r ^= 1 << RHS
        rows.append(r)
    piv, bad = elim(rows)
    free_lin = [c for c in list(range(UY, UY + N)) + list(range(UZ, UZ + N)) if c not in piv]
    out = dict(g=g, bad=bad, rank=len(piv), free_lin=len(free_lin), secs=time.time() - t0)
    if not bad:
        val = backsub(piv)
        recY = sum(((val >> (UY + j)) & 1) << j for j in range(1, N)) | v1
        recZ = sum(((val >> (UZ + k)) & 1) << k for k in range(2, N)) | v2 | (v3 << 1)
        out['Y'] = recY; out['Z'] = recZ
    return out

def stage2(Y, Z, gift_bits, NB):
    mA = _M['mA']; mB = _M['mB']
    if 'mX' not in _M:
        m0 = state_masks(MASKS[0], 3 * NB + 2)
        m4 = state_masks(MASKS[3], 2 * NB + 1)
        _M['mX'] = [m0[3 * i] ^ m0[3 * i + 1] ^ m0[3 * i + 2] for i in range(NB)]
        _M['mW'] = [m4[2 * i] ^ m4[2 * i + 1] for i in range(NB)]
    mX = _M['mX']; mW = _M['mW']
    piv = {}
    for i in range(NB):
        Yb = (mA[i] & Y).bit_count() & 1
        Zb = (mB[i] & Z).bit_count() & 1
        cx = Yb & Zb; cw = Yb; cww = Yb ^ Zb
        r = 0
        if cww:
            a = mX[i]; bw = mW[i]
            while a:
                lb = a & -a
                r ^= bw << (3 * N + (lb.bit_length() - 1) * N)
                a ^= lb
        if cx:
            r ^= mX[i]
        if cw:
            r ^= mW[i] << (2 * N)
        if Yb ^ Zb ^ gift_bits[i]:
            r ^= 1 << RHS2
        while r and r != (1 << RHS2):
            c = (r & -r).bit_length() - 1
            if c == RHS2:
                break
            p = piv.get(c)
            if p is None:
                piv[c] = r; r = 0
            else:
                r ^= p
        if r == (1 << RHS2):
            return None, len(piv)
    val = 0
    for c in sorted(piv, reverse=True):
        rr = piv[c] & ~((1 << c) | (1 << RHS2))
        v = ((piv[c] >> RHS2) & 1) ^ ((rr & val).bit_count() & 1)
        if v:
            val |= 1 << c
    recX = val & ((1 << N) - 1)
    recW = (val >> (2 * N)) & ((1 << N) - 1)
    return (recX, recW), len(piv)

class LFSR:
    def __init__(self, n_, key, mask):
        self.n = n_; self.state = key & ((1 << n_) - 1); self.mask = mask
    def __call__(self):
        b = self.state & 1
        self.state = (self.state >> 1) | (((self.state & self.mask).bit_count() & 1) << (self.n - 1))
        return b

T = [sha256(str(v + 3142).encode()).digest()[0] & 1 for v in range(11)]

def full_check(k, gift_bits, ct):
    lfs = []; kk = k
    for r in range(4):
        lfs.append(LFSR(128, kk, MASKS[r])); kk >>= 128
    def nbit():
        x = lfs[0]() ^ lfs[0]() ^ lfs[0]()
        y = lfs[1]()
        z = lfs[2]() ^ lfs[2]() ^ lfs[2]() ^ lfs[2]()
        w = lfs[3]() ^ lfs[3]()
        return sha256(str(3 * x + y + 4 * z + 2 * w + 3142).encode()).digest()[0] & 1
    for n in range(len(gift_bits)):
        if nbit() != gift_bits[n]:
            return None
    flag = bytearray()
    for by in range(len(ct)):
        bacc = 0
        for _ in range(8):
            bacc = (bacc << 1) | nbit()
        flag.append(ct[by] ^ bacc)
    return bytes(flag)

def main():
    args = [a for a in sys.argv[1:]]
    OUTF = args[0] if args else 'output_live.txt'
    CMPKEY = args[1] if len(args) > 1 else None
    t0 = time.time()
    def log(msg): print('[%7.1fs] %s' % (time.time() - t0, msg), flush=True)
    gift_hex, ct_hex = open(os.path.join(HERE, OUTF)).read().split()
    gift = bytes.fromhex(gift_hex)
    ct = bytes.fromhex(ct_hex)
    NB = len(gift) * 8
    gift_bits = [(gift[i // 8] >> (7 - i % 8)) & 1 for i in range(NB)]
    K1 = [i for i in range(NB) if gift_bits[i]]
    log(f'instance {OUTF}: NB={NB} k=1 rows={len(K1)} ct={len(ct)}B')

    results = []
    try:
        import multiprocessing as mp
        ctx = mp.get_context('spawn')
        with ctx.Pool(4, initializer=init_worker, initargs=(K1, NB)) as pool:
            for res in pool.imap_unordered(stage1_guess, range(8)):
                log('stage1 guess %d: bad=%s rank=%d free_lin=%d (%.0fs)'
                    % (res['g'], res['bad'], res['rank'], res['free_lin'], res['secs']))
                results.append(res)
    except Exception as e:
        log('pool failed (%s); sequential fallback' % e)
        init_worker(K1, NB)
        for g in range(8):
            res = stage1_guess(g)
            log('stage1 guess %d: bad=%s rank=%d free_lin=%d (%.0fs)'
                % (res['g'], res['bad'], res['rank'], res['free_lin'], res['secs']))
            results.append(res)

    surv = sorted([r for r in results if not r['bad']], key=lambda r: -r['rank'])
    log('stage1 consistent guesses: %s' % [r['g'] for r in surv])
    if not surv:
        log('NO consistent guess — abort'); sys.exit(2)
    if 'mA' not in _M:                      # pool ran in workers only; parent needs masks for stage2
        log('building stage2 masks in parent...')
        init_worker(K1, NB)
    for r in surv:
        Y, Z = r['Y'], r['Z']
        (xwres, rank2) = stage2(Y, Z, gift_bits, NB)
        if xwres is None:
            log('guess %d: stage2 inconsistent' % r['g']); continue
        X, W = xwres
        k = X | (Y << 128) | (Z << 256) | (W << 384)
        fl = full_check(k, gift_bits, ct)
        log('guess %d: stage2 rank=%d X=%032x W=%032x full_check=%s'
            % (r['g'], rank2, X, W, 'PASS' if fl else 'fail'))
        if fl:
            log('KEY: 0x%0128x' % k)
            log('FLAG: %s' % fl.decode(errors='replace'))
            with open(os.path.join(HERE, 'flag_hyper512-hitcon_ctf2024.txt'), 'w') as fh:
                fh.write(fl.decode(errors='replace'))
            if CMPKEY:
                planted = int(open(os.path.join(HERE, CMPKEY)).read().strip(), 16)
                log('KEY MATCH vs %s: %s' % (CMPKEY, planted == k))
            sys.exit(0)
    log('no survivor passed full check'); sys.exit(5)

if __name__ == '__main__':
    main()
