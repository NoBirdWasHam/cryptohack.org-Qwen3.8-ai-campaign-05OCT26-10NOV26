#!/usr/bin/env python3
# prejudice (98) v4: 3-prime Carmichael n = p1*p2*p3, p_i = 2*f*a_i + 1, a=(1,421,2521).
#  * f = 1 mod 4, a_i = 1 mod 4  =>  p_i = 3 mod 8  =>  (2/p_i) = -1
#  * per odd prime l<=61: choose f = w mod l with (1+2w*a_i | l) = target_l for all i,
#    target_l = -1 if l=1 mod 4 else +1  (reciprocity sign for l=3 mod 4) => (b/p_i)=-1
#    for EVERY prime base b<64 and every i.
#  * v2(p_i-1)=1 all i, o_i=f*a_i odd, sum o_i = f*2943 odd => v2(n-1)=1, (n-1)/(p_i-1) odd
#    => b^((n-1)/2) = CRT(-1,-1,-1) = n-1 => MR passes at j=1 for all bases.
#  * Carmichael: p1-1=2f | n-1 automatic; a|2943+2f*2521 and a'|2943+2f*421 via CRT on f.
# Then base = p2 | n => x = pow(p2, n-1, n) ~ n/2 => FLAG[:x] = FULL FLAG.
import gmpy2, json, socket
from sympy.ntheory.modular import crt

ODD = [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61]
A1, A2, A3 = 1, 421, 2521
ASUM = A1 + A2 + A3

def leg(x, p):
    x %= p
    return 0 if x == 0 else (1 if pow(x, (p-1)//2, p) == 1 else -1)

mods, rems = [4], [1]
for l in ODD:
    tgt = -1 if l % 4 == 1 else 1
    found = None
    for w in range(l):
        if all(leg(1 + 2*w*a, l) == tgt for a in (A1, A2, A3)):
            found = w; break
    assert found is not None, f"no class for l={l}"
    mods.append(l); rems.append(found)
fa  = (-ASUM * pow(2*A3, -1, A2)) % A2
fa3 = (-ASUM * pow(2*A2, -1, A3)) % A3
mods += [A2, A3]; rems += [fa, fa3]
f0, M = crt(mods, rems)
f0, M = int(f0), int(M)
print("f0 bits:", f0.bit_length(), "M bits:", M.bit_length())

t = 2**95   # f ~ 2^193 => n ~ 2^601 (server needs >2^600)
while True:
    t += 1
    f = f0 + M*t
    p1, p2, p3 = 2*f*A1+1, 2*f*A2+1, 2*f*A3+1
    if not (gmpy2.is_prime(p1) and gmpy2.is_prime(p2) and gmpy2.is_prime(p3)):
        continue
    n = p1*p2*p3
    if not (600 < n.bit_length() <= 900):
        continue
    if any((n-1) % (q-1) for q in (p1,p2,p3)):
        continue
    r, s = 0, n-1
    while s % 2 == 0: r += 1; s //= 2
    okall = True
    for b in [2]+ODD:
        x = pow(b, s, n)
        ok = (x == 1 or x == n-1)
        for _ in range(r-1):
            x = pow(x, 2, n)
            if x == n-1: ok = True; break
        if not ok: okall = False; break
    if okall:
        print(f"FOUND t={t} n bits={n.bit_length()}", flush=True)
        break

a = p2
x = pow(a, n-1, n)
print("x bits:", x.bit_length())
s_ = socket.create_connection(("socket.cryptohack.org", 13385), timeout=30)
f_ = s_.makefile("rwb")
f_.readline()
f_.write((json.dumps({"prime": int(n), "base": int(a)}) + "\n").encode())
f_.flush()
resp = json.loads(f_.readline().decode())
f_.close(); s_.close()
print("RESPONSE:", resp["Response"])
