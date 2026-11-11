#!/usr/bin/env python3
"""Is the RAW p-part delta(k) of the ladder response linear in k (formal-group prediction)?"""
from Crypto.Util.number import GCD, inverse
import random

modulus = 13407807929942597099574024998205846127479365820592393377723561443721764030029777567070168776296793595356747829017949996650141749605031603191442486002224009
p0 = 115792089237316195423570985008687907853269984665640564039457584007913129639747
a, b = -3, 152961

def dbl(P1):
    X1, Z1 = P1
    XX = X1**2 % modulus; ZZ = Z1**2 % modulus
    A = 2 * ((X1 + Z1) ** 2 - XX - ZZ) % modulus
    aZZ = a * ZZ % modulus
    return (((XX - aZZ) ** 2 - 2 * b * A * ZZ) % modulus, (A * (XX + aZZ) + 4 * b * ZZ**2) % modulus)

def diffadd(P1, P2, x0):
    X1, Z1 = P1; X2, Z2 = P2
    X1Z2 = X1 * Z2 % modulus; X2Z1 = X2 * Z1 % modulus; Z1Z2 = Z1 * Z2 % modulus
    T = (X1Z2 + X2Z1) * (X1 * X2 + a * Z1Z2) % modulus
    Z3 = (X1Z2 - X2Z1) ** 2 % modulus
    return ((2 * T + 4 * b * Z1Z2**2 - x0 * Z3) % modulus, Z3)

def scalarmult(scalar, x0):
    R0 = (x0, 1); R1 = dbl(R0)
    n = scalar.bit_length(); pbit = 0
    for i in range(n - 2, -1, -1):
        bit = (scalar >> i) & 1
        pbit = pbit ^ bit
        if pbit: R0, R1 = R1, R0
        R1 = diffadd(R0, R1, x0)
        R0 = dbl(R0)
        pbit = bit
    if bit: R0 = R1
    if GCD(R0[1], modulus) != 1: return "Infinity"
    return R0[0] * inverse(R0[1], modulus) % modulus

random.seed(11)
def sqrt_fp(n):
    return pow(n, (p0 + 1) // 4, p0)

while True:
    x0 = random.randrange(2, p0)
    t = (x0**3 + a*x0 + b) % p0
    if sqrt_fp(t)**2 % p0 == t: break
y0 = sqrt_fp((x0**3 + a*x0 + b) % p0)

print("k, C(k)=delta*y^2/(k*xi*(xi^2+3a))  [expect constant if model holds]")
Cs = []
for k in range(2, 15):
    r = scalarmult(k, x0)
    xi = r % p0
    delta = (r - xi) // p0
    # y(k) sign: ladder gives x only; try both signs, C for each
    rhs = (xi**3 + a*xi + b) % p0
    eta = sqrt_fp(rhs)
    denom = (k * xi % p0) * ((xi*xi + 3*a) % p0) % p0
    for sgn, yy in ((1, eta), (-1, p0 - eta)):
        C = delta * yy % p0 * inverse(denom, p0) % p0
        Cs.append((k, sgn, C))
    print(k, "C+ =", Cs[-2][2] % p0 if False else Cs[-2][2], " C- =", Cs[-1][2], flush=True)
