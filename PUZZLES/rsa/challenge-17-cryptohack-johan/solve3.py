# johan: Franklin-Reiter with SHIFTED differences: m_j = m_i + d*2^s.
import re
from Crypto.Util.number import long_to_bytes
import gmpy2

txt = open("output.txt").read()
blocks = re.findall(r"n = (\d+)\ne = (\d+)\nc = (\d+)", txt)
ns = [int(b[0]) for b in blocks]; cs = [int(b[2]) for b in blocks]

def poly_mod(f, g, n):
    f = f[:]
    dg = len(g) - 1
    lc = g[dg] % n
    try:
        inv = pow(lc, -1, n)
    except ValueError:
        return None
    while len(f) >= len(g) and f:
        shift = len(f) - len(g)
        coef = (f[-1] * inv) % n
        for i in range(len(g)):
            f[shift + i] = (f[shift + i] - coef * g[i]) % n
        while f and f[-1] == 0:
            f.pop()
    return f

def poly_gcd(f, g, n):
    while g:
        r = poly_mod(f, g, n)
        if r is None: return None
        f, g = g, r
    return f

found = False
for i in range(7):
    for j in range(i + 1, 7):
        n = ns[i]; c1 = cs[i]; c2 = cs[j]
        f = [-c1 % n, 0, 0, 1]
        for s in range(0, 600):
            p2 = 1 << s
            for d in list(range(1, 60)) + list(range(-60, 0)):
                dd = d * p2
                g = [pow(dd, 3, n) - c2 % n, 3 * dd * dd % n, 3 * dd % n, 1]
                r = poly_gcd(g[:], f[:], n)
                if r is not None and len(r) == 2:
                    try:
                        m1 = (-r[0] * pow(r[1], -1, n)) % n
                    except ValueError:
                        continue
                    if pow(m1, 3, n) == c1:
                        print(f"PAIR {i},{j} d={d} s={s}")
                        print("m_i:", long_to_bytes(m1))
                        print("m_j:", long_to_bytes((m1 + dd) % n))
                        found = True
                        break
            if found: break
        if found: break
    if found: break
print("DONE", found)
