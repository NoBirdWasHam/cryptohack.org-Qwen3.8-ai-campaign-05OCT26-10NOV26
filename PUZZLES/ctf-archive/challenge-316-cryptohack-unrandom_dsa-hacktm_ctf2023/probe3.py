#!/usr/bin/env python3
"""Fingerprint the server's q-primality rounds: send a smooth composite q that
passes exactly the first t predicted MR bases (+Lucas). If the server prints
y=, its rounds<=t and the RNG stream matches our replication."""
import os, random, socket, sys, time
os.urandom = random.randbytes
from Crypto.Util.number import getPrime, isPrime, isqrt
from Crypto.Math.Numbers import Integer
from Crypto.Math.Primality import lucas_test, PROBABLY_PRIME

SEED = 0x1337

def predicted_bases(p, q, n=30):
    random.seed(SEED)
    Integer(p).is_probable_prime()  # replicate p's test consumption exactly
    # replicate miller_rabin_test(q, rounds) base draws
    bases = []
    one, minus_one = Integer(1), Integer(q - 1)
    d = q - 1
    s = 0
    while d % 2 == 0:
        d //= 2; s += 1
    for _ in range(n):
        base = Integer(1)
        while base in (one, minus_one):
            base = Integer.random_range(min_inclusive=2, max_inclusive=q - 2)
        bases.append(int(base))
    return bases

def mr_pass(base, q):
    d = q - 1; s = 0
    while d % 2 == 0:
        d //= 2; s += 1
    z = pow(base, d, q)
    if z in (1, q - 1):
        return True
    for _ in range(s - 1):
        z = z * z % q
        if z == q - 1:
            return True
    return False

def gen_smooth_q(rng, maxbits=40):
    while True:
        q = 1
        for _ in range(4):
            q *= getPrime(maxbits, rng)
        if q.bit_length() == 160:
            return q

def find_q(t, rng):
    tries = 0
    while True:
        tries += 1
        q = gen_smooth_q(rng)
        if not (q & 1): continue
        bases = predicted_bases(P, q)
        ok = all(mr_pass(b, q) for b in bases[:t])
        if ok and not mr_pass(bases[t], q):
            if lucas_test(Integer(q)) == PROBABLY_PRIME:
                print(f"found q after {tries} tries: {q}")
                return q
        if tries % 2000 == 0:
            print(f"  t={t} tries={tries}", flush=True)

rng = random.Random(99)
# choose q first, then p = k*q+1 prime
print("gen q0...")
q0 = gen_smooth_q(rng)
print("q0 =", q0)
print("gen p = k*q0+1 prime...")
while True:
    k = rng.getrandbits(864)
    P = k * q0 + 1
    if P.bit_length() == 1024 and isPrime(P):
        break
print("P ok")
for t in (3, 6):
    q = find_q(t, rng) if False else None
# do t=3 first
q = find_q(3, rng)
# p must be k*q+1 prime
while True:
    k = rng.getrandbits(864)
    P = k * q + 1
    if P.bit_length() == 1024 and isPrime(P):
        break
h = 2
while pow(h, (P - 1) // 2, P) == 1:
    h += 1
g = pow(h, (P - 1) // q, P)
assert 1 < g < P and pow(g, q, P) == 1
print("sending q (t=3 bypass candidate)...")
s = socket.create_connection(("archive.cryptohack.org", 17001), timeout=20)
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
print("q =", repr(rd())); f.write(str(q).encode() + b"\n"); f.flush()
print("p =", repr(rd())); f.write(str(P).encode() + b"\n"); f.flush()
print("g =", repr(rd())); f.write(str(g).encode() + b"\n"); f.flush()
print("seed =", repr(rd())); f.write(hex(SEED)[2:].encode() + b"\n"); f.flush()
s.settimeout(60)
out = f.read(400)
print("RESPONSE:", out[:300])
s.close()
