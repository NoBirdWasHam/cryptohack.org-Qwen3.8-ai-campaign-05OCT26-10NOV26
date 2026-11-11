#!/usr/bin/env python3
# challenge-273 FULL server-route solve, 2026-11-07: Euclid in (Z/RZ)[x] -> degree-1
# common gcd -> root x0 mod R -> server gcd(f(x0),h(x0)) = R >= len(flag) -> full flag.
# No factorization of R used. Self-derived.
import math, socket, sys

R = int(open('_R.txt').read().strip())

def trim(p):
    while len(p) > 1 and p[-1] == 0: p.pop()
    return p

def monic_div(a, b, M):  # b monic, low->high; remainder
    a = a[:]
    db = len(b) - 1
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i] % M
        if c:
            for j in range(db + 1):
                a[i - db + j] = (a[i - db + j] - c * b[j]) % M
    return [x % M for x in a[:db]] or [0]

from math import comb
f = [37] + [0] * 12 + [1]
h = [(comb(13, k) * pow(42, 13 - k)) % R for k in range(14)]
h[0] = (h[0] + 42) % R

r_prev, r_cur = f, h
while True:
    r_cur = trim([c % R for c in r_cur])
    if all(c == 0 for c in r_cur):
        break
    lc = r_cur[-1] % R
    g = math.gcd(lc, R)
    assert g == 1, f"factor of R leaked: {g}"
    r_cur = [c * pow(lc, -1, R) % R for c in r_cur]
    r_prev, r_cur = r_cur, monic_div(r_prev, r_cur, R)

d = r_prev  # last nonzero = monic gcd, expect degree 1
assert len(d) - 1 == 1, f"deg gcd = {len(d)-1}, not 1"
x0 = (-d[0] * pow(d[1], -1, R)) % R
gv = math.gcd(pow(x0, 13) + 37, pow(x0 + 42, 13) + 42)
assert gv % R == 0, "local check failed"
print("x0 =", x0)
print("local gcd digits:", len(str(gv)), "R | gcd: OK")

s = socket.create_connection(("archive.cryptohack.org", 3721), timeout=30)
s.settimeout(30)
pre = s.recv(4096)
s.sendall((str(x0) + "\n").encode())
out = b""
try:
    while True:
        c = s.recv(4096)
        if not c: break
        out += c
except Exception:
    pass
s.close()
txt = out.decode(errors="replace").strip()
print("server said:", txt)
open('server_response.txt', 'w').write(txt)
if "{" in txt and "}" in txt:
    open('flag_leet_universe.txt', 'w').write(txt)
    print("FLAG SAVED")
else:
    sys.exit("no flag in response")
