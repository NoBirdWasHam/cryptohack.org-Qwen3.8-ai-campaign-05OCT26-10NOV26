# Collision finder for chaos-zh3r0_ctf_v22021: z3 solve v(X,Y,Z,U)==v(X',Y',Z',U')
import sys, json

def rotl(v, b, size=32): return ((v << b) | (v >> (size - b))) & 0xffffffff
def rotr(v, b, size=32): return ((v >> b) | (v << (size - b))) & 0xffffffff

def vfunc(X, Y, Z, U):
    M = 0xffff
    v1 = ((X & 0xffff) * (M - (Y >> 16))) ^ rotl(Z, 1) ^ rotr(U, 1)
    v2 = ((Y & 0xffff) * (M - (Z >> 16))) ^ rotl(U, 2) ^ rotr(X, 2)
    v3 = ((Z & 0xffff) * (M - (U >> 16))) ^ rotl(X, 3) ^ rotr(Y, 3)
    v4 = ((U & 0xffff) * (M - (X >> 16))) ^ rotl(Y, 4) ^ rotr(Z, 4)
    return v1 & 0xffffffff, v2 & 0xffffffff, v3 & 0xffffffff, v4 & 0xffffffff

import z3
BV = lambda n: z3.BitVec(n, 32)
X, Y, Z, U = BV("X"), BV("Y"), BV("Z"), BV("U")
Xp, Yp, Zp, Up = BV("Xp"), BV("Yp"), BV("Zp"), BV("Up")
M = z3.BitVecVal(0xffff, 32)
def rlv(v, b): return (v << b) | z3.LShR(v, 32 - b)
def rtv(v, b): return z3.LShR(v, b) | (v << (32 - b))
def vs(x, y, z, u):
    return [
        ((x & M) * (M - z3.LShR(y, 16))) ^ rlv(z, 1) ^ rtv(u, 1),
        ((y & M) * (M - z3.LShR(z, 16))) ^ rlv(u, 2) ^ rtv(x, 2),
        ((z & M) * (M - z3.LShR(u, 16))) ^ rlv(x, 3) ^ rtv(y, 3),
        ((u & M) * (M - z3.LShR(x, 16))) ^ rlv(y, 4) ^ rtv(z, 4),
    ]
a, b = vs(X, Y, Z, U), vs(Xp, Yp, Zp, Up)
s = z3.Solver()
for i in range(4): s.add(a[i] == b[i])
s.add(z3.Or(X != Xp, Y != Yp, Z != Zp, U != Up))
print("solving...", flush=True)
if s.check() != z3.sat:
    print("UNSAT"); sys.exit(1)
m = s.model()
vals = {n: m[n].as_long() for n in (X, Y, Z, U, Xp, Yp, Zp, Up)}
print(json.dumps({k: hex(v) for k, v in vals.items()}), flush=True)
# sanity in python ints
p1 = vfunc(vals['X'], vals['Y'], vals['Z'], vals['U'])
p2 = vfunc(vals['Xp'], vals['Yp'], vals['Zp'], vals['Up'])
assert p1 == p2 and (vals['X'], vals['Y'], vals['Z'], vals['U']) != (vals['Xp'], vals['Yp'], vals['Zp'], vals['Up'])
print("v-collision OK", [hex(x) for x in p1], flush=True)
