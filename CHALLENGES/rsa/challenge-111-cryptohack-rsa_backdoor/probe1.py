import re
from math import gcd
txt = open("output.txt").read()
d = {k: int(v) for k, v in re.findall(r"(\w+) = (\d+)", txt)}
n, e, c = d["n"], d["e"], d["c"]

class QE:
    def __init__(s, a, b, n): s.a, s.b, s.n = a%n, b%n, n
    def __mul__(s, o):
        n = s.n
        return QE((s.a*o.a - 427*s.b*o.b) % n, (s.a*o.b + s.b*o.a) % n, n)
    def __pow__(s, k):
        r = QE(1,0,s.n); base = s
        while k:
            if k & 1: r = r*base
            base = base*base
            k >>= 1
        return r

for nm, base, exps in (
    ("1+w", QE(1,1,n), ("n","n+1","n-1")),
    ("107", QE(107,0,n), ("n+1",)),
    ("(1+w)/2 skip", None, ()),
):
    if base is None: continue
    for ename in exps:
        k = {"n": n, "n+1": n+1, "n-1": n-1}[ename]
        g = base ** k
        for val in (g.a - 1, g.b, g.a):
            f = gcd(val, n)
            if 1 < f < n:
                print("FACTOR", nm, ename, f.bit_length())
                break
        else:
            continue
        break
    else:
        continue
    break
else:
    print("no factor from QE powers")

def poller(n, B=100000):
    a = 2
    import sympy
    for pp in sympy.primerange(2, B):
        e = 1
        while pp**(e+1) < B: e += 1
        a = pow(a, pow(pp, e), n)
        f = gcd(a-1, n)
        if 1 < f < n: return f, pp
    return None, None
f, at = poller(n, 50000)
print("p-1 factor:", f)
