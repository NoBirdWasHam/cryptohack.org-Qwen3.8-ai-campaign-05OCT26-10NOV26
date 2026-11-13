import random, sys
sys.path.insert(0, ".")
from solve2 import check_branch, RO
from params import p, q, g

def gen():
    w0 = random.randint(0, q); y0 = pow(g, w0, p)
    w1 = random.randint(0, q); y1 = pow(g, w1, p)
    return w0, w1, y0, y1

def fischlin(w0, w1, y0, y1, b):
    if b: w_sim, w_b, y_sim, y_b = w0, w1, y0, y1
    else: w_sim, w_b, y_sim, y_b = w1, w0, y1, y0
    r = random.randint(0, q); a_b = pow(g, r, p)
    e_sim = random.randint(0, 2**511-1); z_sim = random.randint(0, q)
    a_sim = (pow(pow(y_sim, e_sim, p), -1, p) * pow(g, z_sim, p)) % p
    t = 2**10; B = 6
    for e in range(t):
        e_b = e ^ e_sim; z_b = (r + e_b * w_b) % q
        if b: a0, a1, e0, e1, z0, z1 = a_sim, a_b, e_sim, e_b, z_sim, z_b
        else: a1, a0, e1, e0, z1, z0 = a_sim, a_b, e_sim, e_b, z_sim, z_b
        if RO(a0, a1, e, e0, e1, z0, z1) < 2**(512-B): break
    return {"a0": a0, "a1": a1, "e": e, "e0": e0, "e1": e1, "z0": z0, "z1": z1}

N = 1500
pass1 = pass0 = 0
for i in range(N):
    w0, w1, y0, y1 = gen()
    if check_branch(0, w0, fischlin(w0, w1, y0, y1, 1)): pass1 += 1
    if check_branch(0, w0, fischlin(w0, w1, y0, y1, 0)): pass0 += 1
print("P(pass|b=1 simulated):", pass1/N, " P(pass|b=0 real):", pass0/N)
