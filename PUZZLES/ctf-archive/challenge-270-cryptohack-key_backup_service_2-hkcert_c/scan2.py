# Build per-block candidate true moduli from g = gcd(2^e-c2, 3^e-c3) = s * n_real.
# n_real must: be odd, 1022<=bits<=1024, > cb, and satisfy pow(2,e,n)==c2, pow(3,e,n)==c3.
# s's odd part is found by trial division of odd(g) with primes <= 2e6, enumerating
# divisors t whose cand = op//t lands in the allowed window.
import json, os
import solve
from gmpy2 import mpz, gcd

E = 65537
HERE = os.path.dirname(os.path.abspath(__file__))

def small_primes(lim):
    sieve = bytearray([1]) * lim
    sieve[0] = sieve[1] = 0
    for i in range(2, int(lim ** 0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i in range(3, lim) if sieve[i]]

def divisors_from_fac(fac, lo, hi):
    # enumerate divisors t of product(p^a) with lo <= t <= hi (python ints)
    out = [1]
    for p, a in fac:
        new = []
        mul = 1
        for e in range(a + 1):
            for d in out:
                v = d * mul
                if lo <= v <= hi:
                    new.append(v)
                if v > hi:
                    break
            mul *= p
            if mul > hi:
                break
        out = sorted(set(new)) if new else [1]
        if not out:
            return []
    return [d for d in out if lo <= d <= hi]

def main():
    fc, blocks = solve.parse(os.path.join(HERE, 'transcript.log'))
    two_e = mpz(2) ** E
    three_e = mpz(3) ** E
    primes = small_primes(2000000)
    results = []  # list of list-of-candidates (int)
    for k, (c2, c3, cb) in enumerate(blocks):
        g = int(gcd(two_e - c2, three_e - c3))
        op = g >> ((g & -g).bit_length() - 1)  # odd part
        # window for t: cand = op//t in (cb, 2^1024], so  op/2^1024 <= t <= op/cb
        lo = max(1, op >> 1024)
        hi = op // max(cb, 1)
        if hi > op:
            hi = op
        # factor out small primes from op (enough to cover t)
        m = op
        fac = []
        for p in primes:
            if p * p > m and m > 1 and p > 5000 and len(fac) >= 8:
                break
            if p > hi:
                break
            if m % p == 0:
                a = 0
                while m % p == 0:
                    m //= p
                    a += 1
                fac.append((p, a))
        ts = divisors_from_fac(fac, lo, hi)
        cands = []
        for t in ts:
            if op % t:
                continue
            cand = op // t
            bl = cand.bit_length()
            if 1022 <= bl <= 1024 and cand > cb and pow(2, E, cand) == c2 and pow(3, E, cand) == c3:
                cands.append(cand)
        results.append(cands)
        if k % 2000 == 0:
            print('k', k, 'ncand', len(cands), flush=True)
    counts = {1: 0, 2: 0, 3: 0, 0: 0, 'other': 0}
    for cs in results:
        key = len(cs) if len(cs) <= 3 else 'other'
        counts[key] += 1
    print('candidate-count histogram:', counts, flush=True)
    with open(os.path.join(HERE, 'cands.json'), 'w') as f:
        json.dump([[hex(x) for x in cs] for cs in results], f)
    print('saved cands.json', flush=True)

if __name__ == '__main__':
    main()
