# RRSSAA: partial factorization via MT seed brute-force on small indices, partial CRT decrypt.
# Each factor of N comes from random.Random() seeded with < 2^i; small i => tiny seed space.
# Collect enough distinct primes whose product P > 2^1024 >= flag; then m^e mod P = c mod P
# and m < P, so RSA over P recovers the flag exactly (P | N).
import random
from math import prod, gcd
from Crypto.Util.number import isPrime, long_to_bytes

lines = open("output.txt").read().split()
N, c = int(lines[0], 16), int(lines[1], 16)
e = 0x10001

def gen_prime(seed):
    r = random.Random()
    r.seed(seed)
    p = 1
    while not isPrime(p):
        p = r._randbelow(2**256) | 1
    return p

# For every index i <= K the seed is < 2^i <= 2^K, so one global seed scan
# in [0, 2^K) provably finds the primes of ALL indices i <= K (plus lucky hits).
K = 14
factors = set()
for seed in range(2**K):
    p = gen_prime(seed)
    if N % p == 0:
        factors.add(p)
        print(f"[+] seed={seed} p={p}")

usable = [p for p in factors if gcd(e, p - 1) == 1]
best, P = [], 1
for p in sorted(usable, reverse=True):
    best.append(p); P *= p
    if P > 2**1024:
        break
assert P > 2**1024, f"only {P.bit_length()} bits from {len(usable)} primes - widen scan"
d = pow(e, -1, prod(p - 1 for p in best))
m = pow(c, d, P)
assert pow(m, e, N) == c, "full consistency check failed"
flag = long_to_bytes(m)
assert len(flag) == 128
print("flag:", flag.decode())
open("flag_rrssaa-ecsc_2023_norway2023.txt", "w").write(flag.decode())
