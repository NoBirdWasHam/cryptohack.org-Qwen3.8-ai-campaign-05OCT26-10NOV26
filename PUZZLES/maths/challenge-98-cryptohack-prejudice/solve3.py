#!/usr/bin/env python3
# prejudice (98) v3: Arnault-style 3-prime Carmichael, strong pseudoprime to ALL
# prime bases < 64, then a = factor of p -> x = pow(a,p-1,p) huge -> FLAG[:x] = full flag.
#
# Build p_i = 4·F·s_i + 1 (s_i odd small, F odd): v2(p_i-1) = 2.
#  * Carmichael: (p_i-1)|(n-1) iff S=s1s2s3 | 4F(s1+s2+s3)+1  (linear congruence on F)
#  * v2(n-1) = 2 (3 odd o_i sum odd) => (n-1)/(p_i-1) odd
#  * p_i = 5 mod 8  => (2/p_i) = -1 ; p_i = c mod odd-primes<=61 with c simultaneous
#    QNR => (b/p_i) = -1 for every odd prime base b<64 (reciprocity, p_i = 1 mod 4).
#  => b^((n-1)/2) = CRT(-1,-1,-1) = n-1 => MR base b passes at j=1 for ALL bases.
import gmpy2, json, socket
from sympy.ntheory.modular import crt

ODD = [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61]
def qnr(p):
    a = 2
    while pow(a, (p-1)//2, p) != p-1: a += 1
    return a
mods = [8] + ODD
rems = [5] + [qnr(l) for l in ODD]
c = int(crt(mods, rems)[0])          # p_i = c mod N: QNR for every base <64
N = 1
for m in mods: N *= m                # N = 8*3*5*...*61

s1, s2, s3 = 1, 3, 5
S = s1*s2*s3
SUM = s1+s2+s3
# F = 4*N*t + a0:  a0 = c * inv(4N, S) mod S  (so 4F*S? -> 4F*SUM+1 = 0 mod S)
a0 = (c * pow(4*N, -1, S)) % S
if a0 % 2 == 0: a0 += S              # keep F odd
K = 4*N
# F = K*t + a0 ; need F = a0 mod S too: K*t + a0 = 0 mod S? build F = S*(K*t + a0')... simpler:
# F ranges over a0 + S*Z and a0 + S*Z must also be c mod N: F = c mod N and F = a0 mod S:
F0 = int(crt([N, S], [c % N, a0 % S])[0])
FN = N*S
print("c bits:", c.bit_length(), "N bits:", N.bit_length(), "F0 bits:", F0.bit_length())

def primes_ok(F):
    p1, p2, p3 = 4*F*s1+1, 4*F*s2+1, 4*F*s3+1
    if not (gmpy2.is_prime(p1) and gmpy2.is_prime(p2) and gmpy2.is_prime(p3)):
        return None
    n = p1*p2*p3
    if not (600 < n.bit_length() <= 900):
        return None
    # verify Carmichael + strong-liar for every prime base < 64
    for q in (p1,p2,p3):
        if (n-1) % (q-1): return None
    r, s = 0, n-1
    while s % 2 == 0: r += 1; s //= 2
    for b in [2]+ODD:
        x = pow(b, s, n)
        ok = (x == 1 or x == n-1)
        for _ in range(r-1):
            x = pow(x, 2, n)
            if x == n-1: ok = True; break
        if not ok: return None
    return (n, (p1,p2,p3))

t = 0
while True:
    t += 1
    F = F0 + FN*t
    got = primes_ok(F)
    if got:
        n, facs = got
        print(f"FOUND at t={t}: n bits={n.bit_length()}")
        break

a = facs[1]                       # a = p2 | n  ->  x = pow(a,n-1,n) ~ n/2
x = pow(a, n-1, n)
print("x bits:", x.bit_length())
s = socket.create_connection(("socket.cryptohack.org", 13385), timeout=30)
f = s.makefile("rwb")
f.readline()
f.write((json.dumps({"prime": int(n), "base": int(a)}) + "\n").encode())
f.flush()
resp = json.loads(f.readline().decode())
f.close(); s.close()
print("RESPONSE:", resp["Response"])
