# Irish flan: quaternion conjugation over Z/nZ.
# phi(x)=chi^-1 x chi = rotation of pure part about axis A = gamma_pure (parallel to chi_pure).
# v=alpha_pure ; Rv = -N(alpha)*beta_pure (from beta=phi(alpha^-1)) ; R^m v = epsilon_pure.
# Rotation about FIXED axis behaves like a complex number (c,s) in basis {x, J(x)=A x}:
#   c = (vx.w)/|vx|^2 , s = (J(vx).w)/(|vx|^2 L2)  for w = R^t v.
# lambda^(m+1) = lambda * lambda^m by complex mult mod n -> t = R^{m+1} v.
# kappa = (a_alpha/N, -t/N) since kappa = phi^{m+1}(alpha^-1). Then k = kappa^-1 mu kappa^-1,
# K = sha256(str(k)), decrypt AES-CBC.
import re, ast, hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

import sys
txt = open(sys.argv[1] if len(sys.argv)>1 else "output.txt").read()

def qparse(s):
    return [int(x) for x in re.findall(r"(-?\d+) \(mod", s)]

line1, line2 = [l for l in txt.splitlines() if l.strip()][:2]
n = int(line1.split(",")[0].split(":")[1])
qs1 = re.findall(r"\(-?\d+ \(mod \d+\)(?:,-?\d+ \(mod \d+\)){3}\)", line1)
alpha, beta, gamma = [qparse(q) for q in qs1]

first_q = re.search(r"\(-?\d+ \(mod \d+\)", line2)
mu, eps = [qparse(q) for q in
           re.findall(r"\(-?\d+ \(mod \d+\)(?:,-?\d+ \(mod \d+\)){3}\)", line2)]
cblob = line2[len("Encryption: "):first_q.start()].strip().rstrip(",").strip()
ct = ast.literal_eval(cblob)

inv = lambda x: pow(x, -1, n)
M3 = lambda: None

def dot(u, v): return sum((ui * vi) for ui, vi in zip(u, v)) % n
def cross(u, v): return [(u[1]*v[2]-u[2]*v[1]) % n, (u[2]*v[0]-u[0]*v[2]) % n, (u[0]*v[1]-u[1]*v[0]) % n]
def smul(s, v): return [(s*vi) % n for vi in v]

aa = alpha[0]; Nal = dot(alpha, alpha) % n
v   = alpha[1:]
Rv  = smul((-Nal) % n, beta[1:])           # R v
e   = eps[1:]                               # R^m v
A   = gamma[1:]                             # axis, parallel to chi_pure
L2  = dot(A, A) % n
vA  = dot(v, A) % n
vx  = [(vi - vA * inv(L2) % n * Ai) % n for vi, Ai in zip(v, A)]   # perp part
Lvx = dot(vx, vx) % n
ivx = inv(Lvx)

def J(x): return cross(A, x)

def complex_of(w):
    c = dot(vx, w) % n * ivx % n
    s = dot(J(vx), w) % n * ivx % n * inv(L2) % n
    return c, s

lam   = complex_of(Rv)   # rotation R
lam_m = complex_of(e)    # R^m
assert (lam[0]**2 + lam[1]**2 * L2) % n == 1, "lam not unit-complex"
assert (lam_m[0]**2 + lam_m[1]**2 * L2) % n == 1, "lam_m not unit-complex"

def cmul(z1, z2): return ((z1[0]*z2[0] - z1[1]*z2[1]*L2) % n, (z1[0]*z2[1] + z1[1]*z2[0]) % n)

c1, s1 = cmul(lam, lam_m)                  # R^{m+1}
t = [(c1*a + s1*b) % n for a, b in zip(vx, J(vx))]
t = [(t[i] + vA * inv(L2) % n * A[i]) % n for i in range(3)]          # add back parallel part

Ninv = inv(Nal)
kappa = [aa * Ninv % n] + [(n - ti) % n * Ninv % n for ti in t]       # phi^{m+1}(alpha^-1)

# quaternion ops mod n
def qmul(x, y):
    a,b,cc,d = x; e1,f,g,h = y
    return [(a*e1-b*f-cc*g-d*h) % n, (a*f+b*e1+cc*h-d*g) % n,
            (a*g-b*h+cc*e1+d*f) % n, (a*h+b*g-cc*f+d*e1) % n]
def qinv(x):
    d = dot(x, x) % n; di = inv(d)
    return [x[0]*di % n, -x[1]*di % n, -x[2]*di % n, -x[3]*di % n]

k = qmul(qmul(qinv(kappa), mu), qinv(kappa))
sk = "(" + ",".join(f"{xi} (mod {n})" for xi in k) + ")"
K = hashlib.sha256(sk.encode()).digest()
pt = unpad(AES.new(K, AES.MODE_CBC, iv=b"\0"*16).decrypt(ct), 16)
print(pt.decode())
