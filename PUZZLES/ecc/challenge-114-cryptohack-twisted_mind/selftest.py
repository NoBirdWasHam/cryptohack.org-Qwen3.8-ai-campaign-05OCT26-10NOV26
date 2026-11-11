#!/usr/bin/env python3
"""Local self-test of the 114 attack pipeline: simulate server, known key, verify PH recovers k mod S."""
import random
import solve

p, a, b = solve.p, solve.a, solve.b
order, S, Q = solve.order, solve.S, solve.Q

# server ladder (verbatim)
def dbl(P1):
    X1, Z1 = P1
    XX = X1**2 % p
    ZZ = Z1**2 % p
    A = 2 * ((X1 + Z1) ** 2 - XX - ZZ) % p
    aZZ = a * ZZ % p
    X3 = ((XX - aZZ) ** 2 - 2 * b * A * ZZ) % p
    Z3 = (A * (XX + aZZ) + 4 * b * ZZ**2) % p
    return (X3, Z3)
def diffadd(P1, P2, x0):
    X1, Z1 = P1
    X2, Z2 = P2
    X1Z2 = X1 * Z2 % p
    X2Z1 = X2 * Z1 % p
    Z1Z2 = Z1 * Z2 % p
    T = (X1Z2 + X2Z1) * (X1 * X2 + a * Z1Z2) % p
    Z3 = (X1Z2 - X2Z1) ** 2 % p
    X3 = (2 * T + 4 * b * Z1Z2**2 - x0 * Z3) % p
    return (X3, Z3)
def server_scalarmult(scalar, x0):
    R0 = (x0, 1)
    R1 = dbl(R0)
    n = scalar.bit_length()
    pbit = 0
    bit = 0
    for i in range(n - 2, -1, -1):
        bit = (scalar >> i) & 1
        pbit = pbit ^ bit
        if pbit:
            R0, R1 = R1, R0
        R1 = diffadd(R0, R1, x0)
        R0 = dbl(R0)
        pbit = bit
    if bit:
        R0 = R1
    if R0[1] == 0:
        return "Infinity"
    return R0[0] * pow(R0[1], p - 2, p) % p

random.seed(12345)
k = random.randrange(1, order // 2)
print(f"test key k = {k}")
print(f"k mod S    = {k % S}")

P_S = solve.find_point_of_order(S, "P_S")
P_Q = solve.find_point_of_order(Q, "P_Q")

A1x = server_scalarmult(k, P_S[0])
A2x = server_scalarmult(k, P_Q[0])
print(f"A1 = {str(A1x)[:40]}...")
print(f"A2 = {str(A2x)[:40]}...")

# curve checks
A1 = solve.lift(A1x)
A2 = solve.lift(A2x)
print("A1 on curve:", A1 is not None, " S*A1==O:", solve.pt_mul(S, A1) is None)
print("A2 on curve:", A2 is not None, " Q*A2==O:", solve.pt_mul(Q, A2) is None,
      " S*A2!=O:", solve.pt_mul(S, A2) is not None)

# PH
for sign, A1s in [(1, A1), (-1, (A1[0], p - A1[1]))]:
    residues = {}
    for q in solve.SMOOTH_FACTORS:
        G = solve.pt_mul(S // q, P_S)
        T = solve.pt_mul(S // q, A1s)
        e = solve.bsgs(G, T, q)
        assert (e * G == T) or (T is None and e == 0) or solve.pt_mul(e, G) == T
        residues[q] = e
    r = 0
    m = 1
    for q, e in residues.items():
        mi = pow(m, -1, q)
        r = (r + (e - r) * mi % q * m) % (m * q)
        m *= q
    ok = (r % S == k % S) or ((S - r) % S == k % S)
    print(f"sign={sign}: k mod S candidate = {r}   matches k%S: {ok}")
