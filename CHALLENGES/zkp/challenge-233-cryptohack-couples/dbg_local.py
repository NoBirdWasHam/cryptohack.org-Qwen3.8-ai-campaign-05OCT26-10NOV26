from py_ecc.optimized_bn128 import G1, G2, multiply, pairing, is_on_curve, b, FQ
from hashlib import sha256
p = 21888242871839275222246405745257275088696311157297823662689037894645226208583

def inverse(u, v):
    u3, v3 = u, v
    u1, v1 = 1, 0
    while v3 > 0:
        q = u3 // v3
        u1, v1 = v1, u1 - v1*q
        u3, v3 = v3, u3 - v3*q
    while u1<0:
        u1 = u1 + v
    return u1

# simulate set_internal_z with z = p-5 for random x
import secrets
for _ in range(3):
    x = int(secrets.token_bytes(24).hex(),16) % p
    poly = (pow(x,(p-5)+7,p) - pow(x,3,p)) % p
    z = inverse(poly, p)
    print("poly==0:", poly==0, " z:", z, " xz%p==1:", (x*z)%p==1)

# now simulate BLS with z=0
FLAG=b"crypto{test}"
h = int(sha256(FLAG).hexdigest(),16)
H = multiply(G2,h)
x = 12345
z = 0
hsh = 1
G = G1
received_H = multiply(G2,hsh)
xzH = multiply(multiply(H,x),z)
xzG = multiply(multiply(G,x),z)
print("xzH inf:", xzH, "xzG inf:", xzG)
try:
    l = pairing(xzH, G1)
    r = pairing(received_H, xzG)
    print("l==r:", l==r, " l==1:", l==pairing(G2,G1)**0 if False else None)
except Exception as e:
    print("pairing error:", type(e).__name__, e)
