import random, math
from gmpy2 import is_prime, invert

PREF = b'SECUREHASH_'
P = int.from_bytes(PREF,'big')
def exp_of(msg): return int.from_bytes(PREF+msg,'big')

# simulate server: fresh g,p; answer l n m o
p = random.getrandbits(256)
while not is_prime(p): p = random.getrandbits(256)
g = random.getrandbits(256) % p
H = {c: pow(g, exp_of(bytes([c])), p) for c in b'lnmo'}

D1 = H[ord('l')]*H[ord('n')] - H[ord('m')]**2
D2 = H[ord('l')]*H[ord('o')] - H[ord('n')]*H[ord('m')]
print("D1 bits", D1.bit_length(), "D2 bits", D2.bit_length())
print("p | D1:", D1 % p == 0, " p | D2:", D2 % p == 0)
gg = math.gcd(abs(D1), abs(D2))
print("gcd == p:", gg == p, " gcd bits:", gg.bit_length())
# g recovery
e = exp_of(b'l')
if math.gcd(e, p-1) == 1:
    gr = pow(H[ord('l')], invert(e, p-1), p)
    print("g recovered:", gr == g)
else:
    print("e_l not invertible, gcd", math.gcd(e,p-1))
