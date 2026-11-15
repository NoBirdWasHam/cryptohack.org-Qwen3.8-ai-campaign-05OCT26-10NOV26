import re

txt = open(r"~/AppData/Local/hermes/cache/scratch/unbal/output.txt").read()
N = int(re.search(r"N = (0x[0-9a-f]+)", txt).group(1), 16)
e = int(re.search(r"e = (0x[0-9a-f]+)", txt).group(1), 16)
c = int(re.search(r"c = (0x[0-9a-f]+)", txt).group(1), 16)
print("N bits", N.bit_length(), "e bits", e.bit_length())
print("e/N =", e / float(N) if e < 2**2000 else "big")

# relation: e*d - 1 = k*(N - p - q + 1)
# => k*phi + 1 == 0 mod e ; s = p + N/p
# multiply k*phi+1=0 mod e by p:  k*(N*p - p^2 - N + p) + p == 0 mod e
p, q = 3, 11
Nt = p * q
phi = (p - 1) * (q - 1)
et = 3
dt = pow(et, -1, phi)
kt = (et * dt - 1) // phi
print("tiny: k=", kt, "poly mod e =", (kt * (Nt * p - p * p - Nt + p) + p) % et)

# Boneh-Durfee bound Y^(2+3t) * Z^(1+3t+3t^2) < e^(1+3t) for (k, s=p+q-1)
import math
logE = math.log2(e)
print("log2 e =", round(logE, 1))
Y = 2 ** 301          # k bound (d ~ 2^300)
Z = 2 ** 770          # s = p+q-1 bound
for t in [i / 100 for i in range(0, 301)]:
    lhs = math.log2(Y) * (2 + 3 * t) + math.log2(Z) * (1 + 3 * t + 3 * t * t)
    rhs = logE * (1 + 3 * t)
    if lhs < rhs:
        print("BD bound satisfied at tau=", t, "lhs", round(lhs), "rhs", round(rhs))
        break
else:
    print("BD bound NOT satisfied; best gap:",
          min((math.log2(Y) * (2 + 3 * t) + math.log2(Z) * (1 + 3 * t + 3 * t * t)
               - logE * (1 + 3 * t), t) for t in [i / 1000 for i in range(0, 3001)]))
