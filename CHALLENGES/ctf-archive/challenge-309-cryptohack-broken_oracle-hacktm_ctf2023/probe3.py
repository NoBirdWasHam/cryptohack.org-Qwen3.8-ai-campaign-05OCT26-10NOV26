# probe structure of garbage root a1 (Delta QNR mod p)
import random, gmpy2

def solve_quad(r, c, p):
    def mod(poly):
        if poly[2] == 0: return poly
        poly[1] = (poly[1] + poly[2]*r) % p
        poly[0] = (poly[0] - poly[2]*c) % p
        poly[2] = 0
        return poly
    def prod(a, b):
        return mod([a[0]*b[0] % p, (a[1]*b[0]+a[0]*b[1]) % p, a[1]*b[1] % p])
    exp = (p-1)//2
    res, cur = [1,0,0], [0,1,0]
    while True:
        if exp % 2: res = prod(res, cur)
        exp //= 2
        if exp == 0: break
        cur = prod(cur, cur)
    a1 = (-(res[0]-1) * pow(res[1], -1, p)) % p
    a2 = (r - a1) % p
    return a1, a2

p = 10**15+93
while p % 4 != 3: p += 1
c = 2
while gmpy2.jacobi(c, p) != -1: c += 1
random.seed(1)
print("p", p, "c", c)
for _ in range(15):
    r = random.randrange(1, p)
    D = (r*r - 4*c) % p
    if D == 0 or gmpy2.jacobi(D, p) != -1: continue
    a1, a2 = solve_quad(r, c, p)
    e = (a1*a2 - c) % p
    w = pow(2*a1 - r, 2, p)
    print("D", D, "e", e, "L(e)", gmpy2.jacobi(e, p) if e else 0,
          "w", w, "w==4e?", w == 4*e % p, "e==-D?", e == (-D) % p,
          "e==D?", e == D, "e==c?", e == c % p, "w==e?", w == e, "e*invD=", e * pow(D, -1, p) % p if D else 0)
