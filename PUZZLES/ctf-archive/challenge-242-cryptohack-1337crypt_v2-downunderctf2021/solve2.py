# 1337crypt v2 - full solve (lattice on linearized hint equations)
import gmpy2
from gmpy2 import isqrt
from fractions import Fraction as F
from math import gcd
from Crypto.Util.number import long_to_bytes

txt = open('output.txt').read()
h1 = int(txt.split('hint1 = ')[1].split('\n')[0])
h2 = eval(txt.split('hint2 = ')[1].split('\nc = ')[0])
cl = txt.split('\nc = ')[1].strip()
lhs, rhs = cl.split(' + ')
c_im = int(lhs.replace('*I', '')); c_re = int(rhs)
L = 2**338

def pval(y, a, b, beta):
    B = F(b) + F(beta, L)
    return (F(y) - F(a*a) - B*B*h1) / (2*F(a)*B)

(y1,a1,b1),(y2,a2,b2) = h2
p10, p20 = pval(y1,a1,b1,0), pval(y2,a2,b2,0)
q1 = (pval(y1,a1,b1,L) - p10) / L
q2 = (pval(y2,a2,b2,L) - p20) / L
D0 = p20 - p10

Lc = q1.denominator
Lc = Lc * q2.denominator // gcd(Lc, q2.denominator)
Lc = Lc * D0.denominator // gcd(Lc, D0.denominator)
W1 = int(q1 * Lc); W2 = int(q2 * Lc); D = int(D0 * Lc)
print("bits W1,W2,Lc,D:", W1.bit_length(), W2.bit_length(), Lc.bit_length(), D.bit_length())

# Weighted CVP: W1*b1 - W2*b2 = D + err, |err| <= 16*Lc ; b_i in [0,L)
ctr = L//2
Dp = D - ctr*(W1 - W2)
Wt = 2**(8339 - 337)   # weight box coords so |Wt*beta'| ~ |err| ~ 2^8339
basis = [(Wt, 0, W1), (0, Wt, -W2)]
target = (0, 0, Dp)

from fpylll import IntegerMatrix, LLL, CVP
M = IntegerMatrix(2,3)
for i in range(2):
    for j in range(3):
        M[i,j] = basis[i][j]
LLL.reduction(M)
s = CVP.closest_vector(M, (0, 0, Dp))
assert int(s[0]) % Wt == 0 and int(s[1]) % Wt == 0
beta1 = int(s[0])//Wt + ctr
beta2 = int(s[1])//Wt + ctr
err = W1*beta1 - W2*beta2 - D
print("beta1 ok:", 0 <= beta1 < L, "beta2 ok:", 0 <= beta2 < L)
print("err bits:", abs(err).bit_length(), "Lc bits:", Lc.bit_length())

found = None
for d1 in range(-3, 4):
    for d2 in range(-3, 4):
        b1c, b2c = beta1 + d1, beta2 + d2
        if not (0 <= b1c < L and 0 <= b2c < L):
            continue
        pe = int(pval(y1, a1, b1, b1c))
        for dp in range(-12, 13):
            p = pe + dp
            rem = h1 - p*p
            if rem > 0:
                r = isqrt(rem)
                if r*r == rem and gmpy2.is_prime(p) and gmpy2.is_prime(int(r)):
                    found = (int(p), int(r)); break
        if found: break
    if found: break
assert found, "no (p,q)"
p, q = found
print("p,q bits:", p.bit_length(), q.bit_length())
n = p*q
e = 0x1337
lam = (p*p-1)*(q*q-1)//gmpy2.gcd(p*p-1, q*q-1)
d = int(gmpy2.invert(e, lam))
def gmul(x,y,mod):
    (aa,bb),(cc,dd)=x,y
    return ((aa*cc-bb*dd)%mod,(aa*dd+bb*cc)%mod)
def gpow(x,ex,mod):
    r=(1,0)
    while ex:
        if ex&1: r=gmul(r,x,mod)
        x=gmul(x,x,mod); ex>>=1
    return r
m = gpow((c_re,c_im), d, n)
assert gpow(m,e,n)==(c_re,c_im), "re-encrypt failed"
flag = long_to_bytes(m[1])
print("FLAG:", flag.decode())
open('flag_1337crypt_v2-downunderctf2021.txt','w').write(flag.decode())
