# Shared math for schneierfact842_2: group (1+4Z)/2^64 = <5>, order 2^62.
M = 1 << 64
MOD = M  # modulus for products
ORD = 1 << 62  # order of 5 mod 2^64

# pool: codes odd and ≡ 1 mod 4  (digit, upper, lower all present)
POOL = [49, 53, 65, 69, 73, 77, 81, 85, 89, 97, 101, 105, 109, 113, 117, 121]

def log5(x):
    """discrete log base 5 of x (x ≡ 1 mod 4) mod 2^62, via bit lifting."""
    assert x % 4 == 1
    l = 0
    for i in range(62):
        if pow(5, l + (1 << i), 1 << (i + 3)) == x % (1 << (i + 3)):
            l += 1 << i
    assert pow(5, l, M) == x % M
    return l

def v2(n):
    if n == 0:
        return 10**9
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c

def find_swaps():
    """vectors v (dict code->coef, sum-preserving: sum v[c]*c == 0, sum v[c] == 0,
    entries in {-1,0,+1}, support 4) with distinct product ratio."""
    from itertools import combinations
    bysum = {}
    for a, b in combinations(POOL, 2):
        bysum.setdefault(a + b, []).append((a, b))
    swaps = []
    for s, pairs in sorted(bysum.items()):
        for (a, b), (c, d) in combinations(pairs, 2):
            v = {a: 1, b: 1, c: -1, d: -1}
            num = a * b % M
            den = c * d % M
            rho = num * pow(den, -1, M) % M
            if rho % M == 1:
                continue
            swaps.append((v, rho))
    return swaps

if __name__ == "__main__":
    # sanity: log5 on pool codes
    for c in POOL:
        l = log5(c)
        assert pow(5, l, M) == c
    sw = find_swaps()
    print("swaps:", len(sw))
    ds = [v2(log5(rho)) for _, rho in sw]
    print("min v2(lambda):", min(ds), "count at min:", ds.count(min(ds)))
    # show a few with min v2
    d = min(ds)
    shown = 0
    for v, rho in sw:
        if v2(log5(rho)) == d and shown < 12:
            print(v, "rho%16=", rho % 16, "lam=", log5(rho))
            shown += 1
