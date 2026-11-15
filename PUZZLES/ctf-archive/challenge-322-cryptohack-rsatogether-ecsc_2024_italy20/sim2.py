# End-to-end offline sim: exact server model, kernel combo -> phi-multiple -> Miller factor -> decrypt.
import random, sys, json, os
sys.set_int_max_str_digits(10**6)
from math import comb
from Crypto.Util.number import getPrime, bytes_to_long, long_to_bytes
from factor_from_phi_multiple import factor_from_multiple

random = random.SystemRandom()
NB = int(sys.argv[1]) if len(sys.argv) > 1 else 512
flag = b"ECSC{sim_flag_ok}"
p = getPrime(NB//2); q = getPrime(NB//2); n = p*q
phi = (p-1)*(q-1); e = 65537
d = pow(e, -1, phi)
poly = [d] + [random.getrandbits(NB) for _ in range(99)]

def eval_poly(pl, x, nn):
    return sum(pow(x, i, nn)*pl[i] for i in range(len(pl))) % nn

def yours(kinp):                      # input n_shares=k -> t=k+1 nodes, pop -> x=k share
    t = kinp + 1
    pl = poly[:t]
    ys = [eval_poly(pl, i, phi) for i in range(1, t+1)]
    coeffs = [(-1)**(j-1)*comb(t, j) for j in range(1, t+1)]
    sh = [(c*y) % phi for c, y in zip(coeffs, ys)]
    return sh.pop(t-2)

u = {k: yours(k) for k in range(1, 102)}
# model check vs beta formula (exp1)
for k in range(1, 102):
    beta = (-1)**(k-1)*(k+1)
    Pk = sum(poly[i]*k**i for i in range(min(k, 99)+1))
    assert u[k] == (beta*Pk) % phi, k
print("model ok")

K = json.load(open("kernel.json"))
mu = [int(v) for v in K["mu"]]
M0 = sum(mu[k-1]*u[k] for k in range(1, 102))
print("M0 bits:", abs(M0).bit_length(), "multiple of phi:", M0 % phi == 0, "nonzero:", M0 != 0)
assert M0 % phi == 0 and M0 != 0
p2, q2 = factor_from_multiple(n, M0)
assert p2*q2 == n
phi2 = (p2-1)*(q2-1)
d2 = pow(e, -1, phi2)
pad = os.urandom((NB-8)//8 - len(flag)) + flag
ct = pow(bytes_to_long(pad), e, n)
pt = long_to_bytes(pow(ct, d2, n))
print("FLAG:", pt[pt.rfind(b"ECSC"):])
print("SIM FULL SUCCESS")
