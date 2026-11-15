# Shared F_{p^2} / elliptic-curve / 2-isogeny-chain / dual-attack library.
# F_{p^2} = F_p[i]/(i^2+1). Points: (x, y) with x,y = (re, im) tuples, None = O.
import gmpy2

class F:
    def __init__(self, p):
        self.p = p
    def add(self, z, w):  return ((z[0]+w[0]) % self.p, (z[1]+w[1]) % self.p)
    def sub(self, z, w):  return ((z[0]-w[0]) % self.p, (z[1]-w[1]) % self.p)
    def neg(self, z):     return ((-z[0]) % self.p, (-z[1]) % self.p)
    def mul(self, z, w):
        return ((z[0]*w[0] - z[1]*w[1]) % self.p, (z[0]*w[1] + z[1]*w[0]) % self.p)
    def sq(self, z):      return self.mul(z, z)
    def mulc(self, z, c): return ((z[0]*c) % self.p, (z[1]*c) % self.p)
    def inv(self, z):
        n = (z[0]*z[0] + z[1]*z[1]) % self.p
        ni = int(gmpy2.invert(n, self.p))
        return ((z[0]*ni) % self.p, ((-z[1])*ni) % self.p)
    def div(self, z, w):  return self.mul(z, self.inv(w))
    def zero(self):       return (0, 0)
    def one(self):        return (1, 0)
    def eq(self, z, w):   return z[0] == w[0] and z[1] == w[1]
    def pow(self, z, e):
        r, b = self.one(), z
        e = int(e)
        while e:
            if e & 1: r = self.mul(r, b)
            b = self.sq(b); e >>= 1
        return r
    def sqrt(self, z):
        """Tonelli-Shanks in F_{p^2}; p^2-1 = 2^S * Q."""
        if self.eq(z, self.zero()): return self.zero()
        if self.eq(self.pow(z, (self.p*self.p-1)//2), self.neg(self.one())):
            raise ValueError("non-residue")
        Q = self.p*self.p - 1
        S = 0
        while Q % 2 == 0: Q //= 2; S += 1
        x, y = 0, 1
        while True:
            z_ = (x, y)
            x += 1
            if x >= self.p: x, y = 0, y + 1
            if self.eq(self.pow(z_, (self.p*self.p-1)//2), self.neg(self.one())): break
        M, c = S, self.pow(z_, Q)
        t = self.pow(z, Q)
        R = self.pow(z, (Q+1)//2)
        while not self.eq(t, self.one()):
            i, tt = 0, t
            while not self.eq(tt, self.one()):
                tt = self.sq(tt); i += 1
                if i >= M: raise ValueError("no sqrt")
            b = c
            for _ in range(M - i - 1): b = self.sq(b)
            M, c, t, R = i, self.sq(b), self.mul(t, self.sq(b)), self.mul(R, b)
        return R

    def fcbrt(self, b):
        """Cube root in F_{p^2} for b with b^((q-1)/3)=1 (AMM lifting)."""
        q = self.p * self.p
        s, m = 0, q - 1
        while m % 3 == 0: m //= 3; s += 1
        assert self.eq(self.pow(b, (q - 1) // 3), self.one())
        if self.eq(b, self.zero()): return self.zero()
        # element whose m-power has full 3^s order (needs norm non-cube in F_p)
        x, y = 1, 1
        while True:
            t = (x, y)
            x += 1
            if x >= self.p: x, y = 0, y + 1
            zeta = self.pow(t, m)
            if not self.eq(self.pow(zeta, 3**(s - 1)), self.one()): break
        omega = self.pow(zeta, 3**(s - 1)) # primitive cube root
        mu3 = [self.one(), omega, self.mul(omega, omega)]
        # m-part: 3d = 1 + k*m
        d = pow(3, -1, m)
        # split b = b1 * b2, b1 in m'-part... use Bezout: 1 = A*m + B*3^s
        # b1 = b^(B*3^s) has order | m ; b2 = b^(A*m) has order | 3^s
        A = pow(m, -1, 3**s)
        B = (1 - A * m) // 3**s
        b1 = self.pow(b, (B * 3**s) % (q - 1))
        b2 = self.pow(b, (A * m) % (q - 1))
        c1 = self.pow(b1, d)
        assert self.eq(self.pow(c1, 3), b1)
        # 3-part lifting
        x = b2
        y = self.one()
        for k in range(s - 1):
            r = self.mul(x, self.pow(self.inv(y), 3))
            z = self.pow(r, 3**(s - 2 - k))     # in {1, w, w^2}
            j = next(i for i in range(3) if self.eq(z, mu3[i]))
            if j:
                y = self.mul(y, self.pow(zeta, (3**k) * j))
        assert self.eq(self.pow(y, 3), b2)
        c = self.mul(c1, y)
        assert self.eq(self.pow(c, 3), b)
        return c

class EC:
    """y^2 = x^3 + a x + b over F (an F instance), a,b in F_{p^2}."""
    def __init__(self, F, a, b):
        self.F, self.a, self.b = F, a, b
    def on(self, pt):
        if pt is None: return True
        x, y = pt
        return self.F.eq(self.F.sq(y), self.F.add(self.F.mul(x, self.F.mul(x, x)),
                                                  self.F.add(self.F.mul(x, self.a), self.b)))
    def double(self, pt):
        if pt is None: return None
        F = self.F; x, y = pt
        if F.eq(y, F.zero()): return None
        l = F.div(F.add(F.mulc(F.sq(x), 3), self.a), F.mulc(y, 2))
        x2 = F.sub(F.sq(l), F.mulc(x, 2))
        return (x2, F.sub(F.mul(l, F.sub(x, x2)), y))
    def add(self, p1, p2):
        if p1 is None: return p2
        if p2 is None: return p1
        F = self.F; x1, y1 = p1; x2, y2 = p2
        if F.eq(x1, x2):
            if F.eq(y1, y2): return self.double(p1)
            return None
        l = F.div(F.sub(y2, y1), F.sub(x2, x1))
        x3 = F.sub(F.sub(F.sq(l), x1), x2)
        return (x3, F.sub(F.mul(l, F.sub(x1, x3)), y1))
    def mul(self, pt, k):
        r, b = None, pt
        k = int(k)
        while k:
            if k & 1: r = self.add(r, b)
            b = self.double(b); k >>= 1
        return r
    def neg(self, pt):
        if pt is None: return None
        return (pt[0], self.F.neg(pt[1]))

def velu2(Ec, e):
    """2-isogeny of Ec with kernel {(e,0)}. Returns (map(pt), a2, b2)."""
    F = Ec.F
    t = F.add(F.mulc(F.sq(e), 3), Ec.a)
    a2 = F.sub(Ec.a, F.mulc(t, 5))
    b2 = F.sub(Ec.b, F.mulc(F.mul(e, t), 7))
    def m(pt):
        if pt is None: return None
        x, y = pt
        if F.eq(x, e): return None   # point lies in the kernel
        ui = F.inv(F.sub(x, e))
        u = F.mul(t, ui)
        return (F.add(x, u), F.mul(y, F.sub(F.one(), F.mul(t, F.sq(ui)))))
    return m, a2, b2

def build_chain(Ec, T, e_order_pow, S=None):
    """Chain of 2-isogenies with kernel <T>, T of order 2^e_order_pow.
    Returns (steps, E_final, T_final). steps: (e, t, a_old, b_old, d, s, w, w3).
    S: optional generic point on Ec used to pin the dual-step isomorphism
    via the identity hat^ o hat = [2] (needed when a_old = 0)."""
    F = Ec.F
    a, b = Ec.a, Ec.b
    steps = []
    for k in range(1, e_order_pow + 1):
        cur = EC(F, a, b)
        U = cur.mul(T, 2**(e_order_pow - k))
        assert U is not None and F.eq(U[1], F.zero()), "kernel point not order 2"
        e = U[0]
        m, a2, b2 = velu2(cur, e)
        t = F.add(F.mulc(F.sq(e), 3), a)
        # dual kernel = image of another 2-torsion point of the old curve
        disc = F.neg(F.add(F.mulc(F.sq(e), 3), F.mulc(a, 4)))
        sq = F.sqrt(disc)
        e_other = F.mul(F.add(F.neg(e), sq), F.inv(F.mulc(F.one(), 2)))
        d = F.add(e_other, F.div(t, F.sub(e_other, e)))
        s = F.add(F.mulc(F.sq(d), 3), a2)
        ad, bd = F.sub(a2, F.mulc(s, 5)), F.sub(b2, F.mulc(F.mul(d, s), 7))
        # candidate isomorphisms E''(ad,bd) -> E_old(a,b)
        cands = []
        if not F.eq(a, F.zero()):
            w0 = F.div(F.mul(b, ad), F.mul(bd, a))
            r = F.sqrt(w0)
            for w3 in (F.mul(w0, r), F.neg(F.mul(w0, r))):
                cands.append((w0, w3))
        else:
            q = F.p * F.p
            w0 = F.fcbrt(F.div(b, bd))
            omega = F.pow((1, 1), (q - 1) // 3)
            if F.eq(omega, F.one()): omega = F.pow((2, 1), (q - 1) // 3)
            for i in range(3):
                w = F.mul(w0, F.pow(omega, i))
                r = F.sqrt(w)
                for w3 in (F.mul(w, r), F.neg(F.mul(w, r))):
                    cands.append((w, w3))
        def dual_cand(pt, w, w3):
            if pt is None: return None
            x, y = pt
            if F.eq(x, d): return None
            ui = F.inv(F.sub(x, d))
            x2 = F.add(x, F.mul(s, ui))
            y2 = F.mul(y, F.sub(F.one(), F.mul(s, F.sq(ui))))
            return (F.mul(w, x2), F.mul(w3, y2))
        if S is not None:
            ref = cur.mul(S, 2)
            good = None
            for (w, w3) in cands:
                got = dual_cand(m(S), w, w3)
                if (got is None and ref is None) or \
                   (got is not None and ref is not None and F.eq(got[0], ref[0]) and F.eq(got[1], ref[1])):
                    good = (w, w3); break
            assert good, "no dual candidate satisfies [2]"
            w, w3 = good
        else:
            w, w3 = cands[0]
        steps.append((e, t, a, b, d, s, w, w3))
        T = m(T)
        if S is not None: S = m(S)
        a, b = a2, b2
    return steps, EC(F, a, b), T

def dual_map(F, steps, pt):
    for (e, t, a_old, b_old, d, s, w, w3) in reversed(steps):
        if pt is None: return None
        x, y = pt
        if F.eq(x, d): return None
        ui = F.inv(F.sub(x, d))
        x = F.add(x, F.mul(s, ui))
        y = F.mul(y, F.sub(F.one(), F.mul(s, F.sq(ui))))
        pt = (F.mul(w, x), F.mul(w3, y))
    return pt

def recover_n(F, EA, Pa, Qa, Qp, e_pow):
    """Given E_A (EC), Pa, Qa on E: y^2=x^3+1, and Qp = phi(Qa), recover n
    with ker(phi) = <Pa + n Qa> (n mod 2^e_pow)."""
    # generic point on EA to pin dual isomorphisms
    S = None
    x = 1
    while S is None:
        xx = (x % F.p, 7)
        rhs = F.add(F.mul(xx, F.mul(xx, xx)), F.add(F.mul(xx, EA.a), EA.b))
        try:
            yy = F.sqrt(rhs)
        except ValueError:
            x += 1; continue
        if F.eq(F.sq(yy), rhs): S = (xx, yy)
        x += 1
    steps, Efin, _ = build_chain(EA, Qp, e_pow, S=S)
    assert F.eq(Efin.a, F.zero()), "final curve not j=0"
    b216 = Efin.b
    # isomorphisms iota: E -> Efin, (x,y)->(u2 x, u3 y), u2^3=b216, u3^2=b216
    c = F.fcbrt(b216)
    s_ = F.sqrt(b216)
    q = F.p * F.p
    # primitive cube root of unity
    base = (2, 1)
    omega = F.pow(base, (q - 1) // 3)
    while F.eq(omega, F.one()):
        base = (base[0] + 1, base[1])
        omega = F.pow(base, (q - 1) // 3)
    mu3 = [c, F.mul(c, omega), F.mul(c, F.sq(omega))]
    good = None
    for u2 in mu3:
        for u3 in [s_, F.neg(s_)]:
            S = (F.mul(u2, Qa[0]), F.mul(u3, Qa[1]))
            img = dual_map(F, steps, S)
            if img is not None and F.eq(img[0], Qp[0]) and F.eq(img[1], Qp[1]):
                good = (u2, u3); break
        if good: break
    assert good, "no isomorphism candidate matched Q'"
    u2, u3 = good
    H = dual_map(F, steps, (F.mul(u2, Pa[0]), F.mul(u3, Pa[1])))
    assert H is not None and EA.on(H)
    # 2-adic DLP: H = k Qp
    k, W, Qi = 0, H, Qp
    for i in range(e_pow):
        c = EA.mul(W, 2**(e_pow-1-i))
        if c is not None:
            k |= (1 << i)
            W = EA.add(W, EA.neg(Qi))
        Qi = EA.double(Qi)
    return (-k) % (2**e_pow)
