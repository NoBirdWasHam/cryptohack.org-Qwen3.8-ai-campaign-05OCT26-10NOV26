# Local verification of refined leak: mixed-Jacobi query -> gcd(r'-r,n) == prime
import sys, random
sys.path.insert(0, ".")
import server, gmpy2
from math import gcd

random.seed(1234)
pub, priv = server.genkey(512)
n, c = pub.n, pub.c
print("p bits", priv.p.bit_length(), "c jac p,q", gmpy2.jacobi(c, priv.p), gmpy2.jacobi(c, priv.q))

tries = 0
found = None
while tries < 300:
    tries += 1
    r = random.randrange(1, n)
    s = random.choice([1, -1])
    t = random.choice([0, 1])
    try:
        m = server.decrypt(server.Enc(r, s, t), pub, priv)
        e2 = server.encrypt(m, pub)
    except Exception:
        continue
    g = gcd(abs(e2.r - r), n)
    if g in (priv.p, priv.q):
        found = g
        print(f"query {tries}: leaked prime {'p' if g==priv.p else 'q'}, errors before={tries}")
        break
    elif g != 1 and g != n:
        print("partial", g.bit_length())
if not found:
    print("NO LEAK in", tries, "queries")
