# xcheck.py — independent (sympy) root-intersection test of OLD resultants r0..r5_594
import sys
sys.set_int_max_str_digits(10**7)
import sympy as sp

def load(fn):
    co = [int(l) for l in open(fn)]
    x = sp.Symbol('x')
    return sp.Poly(sum(sp.Integer(c)*x**i for i,c in enumerate(co)), x)

u = sp.Symbol('x')
Ps = [load(f"r{i}_594.txt") for i in range(4)]
import gmpy2
allr = {}
for p in (5,7,11,13,17,19,23):
    sets = []
    for P in Ps:
        Rp = P.set_modulus(p)
        xpx = sp.Poly(u**p - u, u, modulus=p)
        g = sp.gcd(Rp, xpx)
        rs = set()
        for f1,e in g.factor_list()[1]:
            if f1.degree() == 1:
                a1,a0 = f1.all_coeffs()
                rs.add(int((-a0*sp.invert(a1,p)) % p))
        sets.append(rs)
    inter = set.intersection(*sets) if sets else set()
    allr[p] = inter
    print(p, [sorted(s) for s in sets], "INTER:", sorted(inter), flush=True)
# CRT on intersections
cands = None; M = 1
for p in sorted(allr):
    rp = allr[p]
    if not rp: print("empty at", p); break
    if cands is None: cands = set(rp); M = p
    else:
        new = set()
        for a in cands:
            ra = a % p
            if ra in rp:
                t = ((ra-a)*int(gmpy2.invert(M,p))) % p
                new.add(a+M*t)
        cands = new; M *= p
    print("after", p, "cands:", sorted(cands)[:6], "Mbits", M.bit_length(), flush=True)
