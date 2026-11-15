# 297 sus (ImaginaryCTF 2023): intended solve per author README
# (github.com/maple3142/My-CTF-Challenges ImaginaryCTF 2023/Sus).
# Bach-Shallit / high-degree p-1 style: in (Z/n)[x]/f(x) with random monic cubic f,
# t = a^n -> when f irreducible mod p, t lands in base field mod p -> gcd(coef, n) = p.
# Source: author README cited 2026-11-08; flag derived locally from output.txt.
import random
from math import gcd

ns = {}
exec(open("output.txt").read(), ns)
n, e, c = ns["n"], ns["e"], ns["c"]
print("n bits", n.bit_length(), "e", e)

def pmul(A, B, mod):
    # cubic-truncated: x^3 = -a x^2 - b x - c supplied via RED list
    C = [0]*5
    for i in range(3):
        if A[i] == 0: continue
        for j in range(3):
            if B[j] == 0: continue
            C[i+j] = (C[i+j] + A[i]*B[j]) % mod
    # reduce x^4 then x^3 (x^3 = RED[2]x^2 + RED[1]x + RED[0])
    for k in (4, 3):
        v = C[k]
        if v:
            C[k-1] = (C[k-1] + v*RED[2]) % mod
            C[k-2] = (C[k-2] + v*RED[1]) % mod
            C[k-3] = (C[k-3] + v*RED[0]) % mod
            C[k] = 0
    return C[:3]

def ppow(base, exp, mod):
    r = [1, 0, 0]
    b = base[:]
    while exp:
        if exp & 1: r = pmul(r, b, mod)
        b = pmul(b, b, mod)
        exp >>= 1
    return r

rnd = random.Random(1337)
p = None
for tries in range(200):
    # random monic cubic x^3 + a x^2 + b x + c  -> RED = [-c, -b, -a] mod n
    a, b, cc = rnd.randrange(n), rnd.randrange(n), rnd.randrange(n)
    global RED
    RED = [(-cc) % n, (-b) % n, (-a) % n]
    for _ in range(30):
        t = ppow([rnd.randrange(n) for _ in range(3)], n, n)
        for coef in t[1:]:
            g = gcd(coef, n)
            if 1 < g < n:
                p = g
                break
        if p: break
    if p:
        print("factored on try", tries, "p bits", p.bit_length())
        break

if p is None:
    raise SystemExit("no factor found")
q = p*p + p + 1
r = n // p // q
assert p * q * r == n, "structure mismatch"
from sympy import isprime
print("q prime?", isprime(q), "r prime?", isprime(r))
phi = (p-1) * (q-1) * (r-1)
d = pow(e, -1, phi)
m = pow(c, d, n)
flag = m.to_bytes((m.bit_length()+7)//8, "big")
print("FLAG:", flag)
