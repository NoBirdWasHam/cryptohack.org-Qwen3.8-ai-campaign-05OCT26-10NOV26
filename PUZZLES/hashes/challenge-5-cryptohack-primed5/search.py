#!/usr/bin/env python
"""primed5 (100 pts) — collision search driver.

Attack (see AAR.md): the 'check' endpoint verifies an RSA signature on
MD5(long_to_bytes(p)) WITHOUT re-checking that p is prime, while 'sign' only
signs primes. So: find a prime p (<=1024 bits) and a number p' with a divisor
a >= 24 such that MD5(long_to_bytes(p)) == MD5(long_to_bytes(p')).
  - sign p  (server, prime check passes)
  - check with prime=p', a=a: signature verifies (same digest),
    g = gcd(a, p') = a >= 24 = len(FLAG)  ->  FLAG[:g] = the whole flag.

The collision pair comes from md5fastcoll (Marc Stevens, hashclash core):
two 128-byte messages that collide, differing only in words 4/11/14 of each
block. Per pair we accept iff int(M1) is prime and int(M2) has a factor a>=24
(either its 23-smooth part, or a prime factor in [29, 1e6]).
Acceptance ~ 1/2 (odd last byte) * 1/710 (primality) * ~0.996 (small factor)
~ 1/720, ~0.6 s per pair, 4 parallel workers -> a few minutes.
"""
import subprocess
import sys
import os
import time
from sympy import isprime
from sympy import primerange

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, "md5fastcoll", "pairgen.exe")

SMALL = [5, 7, 11, 13, 17, 19, 23]          # primes < 24
BIG = [p for p in primerange(29, 10**6)]    # primes in [29, 1e6)
FLAG_LEN = 24


def find_factor(pp):
    """Return a divisor a of pp with a >= 24 (and a < pp), or None."""
    a = 1
    t = pp
    for f in SMALL:
        while t % f == 0:
            a *= f
            t //= f
    if a >= FLAG_LEN:
        return a
    for f in BIG:
        if pp % f == 0:
            return f
    return None


def read_exact(f, n):
    buf = b""
    while len(buf) < n:
        chunk = f.read(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def worker(wid):
    t0 = time.time()
    pairs = 0
    proc = subprocess.Popen(
        [EXE], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        cwd=os.path.join(HERE, "md5fastcoll"))
    try:
        while True:
            data = read_exact(proc.stdout, 256)
            if data is None:
                print(f"[w{wid}] generator exited", flush=True)
                return None
            M1, M2 = data[:128], data[128:]
            pairs += 1
            if M1[0] == 0 or M2[0] == 0:
                continue                      # long_to_bytes() strips leading zeros
            p = int.from_bytes(M1, "big")
            if not (M1[-1] & 1):
                continue
            if not isprime(p):
                continue
            pp = int.from_bytes(M2, "big")
            a = find_factor(pp)
            if a is None:
                continue
            # sanity
            import hashlib
            assert hashlib.md5(M1).digest() == hashlib.md5(M2).digest()
            assert p.bit_length() <= 1024
            assert 24 <= a < pp
            print(f"[w{wid}] FOUND after {pairs} pairs in {time.time()-t0:.1f}s", flush=True)
            out = os.path.join(HERE, "collision")
            os.makedirs(out, exist_ok=True)
            open(os.path.join(out, f"m1_w{wid}.bin"), "wb").write(M1)
            open(os.path.join(out, f"m2_w{wid}.bin"), "wb").write(M2)
            open(os.path.join(out, f"a_w{wid}.txt"), "w").write(str(a))
            return (p, pp, a, M1, M2, pairs)
    finally:
        proc.kill()


if __name__ == "__main__":
    wid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    r = worker(wid)
    if r:
        p, pp, a, M1, M2, pairs = r
        print("p (prime to sign) =", p)
        print("p' (for check)    =", pp)
        print("a (gcd factor)    =", a)
        print("md5(M1) =", __import__("hashlib").md5(M1).hexdigest())
        print("md5(M2) =", __import__("hashlib").md5(M2).hexdigest())
