# Genus-7 Jacobian arithmetic for y^2 = f(x) over F_p, faithful port of
# sage cantor_composition_simple/cantor_reduction_simple (jm97.py, Kohel GPL).
# Polys: lists low->high coeffs. Divisor: (u,v) reduced: u monic, deg<=7, deg v<deg u.
P = None

def set_p(p):
    global P
    P = p

def trim(a):
    a = a[:]
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a

def is_zero(a): return trim(a) == [0]
def deg(a): return len(trim(a)) - 1

def pmul(a, b):
    a, b = trim(a), trim(b)
    if a == [0] or b == [0]:
        return [0]
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    r[i+j] = (r[i+j] + x*y) % P
    return trim(r)

def padd(*args):
    n = max(len(trim(a)) for a in args)
    return trim([sum((a[i] if i < len(a) else 0) for a in args) % P for i in range(n)])

def psub(a, b):
    n = max(len(trim(a)), len(trim(b)))
    return trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % P for i in range(n)])

def pneg(a):
    return trim([(-x) % P for x in trim(a)])

def pscale(a, c):
    return trim([(x*c) % P for x in trim(a)])

def pmodinv(a):  # monic
    a = trim(a)
    return pscale(a, pow(a[-1], P-2, P))

def pdivmod(a, m):
    a = trim(a)[:]; m = trim(m)
    q = [0] * max(1, len(a)-len(m)+1)
    inv = pow(m[-1], P-2, P)
    while True:
        while len(a) > 1 and a[-1] == 0:
            a.pop()
        if a == [0] or len(a) < len(m):
            break
        d = len(a) - len(m); c = a[-1]*inv % P
        q[d] = c
        for i in range(len(m)):
            a[i+d] = (a[i+d] - c*m[i]) % P
    return trim(q), trim(a)

def pdiv(a, m):  # exact quotient
    return pdivmod(a, m)[0]

def pmod(a, m):
    return pdivmod(a, m)[1]

def xgcd(a, b):
    # monic g, s, t: s*a + t*b = g
    old_r, r = trim(a), trim(b)
    old_s, s = [1], [0]
    old_t, t = [0], [1]
    while r != [0]:
        q, nr = pdivmod(old_r, r)
        old_r, r = r, nr
        old_s, s = s, psub(old_s, pmul(q, s))
        old_t, t = t, psub(old_t, pmul(q, t))
    inv = pow(old_r[-1], P-2, P)
    return pscale(old_r, inv), pscale(old_s, inv), pscale(old_t, inv)

def cantor_reduction(a, b, f, genus=7):
    # y^2 = f, deg f = 15 (odd): no infinity adjustment needed
    a = trim(a); b = trim(b)
    while True:
        k = pdiv(psub(f, pmul(b, b)), a)
        a2 = pmodinv(k)
        b2 = pmod(pneg(b), a2)
        if deg(a2) == deg(a):
            raise ValueError("ambiguous reduction deg %d" % deg(a2))
        a, b = a2, b2
        if deg(a) <= genus:
            return a, b

def cantor_composition(D1, D2, f):
    a1, b1 = trim(D1[0]), trim(D1[1])
    a2, b2 = trim(D2[0]), trim(D2[1])
    if a1 == [1]: return D2
    if a2 == [1]: return D1
    if a1 == a2 and b1 == b2:
        d, h1, h3 = xgcd(a1, pscale(b1, 2))
        a = pmul(pdiv(a1, d), pdiv(a1, d))
        b = pmod(padd(b1, pmul(h3, pdiv(psub(f, pmul(b1, b1)), d))), a)
    else:
        d0, s2, h2 = xgcd(a1, a2)
        if d0 == [1]:
            a = pmul(a1, a2)
            b = pmod(padd(b2, pmul(pmul(h2, a2), psub(b1, b2))), a)
        else:
            e0 = padd(b1, b2)
            if e0 == [0]:
                a = pdiv(pmul(a1, a2), pmul(d0, d0))
                b = pmod(padd(b2, pmul(pmul(h2, pdiv(a2, d0)), psub(b1, b2))), a)
            else:
                d, l, h3 = xgcd(d0, e0)
                a = pdiv(pmul(a1, a2), pmul(d, d))
                b = pmod(padd(padd(b2, pmul(pmul(l, h2), pmul(psub(b1, b2), pdiv(a2, d)))),
                              pmul(h3, pdiv(psub(f, pmul(b2, b2)), d))), a)
    return pmodinv(a), b

def h_add(D1, D2, f, genus=7):
    a, b = cantor_composition(D1, D2, f)
    if deg(a) <= genus:
        return a, b
    return cantor_reduction(a, b, f, genus)

def mul_scalar(D, m, f, genus=7):
    R = ([1], [0])
    A = (trim(D[0]), trim(D[1]))
    while m:
        if m & 1:
            R = h_add(R, A, f, genus)
        m >>= 1
        if m:
            A = h_add(A, A, f, genus)
    return R

def is_reduced(D, f, genus=7):
    u, v = D
    if len(u) == 1:
        return u == [1]
    if u[-1] != 1: return False
    if len(v) >= len(u): return False
    return pmod(psub(f, pmul(v, v)), u == [0]) if False else pmod(psub(f, pmul(v, v)), u) == [0]

def point_divisor(x0, y0):
    return ([(-x0) % P, 1], [y0 % P])

def pack_block(D):
    import struct
    u, v = D
    us = [u[i] if i < len(u) else 0 for i in range(7)]
    vs = [v[i] if i < len(v) else 0 for i in range(7)]
    return struct.pack('<' + 'Q'*14, *(us + vs))
