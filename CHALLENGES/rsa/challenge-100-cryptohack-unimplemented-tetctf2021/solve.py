# Unimplemented (TETCTF): RSA over Gaussian integers mod n = p^2 q^2.
# private_key = (p, q) is leaked in output.txt. Implement the missing decrypt:
# unit group of Z/p^2[i] has order p^2(p^2-1) if p=3 mod 4 (inert),
# p^2(p-1)^2 if p=1 mod 4 (split). Invert e mod lcm, decrypt per component,
# CRT, then strip the random pad.
import ast, re, random
from collections import namedtuple
from math import gcd

Complex = namedtuple("Complex", ["re", "im"])

def cmul(c1, c2, m):
    return Complex((c1.re*c2.re - c1.im*c2.im) % m,
                   (c1.re*c2.im + c1.im*c2.re) % m)

def cpow(c, e, m):
    r = Complex(1, 0)
    while e > 0:
        if e & 1: r = cmul(r, c, m)
        c = cmul(c, c, m); e >>= 1
    return r

def unit_order(p):  # |(Z/p^2[i])^*|
    return p*p*(p*p-1) if p % 4 == 3 else p*p*(p-1)**2

def lcm(a, b): return a // gcd(a, b) * b

src = open('output.txt', encoding='utf-8', errors='replace').read()
p, q = ast.literal_eval(re.search(r"private_key = (\(.*?\))", src, re.S).group(1))
n = int(re.search(r"public_key = (\d+)", src).group(1))
ct = ast.literal_eval(re.search(r"ciphertext = (b'.*')", src, re.S).group(1))
assert n == p*p*q*q
L = (n.bit_length() + 7) // 8
assert len(ct) == 2 * L
c = Complex(int.from_bytes(ct[:L], 'big'), int.from_bytes(ct[L:], 'big'))
e = 65537

lam = lcm(unit_order(p), unit_order(q))
assert gcd(e, lam) == 1
d = pow(e, -1, lam)

def cpow_crt(c, exp):
    mp = cpow(Complex(c.re % (p*p), c.im % (p*p)), exp, p*p)
    mq = cpow(Complex(c.re % (q*q), c.im % (q*q)), exp, q*q)
    a = pow(q*q, -1, p*p)
    b = pow(p*p, -1, q*q)
    re_ = (mp.re*q*q*a + mq.re*p*p*b) % n
    im_ = (mp.im*q*q*a + mq.im*p*p*b) % n
    return Complex(re_, im_)

# sanity: encrypt-then-decrypt round-trips a random unit (validates glue)
r = Complex(random.randrange(n), random.randrange(n))
rt = cpow_crt(cpow(r, e, n), d)
assert (rt.re, rt.im) == (r.re, r.im), "roundtrip failed"

m = cpow_crt(c, d)
Lh = (n.bit_length() - 1) // 8          # 252-byte halves
re_pt = m.re.to_bytes(Lh, 'big')
im_pt = m.im.to_bytes(Lh, 'big')
pt = re_pt + im_pt                       # padded plaintext, 504 bytes
i = pt.index(b'\x00')                    # real separator (pad_data has no 0 bytes)
flag = pt[i+1:]
assert b'TetCTF{' in flag, repr(flag[:50])
print(flag.decode(errors='replace'))
