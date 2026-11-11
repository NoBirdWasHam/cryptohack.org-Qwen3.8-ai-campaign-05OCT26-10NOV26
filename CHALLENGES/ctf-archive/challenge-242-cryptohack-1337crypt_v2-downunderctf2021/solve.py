# 1337crypt v2 (DownUnderCTF 2021) - solve
# hint2[i] = (int(y), a, b) with y = A^2 + 2*A*B*p + B^2*hint1, A=a+e1/2^338, B=b+e2/2^338
# => p = round((y - a^2 - b^2*hint1) / (2ab)); q = isqrt(hint1 - p^2)
# decrypt m^0x1337 in (Z/n)[I]/(I^2+1)
import gmpy2
from gmpy2 import isqrt
from Crypto.Util.number import long_to_bytes

txt = open('output.txt').read()
hint1 = int(txt.split('hint1 = ')[1].split('\n')[0].strip())
hint2_src = txt.split('hint2 = ')[1].split('\nc = ')[0].strip()
hint2 = eval(hint2_src)
c_line = txt.split('\nc = ')[1].strip()
# format: "B*I + A"  (Sage prints imaginary term first)
lhs, rhs = c_line.split(' + ')
c_im = int(lhs.replace('*I', ''))
c_re = int(rhs)
print("hint2 entries:", len(hint2), "c_re bits:", c_re.bit_length(), "c_im bits:", c_im.bit_length())

def approx_p(y, a, b):
    num = y - a*a - b*b*hint1
    den = 2*a*b
    return (num + den//2) // den  # round

p = q = None
for (y, a, b) in hint2:
    pc = approx_p(y, a, b)
    rem = hint1 - pc*pc
    if rem > 0:
        r = isqrt(rem)
        if r*r == rem:
            p, q = int(pc), int(r)
            break
assert p is not None, "no candidate gave square q^2"
if p < q: p, q = q, p
n = p*q
print("p bits:", p.bit_length(), "p prime:", bool(gmpy2.is_prime(p)), "q prime:", bool(gmpy2.is_prime(q)))

e = 0x1337
lam = (p*p - 1) * (q*q - 1) // gmpy2.gcd(p*p - 1, q*q - 1)
d = int(gmpy2.invert(e, lam))

def gmul(x, y, mod):
    (a, b), (cc, dd) = x, y
    return ((a*cc - b*dd) % mod, (a*dd + b*cc) % mod)

def gpow(x, exp, mod):
    r = (1, 0)
    while exp:
        if exp & 1: r = gmul(r, x, mod)
        x = gmul(x, x, mod); exp >>= 1
    return r

m = gpow((c_re, c_im), d, n)
assert gpow(m, e, n) == (c_re, c_im), "re-encrypt check failed"
r_part, f_int = m
flag = long_to_bytes(f_int)
print("flag:", flag.decode(errors='replace'))
open('flag_1337crypt_v2-downunderctf2021.txt', 'w').write(flag.decode())
