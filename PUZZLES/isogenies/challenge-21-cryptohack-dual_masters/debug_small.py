# Debug: verify dual chain composes to [2^e] on a tiny instance.
import random, gmpy2
from isog_lib import F, EC, build_chain, dual_map, velu2

random.seed(3)
e_a, e_b = 5, 4
p = 2**e_a * 3**e_b - 1
assert gmpy2.is_prime(p)
Fp2 = F(p)
E = EC(Fp2, Fp2.zero(), Fp2.one())
cof = 3**e_b
def rand_point():
    while True:
        x = (random.randrange(p), random.randrange(p))
        rhs = Fp2.add(Fp2.mul(x, Fp2.mul(x, x)), Fp2.one())
        try: y = Fp2.sqrt(rhs)
        except ValueError: continue
        if Fp2.eq(Fp2.sq(y), rhs): return (x, y)
while True:
    R1 = E.mul(rand_point(), cof); R2 = E.mul(rand_point(), cof)
    if R1 is None or R2 is None: continue
    U1, U2 = E.mul(R1, 2**(e_a-1)), E.mul(R2, 2**(e_a-1))
    if U1 and U2 and not Fp2.eq(U1[0], U2[0]): Pa, Qa = R1, R2; break
n = random.randrange(2**e_a)
R = E.add(Pa, E.mul(Qa, n))
steps_f, EA, _ = build_chain(E, R, e_a)
def apply_step(Ecx, pt, e, t):
    if pt is None: return None
    x, y = pt
    if Fp2.eq(x, e): return None
    ui = Fp2.inv(Fp2.sub(x, e))
    return (Fp2.add(x, Fp2.mul(t, ui)), Fp2.mul(y, Fp2.sub(Fp2.one(), Fp2.mul(t, Fp2.sq(ui)))))
Qp = Qa
for (e, t, *_r) in steps_f: Qp = apply_step(EA, Qp, e, t)
print("Qp on EA:", EA.on(Qp))

steps_h, Efin, _ = build_chain(EA, Qp, e_a)
print("Efin a=0:", Fp2.eq(Efin.a, Fp2.zero()), " b:", Efin.b[:1], "...")

# TEST 1: hat^ o hat = [2^e_a] on EA
U = rand_point()
U = EA.mul(U, 3**e_b)  # land in 2-power part (not strictly needed)
hU = U
for (e, t, *_r) in steps_h: hU = apply_step(None, hU, e, t)
d2 = dual_map(Fp2, steps_h, hU)
ref = EA.mul(U, 2**e_a)
print("TEST1 hat^hat(U)==[2^e]U:", (d2 is None and ref is None) or (d2 is not None and ref is not None and Fp2.eq(d2[0], ref[0]) and Fp2.eq(d2[1], ref[1])))

# TEST 2: candidates for isomorphism
b216 = Efin.b
c = Fp2.fcbrt(b216); s_ = Fp2.sqrt(b216)
q = p*p
base = (2,1); omega = Fp2.pow(base, (q-1)//3)
while Fp2.eq(omega, Fp2.one()):
    base = (base[0]+1, base[1]); omega = Fp2.pow(base, (q-1)//3)
for i, u2 in enumerate([c, Fp2.mul(c, omega), Fp2.mul(c, Fp2.sq(omega))]):
    for sgn, u3 in [("+", s_), ("-", Fp2.neg(s_))]:
        S = (Fp2.mul(u2, Qa[0]), Fp2.mul(u3, Qa[1]))
        onE = Efin.on(S)
        img = dual_map(Fp2, steps_h, S)
        match = img is not None and Fp2.eq(img[0], Qp[0]) and Fp2.eq(img[1], Qp[1])
        print(f"cand u2={i} u3={sgn}: S on Efin={onE}, img on EA={EA.on(img)}, match Qp={match}")
