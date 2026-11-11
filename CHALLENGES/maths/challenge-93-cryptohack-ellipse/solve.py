# Ellipse Curve (#93): "conic" x^2 - 529 y^2 = 1 (529=23^2) over F_p.
# The group law is just multiplication in F_p* via the homomorphism t = x + 23y.
# So [n]G <-> t(G)^n ; DLP is in <t(G)> which has order (p-1)/2 (smooth: 8 primes ~30b).
# Solve via Pohlig-Hellman + per-prime BSGS. n is only known mod (p-1)/2, so two
# candidates; the shared secret x = (t + t^-1)/2 differs, but only one decrypts cleanly.
import math
from sympy import factorint, mod_inverse
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import sha1

p   = 173754216895752892448109692432341061254596347285717132408796456167143559
d   = 23
Gx  = 29394812077144852405795385333766317269085018265469771684226884125940148
Gy  = 94108086667844986046802106544375316173742538919949485639896613738390948
Ax  = 155781055760279718382374741001148850818103179141959728567110540865590463
Ay  = 73794785561346677848810778233901832813072697504335306937799336126503714
Bx  = 171226959585314864221294077932510094779925634276949970785138593200069419
By  = 54353971839516652938533335476115503436865545966356461292708042305317630

def t(x, y): return (x + d * y) % p

g = t(Gx, Gy)
a = t(Ax, Ay)
order = 86877108447876446224054846216170530627298173642858566204398228083571779
assert pow(g, order, p) == 1, "order wrong"
assert (Gx*Gx - 529*Gy*Gy) % p == 1

F = factorint(order)

def bsgs(base, target, q, mod):
    m = math.isqrt(q) + 1
    table = {}
    cur = 1
    for j in range(m + 1):
        table[cur] = j
        cur = cur * base % mod
    step = pow(base, -m, mod)
    giant = target
    for i in range(m + 1):
        if giant in table:
            return (table[giant] + m * i) % q
        giant = giant * step % mod
    return None

n = 0; M = 1
for q in sorted(F):
    q = int(q)
    base = pow(g, order // q, p)
    tgt = pow(a, order // q, p)
    x = bsgs(base, tgt, q, p)
    assert x is not None and pow(base, x, p) == tgt
    # incremental CRT: n' = n + M*(x-n)*inv(M mod q)  mod (M*q)
    n = (n + M * ((x - n) * mod_inverse(M % q, q) % q)) % (M * q)
    M *= q

assert M == order
assert pow(g, n, p) == a, "g^n != a : DLP/CRT wrong"
print("DLP n_a =", n, " (verified g^n==a)")

half = (p - 1) // 2
tb = t(Bx, By)
iv = bytes.fromhex('64bc75c8b38017e1397c46f85d4e332b')
ct = bytes.fromhex('13e4d200708b786d8f7c3bd2dc5de0201f0d7879192e6603d7c5d6b963e1df2943e3ff75f7fda9c30a92171bbbc5acbf')
inv2 = mod_inverse(2, p)
for cand in (n, (n + half) % (p - 1)):
    tt = pow(tb, cand, p)
    x_shared = (tt + pow(tt, -1, p)) % p * inv2 % p
    key = sha1(str(x_shared).encode()).digest()[:16]
    try:
        pt = unpad(AES.new(key, AES.MODE_CBC, iv=iv).decrypt(ct), 16)
        print("SOLVED n candidate ->", pt.decode())
    except Exception:
        print("candidate fails padding")
