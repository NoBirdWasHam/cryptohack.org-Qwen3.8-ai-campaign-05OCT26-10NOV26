# Miller/Sabt: factor n given ANY multiple of phi(n) (size irrelevant).
import random
import gmpy2

def factor_from_multiple(n, M, tries=60):
    M = abs(int(M))
    m = M; s = 0
    while m % 2 == 0:
        m //= 2; s += 1
    assert s >= 1, "multiple is odd - impossible for phi"
    rnd = random.Random(0xC0FFEE)
    for _ in range(tries):
        g = rnd.randrange(2, n - 1)
        gg = int(gmpy2.gcd(g, n))
        if gg != 1 and 1 < gg < n:
            return gg, n // gg
        x = pow(g, m, n)
        if x == 1:
            continue
        for _ in range(s):
            y = x
            x = (x * x) % n
            if x == 1:
                if y != 1 and y != n - 1:
                    f = int(gmpy2.gcd(y - 1, n))
                    if 1 < f < n:
                        return f, n // f
                break
    raise RuntimeError("factorization failed")
