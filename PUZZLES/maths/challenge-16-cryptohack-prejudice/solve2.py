#!/usr/bin/env python3
# prejudice (98): server returns FLAG[:pow(a,p-1,p)] for (a,p) passing MR(bases<64),
# 600 < bits(p) <= 900, 1 <= a < p. Prime p => x=1 (Fermat) => only 'c'.
# ATTACK: Chernick Carmichael p=(6m+1)(12m+1)(18m+1), all prime, m = (61#/6)*j so
# q2=12m+1 = 1 mod 2*61# => Legendre(b,q2)=+1 for every prime b<64 => p is a STRONG
# pseudoprime to all MR bases the server uses (v2(p-1)=v2(q2-1)=2+v2(m), q2 unique max).
# Then a = q2 (a factor of p): x = pow(q2,p-1,p) = CRT(1,0,1) ~ p/2 >> 41 => FULL FLAG.
import gmpy2, json, random, socket, sys

def generate_basis(n):
    basis = [True] * n
    for i in range(3, int(n**0.5)+1, 2):
        if basis[i]:
            basis[i*i::2*i] = [False]*((n-i*i-1)//(2*i)+1)
    return [2] + [i for i in range(3, n, 2) if basis[i]]

def miller_rabin(n, b):   # verbatim server logic
    basis = generate_basis(b)
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False
    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1; s //= 2
    for b in basis:
        x = pow(b, s, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True

PRIMES64 = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61]
M0 = 1
for b in PRIMES64: M0 *= b
M0 *= 2                       # m = M0*j: q2 = 12M0 j+1 = 1 mod 2*61# (all Legendre +1)

tries = 0
while True:
    tries += 1
    j = 2**125 + tries
    m = M0 * j
    q1, q2, q3 = 6*m+1, 12*m+1, 18*m+1
    if not (gmpy2.is_prime(q1) and gmpy2.is_prime(q2) and gmpy2.is_prime(q3)):
        continue
    p = q1 * q2 * q3
    if not (600 < p.bit_length() <= 900):
        continue
    if not miller_rabin(p, 64):
        print("carmichael but failed MR?!", tries); continue
    a = int(q2)
    x = pow(a, p-1, p)
    if x > 41:
        print(f"FOUND after {tries} tries: bits(p)={p.bit_length()} x={x.bit_length()}-bit")
        break

s = socket.create_connection(("socket.cryptohack.org", 13385), timeout=30)
f = s.makefile("rwb")
f.readline()
f.write((json.dumps({"prime": int(p), "base": a}) + "\n").encode())
f.flush()
resp = json.loads(f.readline().decode())
f.close(); s.close()
print("RESPONSE:", resp["Response"])
