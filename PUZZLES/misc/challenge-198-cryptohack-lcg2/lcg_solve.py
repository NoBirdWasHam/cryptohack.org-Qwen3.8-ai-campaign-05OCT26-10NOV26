import random, time, itertools
import sympy as sp

a = 0x1337deadbeef
b = 0xb
M = 2 ** 48
L = 40
m = 8
HALF = 2 ** (L - 1)

def f(x): return (a * x + b) % M
def top(x): return x >> (48 - 8)

def build():
    c = [0] * m
    for i in range(m):
        S_i = (pow(a, i) - 1) // (a - 1)
        c[i] = (b * S_i) % M
    # lattice B (m x m): col0 = v=(a^0..a^{m-1}); col_i (i>=1) = M e_i
    B = sp.zeros(m, m)
    for i in range(m):
        B[i, 0] = pow(a, i, M)
        if i >= 1:
            B[i, i] = M
    return B, c

def recover_x0(h, a, b, B, c, W=256):
    """h[i]=top(x_i) for i=0..m-1. Return x_0."""
    H0 = h[0]
    K = [ (pow(a, i, M) * (H0 * (2**L)) + c[i]) % M for i in range(m) ]
    T = sp.Matrix([ (h[i] + sp.Rational(1,2)) * (2**L) - K[i] for i in range(m) ])
    # exact Babai
    BRT = B.T
    G = (BRT * B).inv() * (BRT * T)
    z0 = [ int((sp.Rational(G[i]) + sp.Rational(1, 2)).__floor__()) for i in range(m) ]
    e0_guess = z0[0]
    for Wd in (W, 4*W, 64*W):
        for e0 in range(e0_guess - Wd, e0_guess + Wd + 1):
            e0m = e0 % (2**L)
            x0 = (H0 * (2**L) + e0m) % M
            x = x0
            ok = True
            for i in range(m):
                if top(x) != h[i]:
                    ok = False; break
                x = f(x)
            if ok:
                return x0
    return None

if __name__ == "__main__":
    B, c = build()
    ok = 0
    t0 = time.time()
    for trial in range(40):
        S = random.getrandbits(48)
        x = S
        h = []
        for i in range(8):
            x = f(x)
            h.append(top(x))
        true_x0 = f(S)  # first state whose top is h[0]
        tc = time.time()
        rec = recover_x0(list(h), a, b, B, c)
        dt = time.time() - tc
        if rec != true_x0:
            print(f"FAIL {trial}: rec={rec} true={true_x0}  ({dt:.2f}s)"); break
        ok += 1
    print(f"recovered {ok}/40 in {time.time()-t0:.1f}s")
