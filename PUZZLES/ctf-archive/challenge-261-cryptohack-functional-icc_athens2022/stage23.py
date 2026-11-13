import re, ast, json, hashlib
from Crypto.Cipher import AES
p = 2**142 - 111
txt = open('output.txt').read()
stage2 = txt.split('Stage 2:')[1].split('Stage 3:')[0]
S3 = ast.literal_eval(re.search(r'\[.*\]', stage2, re.S).group(0))
assert len(S3) == 1337
ct_hex = txt.split('Stage 3:')[1].split('========')[1].strip()
ITERS = json.load(open('iters.json'))['ITERS']

# recurrence coefficients a_i, taps j(n-9900-i), i=0..99
import math
a = [int(10000*math.log(31337+i)) % p for i in range(100)]
# initial j(n) n<10^4: sum S3[d] over base-1337 digits
def digits(n, b=1337):
    d=[]
    while n: d.append(n%b); n//=b
    return d or [0]
J = [sum(S3[d] for d in digits(n)) % p for n in range(10000)]
# quick identity test: does recurrence keep digit-sum form up to 60000?
ext = J[:]
ident = True
for n in range(10000, 60000):
    v = sum(a[i]*ext[n-9900-i] for i in range(100)) % p
    ext.append(v)
    if v != sum(S3[d] for d in digits(n)) % p:
        ident = False
        print("digit-sum identity fails first at n =", n)
        break
print("identity holds to 60000:", ident)

# Bostan-Mori: J(x)=P(x)/Q(x), Q = 1 - sum a_i x^{9901+i}
Q = {0: 1}
for i in range(100):
    Q[9901+i] = (-a[i]) % p
LIMB = 320
MASK = (1 << LIMB) - 1
def pack(coeffs):  # list low-first -> mpz
    s = 0
    for c in reversed(coeffs):
        s = (s << LIMB) | c
    return s
def unpack(t, ln):
    out = []
    for _ in range(ln):
        out.append(t & MASK); t >>= LIMB
    return out
# P = (J*Q) truncated deg<10000
P = J[:]
for k in range(9901, 10000):
    sub = sum(a[i]*J[k-9901-i] for i in range(100)) % p
    P[k] = (P[k] - sub) % p
n = ITERS
packP = pack(P)
while n > 0:
    Qm = {e: ((c if e % 2 == 0 else (-c) % p)) for e, c in Q.items()}
    # S = P * Qm via packed shifts
    t = 0
    for e, c in Qm.items():
        if c:
            t += packP << (LIMB*e)
    d = len(P) + max(Qm)  # S degree bound
    limbs = unpack(t, d)
    keep_even = (n % 2 == 0)
    start = 0 if keep_even else 1
    P = [limbs[j] % p for j in range(start, d, 2)]
    # Q = even(Poly(Q*Qm))
    S2 = {}
    items = list(Q.items())
    for e1, c1 in items:
        for e2, c2 in Qm.items():
            ee = e1 + e2
            if ee % 2 == 0:
                S2[ee//2] = (S2.get(ee//2, 0) + c1*c2) % p
    Q = S2
    packP = pack(P)
    n //= 2
jt = P[0] * pow(Q.get(0, 1), p-2, p) % p
print("j(ITERS) =", jt)
key = hashlib.sha256(str(jt).encode()).digest()
pt = AES.new(key, AES.MODE_ECB).decrypt(bytes.fromhex(ct_hex))
print("PLAINTEXT:", pt)
