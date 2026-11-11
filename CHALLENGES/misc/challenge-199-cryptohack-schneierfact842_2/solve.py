# schneierfact842_2 solver: multiset of odd codes (all ≡1 mod 4) with
# prod ≡ sum (mod 2^64), sum prime. Sum-preserving swaps + lattice (embedding/BKZ).
import sys, json, math
sys.path.insert(0, ".")
from mathlib import M, POOL, log5, find_swaps, v2
from Crypto.Util.number import isPrime
from gmpy2 import next_prime

INV = 600  # base inventory per pool char

def build_base():
    b = {c: INV for c in POOL}
    S0 = sum(c * n for c, n in b.items())
    p0 = 1
    for c, n in b.items():
        p0 = p0 * pow(c, n, M) % M
    # add Delta copies of '1' (49): S = S0+49D, p = p0*49^D ≡ p0 mod 16 (49≡1 mod16)
    # need S ≡ p0 mod 16 -> D ≡ p0 - S0 (mod 16)
    D0 = (p0 - S0) % 16
    D = D0
    while True:
        S = S0 + 49 * D
        if isPrime(S):
            break
        D += 16
    b[49] += D
    S = S0 + 49 * D
    p = p0 * pow(49, D, M) % M
    assert S % 16 == p % 16 and S % 4 == 1
    return b, S, p

def main():
    b, S, p_base = build_base()
    T = log5(S * pow(p_base, -1, M) % M)
    assert T % 4 == 0
    d = 2
    Mp = 1 << (62 - d)
    Tp = T >> d
    sw = find_swaps()
    sw = [(v, log5(r)) for v, r in sw if v2(log5(r)) == d]
    import random
    random.seed(1234)
    J = 10
    from fpylll import IntegerMatrix, BKZ, LLL, CVP
    for attempt in range(40):
        chosen = random.sample(sw, J)
        lam = [l >> d for _, l in chosen]
        g = math.gcd(math.gcd(*lam), Mp)
        if Tp % g != 0:
            continue
        # lattice rows: (Mp,0..0), (lam_j, e_j); CVP target (Tp,0..0)
        dim = J + 1
        A = IntegerMatrix(dim, dim)
        A[0, 0] = Mp
        for j in range(J):
            A[1 + j, 0] = lam[j]
            A[1 + j, 1 + j] = 1
        BKZ.reduction(A, BKZ.EasyParam(40))
        k = None
        try:
            from fpylll.fplll.utils import FPLLL
            target = [Tp] + [0] * J
            v = CVP.closest_vector(A, target)
            kk = [int(v[1 + j]) for j in range(J)]
            if (int(v[0]) - Tp) % Mp == 0 and (sum(lam[j] * kk[j] for j in range(J)) - Tp) % Mp == 0:
                k = kk
        except Exception as e:
            pass
        if k is None:
            # fallback: embedding trick
            W = 64
            B = IntegerMatrix(dim + 1, dim + 1)
            B[0, 0] = Mp
            for j in range(J):
                B[1 + j, 0] = lam[j]
                B[1 + j, 1 + j] = 1
            B[dim, 0] = Tp
            B[dim, dim] = W
            BKZ.reduction(B, BKZ.EasyParam(40))
            for i in range(dim + 1):
                if abs(B[i, dim]) == W:
                    sgn = 1 if B[i, dim] > 0 else -1
                    kk = [int(-sgn * B[i, 1 + j]) for j in range(J)]
                    if (Tp - sum(lam[j] * kk[j] for j in range(J))) % Mp == 0:
                        k = kk
                        break
        if k is None:
            continue
        n = dict(b)
        for j, (v, _) in enumerate(chosen):
            for c, coef in v.items():
                n[c] = n.get(c, 0) + k[j] * coef
        if not all(x >= 0 for x in n.values()):
            print("attempt", attempt, "negative counts, retrying; k=", k)
            continue
        break
    assert k is not None, "no short vector found"
    print("k =", k, "max|k| =", max(abs(x) for x in k))
    # apply swaps
    n = dict(b)
    for j, (v, _) in enumerate(chosen):
        for c, coef in v.items():
            n[c] = n.get(c, 0) + k[j] * coef
    assert all(x >= 0 for x in n.values()), n
    S2 = sum(c * x for c, x in n.items())
    pr = 1
    for c, x in n.items():
        pr = pr * pow(c, x, M) % M
    assert S2 == S, (S2, S)
    assert pr == S, (pr, S)
    assert isPrime(S)
    pw = "".join(chr(c) * n[c] for c in sorted(n))
    assert pw.isalnum() and any(ch.isdigit() for ch in pw) and any(ch.isupper() for ch in pw) and any(ch.islower() for ch in pw)
    # emulate numpy int64 prod/sum
    s64 = sum(ord(ch) for ch in pw)
    p64 = 1
    for ch in pw:
        p64 = (p64 * ord(ch)) & (M - 1)
    p64s = p64 - M if p64 >= (1 << 63) else p64
    assert s64 == p64s and isPrime(s64)
    print("password length:", len(pw), "S =", S, "prime OK, prod64 == sum OK")
    open("password.txt", "w").write(pw)

if __name__ == "__main__":
    main()
