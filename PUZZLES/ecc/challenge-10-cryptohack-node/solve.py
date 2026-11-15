# node: recover secret a,b from G,Q -> curve is SINGULAR (nodal, split) ->
# E_ns(F_p) ~ F_p^* via phi(P) = (t-s)/(t+s), t = y/(x-x0), s^2 = c = 3*x0.
# Then DLP in F_p^* (p-1 smooth-ish) via PARI znlog.
from Crypto.Util.number import inverse, long_to_bytes
from sympy import sqrt_mod
import subprocess, re, sys

F = "~/Practice_runs/cryptohack_org/challenge-121-cryptohack-node/"
p = 4368590184733545720227961182704359358435747188309319510520316493183539079703
gx = 8742397231329873984594235438374590234800923467289367269837473862487362482
gy = 225987949353410341392975247044711665782695329311463646299187580326445253608
qx = 2582928974243465355371953056699793745022552378548418288211138499777818633265
qy = 2421683573446497972507172385881793260176370025964652384676141384239699096612
a = 64186688762130075872648727143532923412208390610536286437268423112
b = 32579945572763798990069104934898692239152360555014084068553395172709029894
O = None  # point at infinity

def padd(P, Q):
    if P is O: return Q
    if Q is O: return P
    if (P[1] + Q[1]) % p == 0 and P[0] == Q[0]: return O
    if P == Q:
        lam = (3*P[0]**2 + a) * inverse(2*P[1], p) % p
    else:
        lam = (Q[1] - P[1]) * inverse(Q[0] - P[0], p) % p
    Rx = (lam*lam - P[0] - Q[0]) % p
    Ry = (lam*(P[0] - Rx) - P[1]) % p
    return (Rx, Ry)

def pmul(P, n):
    R, Q = O, P
    while n:
        if n & 1: R = padd(R, Q)
        Q = padd(Q, Q)
        n >>= 1
    return R

x0 = (-3 * b * inverse(2 * a, p)) % p
c = (3 * x0) % p
s = sqrt_mod(c, p)
assert (s*s - c) % p == 0

def phi(P):
    X = (P[0] - x0) % p
    t = P[1] * inverse(X, p) % p
    return (t - s) * inverse(t + s, p) % p

G = (gx, gy); Qp = (qx, qy)
g, h = phi(G), phi(Qp)

# sanity: phi is a homomorphism for the source's group law?
for k in (2, 3, 5):
    lhs = phi(pmul(G, k)); rhs = pow(g, k, p)
    print(f"phi({k}G)==g^{k}:", lhs == rhs)
    if lhs != rhs:
        # try inverse convention
        def phi2(P):
            X = (P[0] - x0) % p
            t = P[1] * inverse(X, p) % p
            return (t + s) * inverse(t - s, p) % p
        g2, h2 = phi2(G), phi2(Qp)
        if all(phi2(pmul(G, k)) == pow(g2, k, p) for k in (2, 3, 5)):
            g, h = g2, h2
            print("switched to inverse convention")
            break
        sys.exit("no homomorphism convention worked")

# DLP in F_p^* via PARI znlog
gp = f'''default(parisize,"512M");
g = {g}; h = {h}; p = {p};
k = znlog(Mod(h,p), Mod(g,p), p-1);
print("k=", k);
'''
open(F + "dl.gp", "w").write(gp)
out = subprocess.run(["~/tools/gp64.exe", "-q", F + "dl.gp"],
                     capture_output=True, text=True).stdout
print(out)
k = int(re.search(r"k=\s*(\d+)", out).group(1))
print("check k*G == Q:", pmul(G, k) == Qp)
flag = long_to_bytes(k)
print("flag bytes:", flag)
open(F + "flag_node.txt", "wb").write(flag)
