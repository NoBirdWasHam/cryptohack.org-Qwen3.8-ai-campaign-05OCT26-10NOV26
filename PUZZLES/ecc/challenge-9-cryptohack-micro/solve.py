# micro (CryptoHack, ecc, 120 pts): ECDH with 64-bit secret on a smooth-order curve.
# #E = 7*11*17*191*317*331*5221385621*5397618469*210071842937040101*637807437018177170959577732683
# Product of the first 7 factors ~ 2^67 > 2^64 > n_a, so PH over small factors pins n_a
# uniquely (x-only sign ambiguity killed by the size bound n_a < 2^64).
import hashlib
from math import isqrt
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

p = 99061670249353652702595159229088680425828208953931838069069584252923270946291
a, b = 1, 4
N = 99061670249353652702595159229088680426160873357666659718134032418967620849171
G = (43190960452218023575787899214023014938926631792651638044680168600989609069200,
     20971936269255296908588589778128791635639992476076894152303569022736123671173)
ax = 87360200456784002948566700858113190957688355783112995047798140117594305287669
bx = 6082896373499126624029343293750138460137531774473450341235217699497602895121
iv = bytes.fromhex('ceb34a8c174d77136455971f08641cc5')
ct = bytes.fromhex('b503bf04df71cfbd3f464aec2083e9b79c825803a4d4a43697889ad29eb75453')

O = None

def on_curve(P):
    if P is O:
        return True
    x, y = P
    return (y * y - (x * x * x + a * x + b)) % p == 0

def add(P, Q):
    if P is O: return Q
    if Q is O: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return O
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def mul(k, P):
    R = O
    while k:
        if k & 1:
            R = add(R, P)
        P = add(P, P)
        k >>= 1
    return R

def lift_x(x):
    rhs = (x * x * x + a * x + b) % p
    y = pow(rhs, (p + 1) // 4, p)  # p = 3 mod 4
    assert y * y % p == rhs
    return (x, y)

def bsgs(Gq, Tq, q):
    """e in [0,q) with e*Gq == Tq (Gq of prime order q)."""
    m = isqrt(q) + 1
    table = {}
    cur = O
    for j in range(m):
        table.setdefault(cur, j)
        cur = add(cur, Gq)
    mG = mul(m, Gq)
    neg_mG = (mG[0], (-mG[1]) % p)
    gamma = Tq
    for i in range(m):
        j = table.get(gamma)
        if j is not None:
            e = (j + i * m) % q
            assert mul(e, Gq) == Tq
            return e
        gamma = add(gamma, neg_mG)
    raise RuntimeError("BSGS failed")

def crt(residues, mods):
    r, M = 0, 1
    for ri, mi in zip(residues, mods):
        t = (ri - r) * pow(M % mi, -1, mi) % mi
        r += M * t
        M *= mi
        r %= M
    return r, M

assert on_curve(G) and mul(N, G) is O

# Pohlig-Hellman over factors whose product exceeds 2^64
factors = [7, 11, 17, 191, 317, 331, 5221385621, 5397618469]
A = lift_x(ax)
assert on_curve(A)
residues = []
for q in factors:
    Gq = mul(N // q, G)
    assert mul(q, Gq) is O and Gq is not O  # exact order q (q prime)
    Tq = mul(N // q, A)
    residues.append(bsgs(Gq, Tq, q))

r, S = crt(residues, factors)
assert S > 1 << 64
# x-only: r == +n_a or -n_a mod S; n_a < 2^64 < S - 2^64 decides uniquely
n_a = r if r < (1 << 64) else S - r
assert n_a < (1 << 64) and mul(n_a, G)[0] == ax

B = lift_x(bx)  # sign of B is irrelevant: x(n*(-B)) == x(n*B)
shared = mul(n_a, B)[0]
key = hashlib.sha1(str(shared).encode('ascii')).digest()[:16]
flag = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), 16)
print("n_a =", n_a)
print("flag =", flag.decode())
