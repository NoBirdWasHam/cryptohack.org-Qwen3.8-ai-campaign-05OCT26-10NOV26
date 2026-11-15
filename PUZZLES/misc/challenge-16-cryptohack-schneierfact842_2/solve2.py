# schneierfact842_2 solver v2: minimize password length (<1024 bytes msg limit).
# Multiset of odd codes ≡1 mod 4; prod ≡ sum (mod 2^64), sum prime.
# Sum-preserving swaps -> linear congruence in log5 -> small-k via CVP.
import sys, math, random
sys.path.insert(0, ".")
from mathlib import M, log5, v2
from Crypto.Util.number import isPrime

def swaps_for(pool):
    from itertools import combinations
    bysum = {}
    for a, b in combinations(pool, 2):
        bysum.setdefault(a + b, []).append((a, b))
    out = []
    for s, pairs in sorted(bysum.items()):
        for (a, b), (c, d) in combinations(pairs, 2):
            v = {a: 1, b: 1, c: -1, d: -1}
            rho = a * b % M * pow(c * d % M, -1, M) % M
            if rho == 1:
                continue
            lam = log5(rho)
            out.append((v, rho, lam))
    return out

def build_base(pool, INV):
    b = {c: INV for c in pool}
    S0 = sum(c * n for c, n in b.items())
    p0 = 1
    for c, n in b.items():
        p0 = p0 * pow(c, n, M) % M
    # adjust with d1 copies of '1'(49) and d2 copies of 'a'(97): both ≡1 mod16,
    # so p stays ≡p0 mod16; need S≡p0 mod16 -> (d1+d2) ≡ p0-S0 mod16.
    c16 = (p0 - S0) % 16
    best = None
    for t in range(c16, 200, 16):          # t = d1+d2
        for d2 in range(t + 1):            # S = S0 + 49t + 48*d2
            S = S0 + 49 * t + 48 * d2
            if isPrime(S):
                best = (t - d2, d2, S)
                break
        if best:
            break
    if best is None:
        return None
    d1, d2, S = best
    b[49] += d1
    if 97 in b:
        b[97] += d2
    else:
        b[97] = d2
    p = p0 * pow(49, d1, M) % M * pow(97, d2, M) % M
    assert S % 16 == p % 16 and isPrime(S)
    return b, S, p

def try_solve(pool, INV, J, seed):
    random.seed(seed)
    bb = build_base(pool, INV)
    if bb is None:
        return None
    b, S, p_base = bb
    T = log5(S * pow(p_base, -1, M) % M)
    if T % 4:
        return None
    d = 2
    Mp = 1 << (62 - d)
    Tp = T >> d
    sw = [x for x in swaps_for(pool) if v2(x[2]) == d]
    if len(sw) < J:
        return None
    from fpylll import IntegerMatrix, BKZ, CVP
    for attempt in range(60):
        chosen = random.sample(sw, J)
        lam = [l >> d for _, _, l in chosen]
        if Tp % math.gcd(math.gcd(*lam), Mp):
            continue
        dim = J + 1
        A = IntegerMatrix(dim, dim)
        A[0, 0] = Mp
        for j in range(J):
            A[1 + j, 0] = lam[j]
            A[1 + j, 1 + j] = 1
        BKZ.reduction(A, BKZ.EasyParam(40))
        try:
            v = CVP.closest_vector(A, [Tp] + [0] * J)
            kk = [int(v[1 + j]) for j in range(J)]
            if (sum(lam[j] * kk[j] for j in range(J)) - Tp) % Mp == 0:
                k = kk
            else:
                continue
        except Exception:
            continue
        n = dict(b)
        for j, (v_, _, _) in enumerate(chosen):
            for c, coef in v_.items():
                n[c] = n.get(c, 0) + k[j] * coef
        if not all(x >= 0 for x in n.values()):
            continue
        S2 = sum(c * x for c, x in n.items())
        pr = 1
        for c, x in n.items():
            pr = pr * pow(c, x, M) % M
        if S2 != S or pr != S or not isPrime(S):
            continue
        pw = "".join(chr(c) * n[c] for c in sorted(n))
        if not (any(ch.isdigit() for ch in pw) and any(ch.isupper() for ch in pw) and any(ch.islower() for ch in pw)):
            continue
        return pw, S, k, len(pw)
    return None

if __name__ == "__main__":
    POOLS = [
        [49, 53, 65, 69, 73, 77, 81, 85, 89, 97, 101, 105, 109, 113],
        [49, 53, 65, 69, 73, 77, 81, 85, 89, 97, 101, 105, 109, 113, 117, 121],
    ]
    best = None
    for pool in POOLS:
        nsw = len([x for x in swaps_for(pool) if v2(x[2]) == 2])
        print("pool", len(pool), "min-v2 swaps:", nsw)
        for J in (24, 20, 16, 12):
            if J > nsw:
                continue
            for INV in (30, 40, 50, 60, 80):
                r = try_solve(pool, INV, J, seed=INV * 100 + J)
                if r:
                    pw, S, k, L = r
                    print(f"OK pool={len(pool)} INV={INV} J={J} len={L} S={S} maxk={max(abs(x) for x in k)}")
                    if best is None or L < best[2]:
                        best = (pw, S, L)
                    break
            if best:
                break
        if best:
            break
    if best:
        pw, S, L = best
        # final independent verification (numpy-int64 emulation)
        s64 = sum(ord(c) for c in pw)
        p64 = 1
        for c in pw:
            p64 = p64 * ord(c) & (M - 1)
        p64s = p64 - M if p64 >= (1 << 63) else p64
        assert s64 == p64s and isPrime(s64) and len(pw) < 1010
        open("password.txt", "w").write(pw)
        print("FINAL len", L, "S", S, "verified")
    else:
        print("FAILED")
