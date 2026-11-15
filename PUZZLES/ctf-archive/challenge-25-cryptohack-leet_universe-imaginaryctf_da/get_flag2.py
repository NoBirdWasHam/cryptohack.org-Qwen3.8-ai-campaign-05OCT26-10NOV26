#!/usr/bin/env python3
# factor p | R => f,h share root r mod p => server gcd(f(r),h(r)) >= p >> len(flag)
import socket, sys
from math import gcd
from sympy import symbols, Poly, GF
import flint
x = symbols('x')
R = int(open('_R.txt').read().strip())

def find_root(p):
    F = GF(p)
    pf = Poly(x**13 + 37, x, domain=F)
    ph = Poly((x + 42)**13 + 42, x, domain=F)
    g = pf.gcd(ph)
    print("common factor degree mod p:", g.degree())
    if g.degree() == 1:
        return int(-g.nth(0) / g.nth(1)) % p
    for fac, mult in g.factor_list()[1]:
        if fac.degree() == 1:
            return int(-fac.nth(0) / fac.nth(1)) % p
    raise RuntimeError("no linear common factor")

try:
    f0 = int(open('factor_found.txt').read().strip())
except FileNotFoundError:
    print("no factor_found.txt"); sys.exit(1)

for p, e in flint.fmpz(f0).factor()[0].items():
    p = int(p)
    if R % p:
        continue
    print("trying prime factor digits:", len(str(p)))
    r = find_root(p)
    assert (pow(r,13,p)+37) % p == 0 and (pow(r+42,13,p)+42) % p == 0
    glocal = gcd(r**13 + 37, (r+42)**13 + 42)
    print("local gcd digits:", len(str(glocal)))
    s = socket.create_connection(("archive.cryptohack.org", 3721), timeout=30)
    s.settimeout(30)
    pre = s.recv(4096)
    s.sendall((str(r) + "\n").encode())
    out = b""
    try:
        while True:
            d = s.recv(4096)
            if not d: break
            out += d
    except Exception:
        pass
    s.close()
    txt = out.decode(errors="replace").strip()
    print("server said:", txt)
    open('server_response.txt','w').write(txt)
    if txt.endswith("}") and "{" in txt:
        open('flag_leet_universe.txt','w').write(txt)
        print("FLAG SAVED:", txt)
        sys.exit(0)
