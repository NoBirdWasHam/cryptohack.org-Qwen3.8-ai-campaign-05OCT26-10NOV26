import random, time, itertools
import numpy as np
import sympy as sp

a = 0x1337deadbeef
b = 0xb
M = 2 ** 48
L = 40
m = 8

def f(x): return (a * x + b) % M
def top(x): return x >> (48 - 8)

def make_B():
    c = [0]*m
    for i in range(m):
        S_i = (pow(a, i) - 1) // (a - 1)
        c[i] = (b * S_i) % M
    B = sp.zeros(m, m)
    for i in range(m):
        B[i, 0] = pow(a, i, M)
        for j in range(1, i+1):
            B[i, j] = (pow(a, i-j, M) * M)
    return B, c

def solve_case(h, B, c, Rmax=12):
    t = sp.Matrix([h[i]*(2**L) - c[i] for i in range(m)])
    Bred = (B.T.lll()).T
    # exact Babai
    BRT = Bred.T
    G = (BRT*Bred).inv()*(BRT*t)
    u0 = [int((sp.Rational(G[i]) + sp.Rational(1,2)).__floor__()) for i in range(m)]
    # numpy int64 eval using B mod M
    Bm = np.zeros((m, m), dtype=np.int64)
    for i in range(m):
        for j in range(m):
            Bm[i, j] = int(Bred[i, j]) % M
    tvec = np.array([int(t[i]) for i in range(m)], dtype=np.int64)
    for R in range(1, Rmax+1):
        for dc in itertools.product(range(-R, R+1), repeat=m):
            u = np.array([u0[i]+dc[i] for i in range(m)], dtype=np.int64)
            r = (Bm @ u - tvec) % M
            if (r < 2**L).all():
                x0 = int((Bm @ u)[0]) % M
                # verify by simulating
                x = x0
                ok = all(top(x)==h[i] for i in [0]) 
                y = x0
                tops=[]
                for i in range(m):
                    tops.append(top(y)); y=f(y)
                if tops == list(h):
                    return x0, R
    return None, None

if __name__ == "__main__":
    B, c = make_B()
    t0=time.time()
    Rs=[]
    for trial in range(15):
        S = random.getrandbits(48)
        x = S
        h=[]
        for i in range(8):
            x=f(x); h.append(top(x))
        true_x0 = x  # after 8 f's, x is state8; but h[0]=top(f(S))=top(state1)... 
        # recompute: x after loop = f^8(S). h[i]=top(f^{i+1}(S)). So x0 (first state with top h[0]) = f(S).
        true_first = f(S)
        tcase=time.time()
        x0, R = solve_case(list(h), B, c, Rmax=12)
        dt=time.time()-tcase
        Rs.append(R)
        print(f"trial {trial}: x0={'OK' if x0==true_first else 'WRONG(got %s want %s)'%(x0,true_first)} R={R} {dt:.1f}s")
    print(f"R values: {Rs}  total {time.time()-t0:.1f}s")
