import random, itertools, time
import sympy as sp

a = 0x1337deadbeef
b = 0xb
M = 2 ** 48
L = 40

def f(x): return (a * x + b) % M
def top(x): return x >> (48 - 8)

def recover_e0(h, a, b, m=8):
    """h[i]=top(x_i) for i=0..m-1, x_{i+1}=a x_i+b (mod M). Return x_0.
    Only e0 (low L bits of x0) is free: x_i = (K_i + a^i e0) mod M, K_i=(a^i h0 2^L + c_i) mod M.
    CVP: find p in Lambda (gen by (1,a,...,a^{m-1}) and M e_j) closest to target t_i=(h_i 2^L+2^{L-1}-K_i) mod M."""
    h0 = h[0]
    S = [0] * m
    for i in range(m):
        S[i] = (pow(a, i) - 1) // (a - 1)
    c = [(b * S[i]) % M for i in range(m)]
    K = [(pow(a, i, M) * (h0 * (2 ** L)) + c[i]) % M for i in range(m)]
    t = sp.Matrix([ (h[i] * (2 ** L) + 2 ** (L - 1) - K[i]) % M for i in range(m) ])
    # Lambda generators: col0 = (1, a, ..., a^{m-1})^T ; cols 1..m = M e_j
    G = sp.zeros(m, m + 1)
    for i in range(m):
        G[i, 0] = pow(a, i, M)
        G[i, i + 1] = M
    # LLL: need to reduce COLUMNS. sympy lll reduces rows -> reduce G.T if allowed (m+1 x m, rows>cols -> fails).
    # Instead: use the  x m+1 matrix and call lll on it (m rows <= m+1 cols). Test what it reduces.
    # We'll determine convention empirically and reduce the right orientation.
    Gred_cols = None
    # Try: lll on G (m x (m+1)) -> if sympy reduces rows, result is row-basis (wrong).
    # To get a reduced COLUMN basis, we want a basis of the same lattice as columns of G.
    # Trick: the column lattice of G == row lattice of G.T. G.T is (m+1) x m -> lll needs rows<=cols, fails.
    # So instead build an equivalent square-ish: use the 8x8 B lattice (full rank in R^8) which we know works.
    raise SystemExit("use B8 formulation")

# ---- Use the 8x8 B lattice (proven to work for backward path) ----
def recover_x0_B8(h, a, b, m=8):
    M = 2 ** 48
    # x_i = a^i x0 + b S_i (mod M); c_i = b S_i mod M
    c = [0] * m
    for i in range(m):
        S_i = (pow(a, i) - 1) // (a - 1)
        c[i] = (b * S_i) % M
    B = sp.zeros(m, m)
    for i in range(m):
        B[i, 0] = pow(a, i, M)
        for j in range(1, i + 1):
            B[i, j] = (pow(a, i - j, M) * M)
    t = sp.Matrix([h[i] * (2 ** L) - c[i] for i in range(m)])
    Bred = (B.T.lll()).T
    # Babai exact
    BRT = Bred.T
    G = (BRT * Bred).inv() * (BRT * t)
    u0 = [int((sp.Rational(G[i]) + sp.Rational(1, 2)).__floor__()) for i in range(m)]
    best = None
    for R in (2, 4, 8):
        for dc in itertools.product(range(-R, R + 1), repeat=m):
            u = sp.Matrix([u0[i] + dc[i] for i in range(m)])
            r = (Bred * u - t) % M
            if all(0 <= int(r[i]) < 2 ** L for i in range(m)):
                val = sum(int((r[i] - 2 ** (L - 1)) ** 2) for i in range(m))
                if best is None or val < best[0]:
                    best = (val, int((Bred * u)[0]))
        if best is not None:
            break
    if best is None:
        return None
    x0 = best[1] % M
    x = x0
    for i in range(m):
        if top(x) != h[i]:
            return None
        x = f(x)
    return x0

if __name__ == "__main__":
    ok = 0
    t0 = time.time()
    for trial in range(30):
        S = random.getrandbits(48)
        x = S
        h = []
        for i in range(8):
            x = f(x)
            h.append(top(x))
        true_x0 = (pow(a, 0, M) * S + 0) % M  # x after 0 steps? no: h[0]=top(f(S)) so x0=f(S)
        true_x0 = f(S)
        rec = recover_x0_B8(h, a, b)
        if rec != true_x0:
            print(f"FAIL {trial}: rec={rec} true={true_x0} h={h}")
            break
        ok += 1
    print(f"recovered {ok}/30 in {time.time()-t0:.1f}s")
