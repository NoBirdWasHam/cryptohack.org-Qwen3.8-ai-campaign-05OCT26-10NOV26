# v3 solver: exact modulus per block, collision-aware CRT, Hastad root, AES decrypt.
import os, sys
import gmpy2
from gmpy2 import mpz, iroot, gcd, invert
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import solve

HERE = os.path.dirname(os.path.abspath(__file__))
E = 65537

def build_L(lim=8192, cap=1 << 24):
    L = 1
    sieve = bytearray([1]) * lim
    sieve[0] = sieve[1] = 0
    for i in range(2, int(lim ** 0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    import math
    for p in range(3, lim):
        if sieve[p]:
            e = int(math.log2(cap) / math.log2(p))
            L *= p ** e
    return L

def divisors(n):
    # n is small-ish (< 2^30 typical); return all divisors
    out = [1]
    m = n
    d = 3
    while d * d <= m:
        if m % d == 0:
            a = 1
            pw = d
            while m % d == 0:
                m //= d
                pw *= d if m % d == 0 else pw  # placeholder
            # simpler: redo
            a = 0
            pw = 1
            while n % (d ** (a + 1)) == 0:
                a += 1
                pw *= d
            cur = [pw]
            # build powers
            powers = [d ** i for i in range(1, a + 1)]
            new = []
            for o in out:
                new.append(o)
                for q in powers:
                    new.append(o * q)
            out = new
        d += 2
    if m > 1:
        out = out + [m * o for o in out]
    return out

def main():
    L = build_L()
    fc, blocks = solve.parse(os.path.join(HERE, 'transcript.log'))
    two_e = mpz(2) ** E
    three_e = mpz(3) ** E
    mods, cbs, info = [], [], []
    for k, (c2, c3, cb) in enumerate(blocks):
        g = int(gcd(two_e - c2, three_e - c3))
        op = g >> ((g & -g).bit_length() - 1)
        Sc = int(gcd(mpz(op), mpz(L)))
        best = None
        for t in divisors(Sc):
            if op % t:
                continue
            cand = op // t
            bl = cand.bit_length()
            if 1022 <= bl <= 1024 and cand > cb:
                if pow(2, E, cand) == c2 and pow(3, E, cand) == c3:
                    if best is None or cand < best:
                        best = cand
        if best is None:
            info.append(k)
            continue
        mods.append(mpz(best)); cbs.append(mpz(cb))
    print('kept', len(mods), 'zero-cand blocks:', info, flush=True)

    # collision-aware CRT
    R = mpz(cbs[0]); M = mpz(mods[0])
    used = 1
    for m, c in zip(mods[1:], cbs[1:]):
        g = gcd(M, m)
        if g > 1:
            # m shares a factor (prime collision or spurious s leftover)
            m2 = m // g
            if m2 == 1 or m2.bit_length() < 200:
                continue
            m = m2
            c = c % m
        try:
            t = ((c - R) % m) * invert(M % m, m) % m
        except ZeroDivisionError:
            continue
        R += M * t
        M *= m
        used += 1
    R %= M
    print('CRT done used', used, 'R bits', R.bit_length(), 'M bits', M.bit_length(), flush=True)

    root, exact = iroot(R, E)
    print('iroot exact?', exact, 'root bits', root.bit_length(), flush=True)
    if not exact:
        for d in (-1, 0, 1):
            x = root + d
            if x > 0 and x ** E == R:
                root = x; exact = True
                break
    if not exact:
        sys.exit('R not perfect 65537th power -> insufficient product (need more/cleaner moduli)')

    # full verification
    fails = [i for i in range(len(mods)) if pow(root, E, mods[i]) != cbs[i] and int(mods[i]) > 1]
    print('full pow-verify failures:', len(fails), fails[:10], flush=True)
    ms = root
    msb = int(ms).to_bytes(32, 'big') if ms.bit_length() <= 256 else None
    if msb is None:
        sys.exit('root too big for a 32-byte master secret')
    pt = unpad(AES.new(msb, AES.MODE_CBC, b'\0' * 16).decrypt(fc), 16)
    print('FLAG:', pt.decode(), flush=True)
    with open(os.path.join(HERE, 'flag_key_backup_service_2-hkcert_c.txt'), 'w') as f:
        f.write(pt.decode().strip() + '\n')
    with open(os.path.join(HERE, 'ms_hex.txt'), 'w') as f:
        f.write(msb.hex() + '\n')

if __name__ == '__main__':
    main()
