#!/usr/bin/env python3
# Decisive fingerprint: is the live server's x deterministic (seeded SystemRandom)?
# Connect twice with identical (seed,q,p,g): same y => deterministic. Different
# seeds => different y => seed controls x.
import socket, random
from sympy import isprime

rng = random.Random(7)
q = None
while q is None or not isprime(q):
    q = rng.randrange(1 << 159, 1 << 160) | 1
while True:
    k = rng.getrandbits(864)
    p = k * q + 1
    if p.bit_length() == 1024 and isprime(p):
        break
h = 2
while pow(h, (p - 1) // 2, p) == 1:
    h += 1
g = pow(h, (p - 1) // q, p)
print("q,p,g ready")

def get_y(seed):
    s = socket.create_connection(("archive.cryptohack.org", 2783), timeout=20)
    f = s.makefile("rwb")
    def rd():
        d = b""
        s.settimeout(25)
        while True:
            try:
                c = f.read(1)
            except Exception:
                return d
            if not c: return d
            d += c
            if d.endswith(b": ") or d.endswith(b"\n"): return d
    rd(); f.write(str(q).encode()+b"\n"); f.flush()
    rd(); f.write(str(p).encode()+b"\n"); f.flush()
    rd(); f.write(str(g).encode()+b"\n"); f.flush()
    rd(); f.write(hex(seed)[2:].encode()+b"\n"); f.flush()
    out = b""
    s.settimeout(90)
    while True:
        try:
            c = f.read(1)
        except Exception:
            return out
        if not c: return out
        out += c
        if out.endswith(b"sign = ") or (b"\n" in out[3:] and len(out) > 200):
            return out

for seed in (0x1337, 0x1337, 0x42):
    out = get_y(seed)
    print(f"seed={seed:#x} ->", out[:120])
