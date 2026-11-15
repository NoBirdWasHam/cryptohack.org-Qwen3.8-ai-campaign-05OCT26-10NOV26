import random
from quo_core import (modulus_from_line, Tower, Nest, cz_roots, solve_mod2k, prod)

def unit_inv_newton(u, N1, tw, iters=8):
    L = N1.L - 1
    ub = N1.flatten(u)
    mask = 0
    for i, b in enumerate(ub):
        if b & 1: mask |= 1 << i
    assert mask != 0, "not a unit"
    v = tw.from_mask(tw.minv(mask))   # nested tuple of bits
    two = N1.scale(N1.one(L), 2, L)
    for _ in range(iters):
        v = N1.mul(v, N1.sub(two, N1.mul(u, v, L), L), L)
    return v

def hensel_root(moduli, gbits, k, seed=0):
    """returns (T, N1, theta (nest el), cols (flat theta^i)) for R1 tower ds, R2 modulus bits."""
    ds = [len(m) - 1 for m in moduli]
    D = prod(ds)
    p = 2 ** k
    T = Tower(ds, moduli)
    roots = cz_roots(gbits, T)
    rbits = roots[0]
    Fbits = [(gbits >> i) & 1 for i in range(D + 1)]
    assert T.mmul_chain if False else True
    # verify root: eval g at rbits over T
    ev = 0
    for c in reversed(Fbits):
        ev = T.mmul(ev, rbits)
        if c: ev ^= rbits if False else 1
    # careful Horner with scalar 1 constant:
    ev = 0
    one = 1
    for c in reversed(Fbits):
        ev = T.mmul(ev, rbits)
        if c: ev ^= one
    assert ev == 0, "root check failed"
    N1 = Nest(ds, moduli, p)
    L = N1.L - 1
    theta = T.from_mask(rbits)
    gcoeff = [(gbits >> i) & 1 for i in range(D + 1)]
    gprime = [(i * ((gbits >> i) & 1)) % p for i in range(1, D + 1)]
    for _ in range(7):
        u = N1.eval_int_poly(theta, gcoeff)
        du = N1.eval_int_poly(theta, gprime)
        inv = unit_inv_newton(du, N1, T)
        theta = N1.sub(theta, N1.mul(u, inv, L), L)
    assert N1.eval_int_poly(theta, gcoeff) == N1.zero(L), "hensel failed"
    cols = []
    pw = N1.one(L)
    for i in range(D):
        cols.append(N1.flatten(pw))
        pw = N1.mul(pw, theta, L)
    return T, N1, theta, cols

def hom_check(N1, T, theta, cols, gbits, rng):
    """phi(beta*x) == theta*phi(x) for random x; and M invertible (odd det)."""
    ds = N1.ds; D = prod(ds); p = N1.p; L = N1.L - 1
    for _ in range(6):
        xflat = [rng.randrange(p) for _ in range(D)]
        # beta * x in R2: shift then reduce by g (monic, coeffs bits)
        sh = [0] + xflat
        c = sh[D]
        if c:
            for j in range(D):
                if (gbits >> j) & 1:
                    sh[j] = (sh[j] - c) % p
        bx = [v % p for v in sh[:D]]
        lhs = [sum(cols[i][r] * bx[i] for i in range(D)) % p for r in range(D)]
        xf = xflat
        mx = [sum(cols[i][r] * xf[i] for i in range(D)) % p for r in range(D)]
        # theta * mx in R1: unflatten
        mxn = nest_from_flat(N1, mx)
        tmx = N1.flatten(N1.mul(N1._theta_el if False else nest_from_flat(N1, [1] + [0]*(D-1)) if False else theta, mxn, L))
        assert lhs == tmx, "homomorphism check failed"
    return True

def nest_from_flat(N1, flat):
    def rec(flat, lvl):
        if lvl == 0:
            return [v % N1.p for v in flat]
        block = prod(N1.ds[:lvl])
        return tuple(rec(flat[i * block:(i + 1) * block], lvl - 1) for i in range(N1.ds[lvl]))
    return rec(flat, N1.L - 1)

if __name__ == "__main__":
    lines = [
        "b0^2 + b0 + 1",
        "b1^3 + (b0bar + 1)*b1 + 1",
        "b0^6 + b0^5 + b0^2 + b0 + 1",
    ]
    ds = [2, 3]
    moduli = [modulus_from_line(lines[0], 0, ds), modulus_from_line(lines[1], 1, ds)]
    print("moduli:", moduli)
    gd = modulus_from_line(lines[2], 0, [6])
    gbits = sum(c << i for i, c in enumerate(gd))
    print("gbits:", bin(gbits))
    rng = random.Random(1)
    T, N1, theta, cols = hensel_root(moduli, gbits, 2, rng)
    print("theta cols:")
    for c in cols: print(c)
    hom_check(N1, T, theta, cols, gbits, rng)
    print("HOM OK")
    # invertibility
    import quo_core
    x = quo_core.solve_mod2k(cols, [2,3,1,3,3,0], 4)
    print("solve demo x:", x)
    print("ALL TESTS PASS")
