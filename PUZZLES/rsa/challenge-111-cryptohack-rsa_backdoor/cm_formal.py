#!/usr/bin/env python3
# rsa_backdoor final attack: CM curve over R=(Z/n)[d]/(d^2-DH), DH=disc(H_-427),
# formal-y algebra S=R[Y]/(Y^2-g(x0)) -- NO square roots needed.
# p=(427s^2+1)/4 => p principal of disc -427 => H splits mod p, #E(F_p)=p+1-t.
# t=+1: [n]P=O mod p => denominator norm gcd(.,n)=p. t=-1: random twist d in R.
import random
from math import gcd
import gmpy2

HB = 15611455512523783919812608000
HC = 155041756222618916546936832000000

class BadDen(Exception):
    def __init__(self, val): self.val = val   # integer whose gcd with n may split n

def factor(n, seed=1, trials=40, verbose=False):
    rng = random.Random(seed)
    DD = (HB*HB - 4*HC) % n
    inv2 = (n + 1) // 2
    # ---- R = (Z/n)[d]/(d^2 - DD) ----
    def rmul(u, v):
        a, b = u; c, d = v
        return ((a*c + b*d*DD) % n, (a*d + b*c) % n)
    def radd(u, v): return ((u[0]+v[0]) % n, (u[1]+v[1]) % n)
    def rsub(u, v): return ((u[0]-v[0]) % n, (u[1]-v[1]) % n)
    def rsq(u): return rmul(u, u)
    def rnorm(u):
        a, b = u
        return (a*a - b*b*DD) % n
    def rinv(u):
        N = rnorm(u)
        try: g = pow(N, -1, n)
        except ValueError: raise BadDen(N)
        return (u[0]*g % n, (-u[1]) * g % n)
    # ---- S = R[Y]/(Y^2 - c0), c0 in R ----
    def smul(s1, s2, c0):
        a, b = s1; c, d = s2
        ac = rmul(a, c); bd = rmul(b, d)
        return (radd(ac, rmul(bd, c0)), radd(rmul(a, d), rmul(b, c)))
    def ssq(s1, c0): return smul(s1, s1, c0)
    def snorm(s1, c0):
        a, b = s1
        return rsub(rsq(a), rmul(rsq(b), c0))
    def sinv(s1, c0):
        N = snorm(s1, c0)
        Ni = rinv(N)
        return (rmul(s1[0], Ni), rmul((-s1[1][0] % n, -s1[1][1] % n), Ni))  # (u-vY)/N
    # curve constants: A=3x/(1728-x), B=2x/(1728-x), x=(d-HB)/2
    xd = ((-HB % n) * inv2 % n, inv2)
    ti = rinv(rsub((1728, 0), xd))
    jti = rmul(xd, ti)
    A = rmul((3, 0), jti); B = rmul((2, 0), jti)

    def sadd(u, v): return (radd(u[0], v[0]), radd(u[1], v[1]))
    def ssub(u, v): return (rsub(u[0], v[0]), rsub(u[1], v[1]))
    def iszero_S(y1, y2):
        s = sadd(y1, y2)
        return s[0] == (0, 0) and s[1] == (0, 0)
    def rsmul(a, s1):  # R-elem a times S-elem s1
        return (rmul(a, s1[0]), rmul(a, s1[1]))
    def emb(a):        # R-elem -> S-elem
        return (a, (0, 0))

    def add(P, Q, At, Bt, c0):
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2:
            if iszero_S(y1, y2): raise BadDen(rnorm(y1[0]))
            num = emb(radd(rmul((3, 0), rsq(x1)), At))
            den = rsmul((2, 0), y1)
        else:
            num = ssub(y2, y1); den = emb(rsub(x2, x1))
        m = smul(num, sinv(den, c0), c0)
        m2 = ssq(m, c0)
        x3 = rsub(rsub(m2[0], x1), x2)
        y3 = ssub(smul(m, emb(rsub(x1, x3)), c0), y1)
        return (x3, y3)

    for trial in range(trials):
        d = (1, 0) if trial == 0 else (rng.randrange(n), rng.randrange(n))
        try:
            d2 = rsq(d); d3 = rmul(d2, d)
            At = rmul(d2, A); Bt = rmul(d3, B)
        except BadDen as ex:
            f = gcd(ex.val, n)
            if 1 < f < n: return f
        for _ in range(3):
            x0 = (rng.randrange(n), rng.randrange(n))
            c0 = radd(radd(rmul(rsq(x0), x0), rmul(At, x0)), Bt)  # g(x0) in R
            P = (x0, ((0, 0), (1, 0)))   # (x0, Y)
            R = None; k = n
            try:
                while k:
                    if k & 1: R = add(R, P, At, Bt, c0)
                    P = add(P, P, At, Bt, c0); k >>= 1
            except BadDen as ex:
                f = gcd(ex.val, n)
                if 1 < f < n: return f
                if verbose: print("  trial%d: bad den gcd=%s" % (trial, f))
            if R is None and verbose: print("  trial%d: O mod n" % trial)
    return None

if __name__ == "__main__":
    import sys, time, re
    from Crypto.Util.number import getPrime, isPrime
    mode = sys.argv[1] if len(sys.argv) > 1 else "self"
    if mode == "self":
        rng = random.Random(7)
        ok = 0
        for it in range(4):
            while True:
                s = rng.randrange(2**62, 2**64)
                t = 427*s*s + 1
                if t % 4 == 0 and isPrime(t//4): p = t//4; break
            q = getPrime(160); n = p*q
            t0 = time.time()
            f = factor(n, seed=100+it, verbose=True)
            good = f in (p, q)
            ok += good
            print(f"inst{it}: good={good} %.1fs" % (time.time()-t0))
        print("ok:", ok, "/4")
    else:
        txt = open("output.txt").read()
        d_ = {k: int(v) for k, v in re.findall(r"(\w+) = (\d+)", txt)}
        n, e, c = d_["n"], d_["e"], d_["c"]
        t0 = time.time()
        f = factor(n, seed=2026, verbose=True)
        if f and 1 < f < n:
            p = f; q = n // p
            print("p bits:", p.bit_length(), "q bits:", q.bit_length(),
                  "primes:", gmpy2.is_prime(p), gmpy2.is_prime(q))
            m = pow(c, pow(e, -1, (p-1)*(q-1)), n)
            flag = m.to_bytes((m.bit_length()+7)//8, "big").decode()
            print("flag:", flag)
            open("flag_rsa_backdoor.txt", "w").write(flag)
        else:
            print("NOT SOLVED, result:", f, "%.1fs" % (time.time()-t0))
