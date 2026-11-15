import ast, re, io, contextlib
from math import gcd
buf = io.StringIO()
g = {'__name__': '__main__'}
with contextlib.redirect_stdout(buf):
    exec(open('solve.py').read(), g)
cpow, Complex, n, L, ct, pt = g['cpow'], g['Complex'], g['n'], g['L'], g['ct'], g['pt']
p, q = g['p'], g['q']
rt = cpow(Complex(int.from_bytes(pt[:252],'big'), int.from_bytes(pt[252:],'big')), 65537, n)
ct2 = rt.re.to_bytes(L,'big') + rt.im.to_bytes(L,'big')
print("re-encrypt match:", ct2 == ct)
try:
    import gmpy2
    print("p,q prime:", gmpy2.is_prime(p), gmpy2.is_prime(q))
except ImportError:
    print("(gmpy2 unavailable: skipped primality)")
print("flag bytes tail:", repr(pt[-12:]))
