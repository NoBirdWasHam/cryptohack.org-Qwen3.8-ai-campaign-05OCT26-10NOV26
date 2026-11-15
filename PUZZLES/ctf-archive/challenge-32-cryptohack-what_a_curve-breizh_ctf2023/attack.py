import json, sys, os, struct, random
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")
import cantor2 as K7
P7 = 17585255163044402023
K7.set_p(P7)
SUF = b" This is your final boss, enjoy it while you still can:)"
import functools
# ---- poly helpers (monic ops) ----
gcd = lambda a, b: K7.xgcd(a, b)[0]

def ppowmod(a, e, m):
    return K7.__dict__  # placeholder no

def ppow_p(a, e, m):
    r = [1]; b = K7.pmod(a, m)
    while e:
        if e & 1:
            r = K7.pmod(K7.pmul(r, b), m)
        b = K7.pmod(K7.pmul(b, b), m); e >>= 1
    return r

def derivative(a):
    return K7.trim([(i * a[i]) % P7 for i in range(1, len(a))]) if len(a) > 1 else [0]

def factor_monic(M):
    """return list of (irreducible monic poly, exponent). M monic squarefree assumed."""
    # squarefree check
    if gcd(M, derivative(M)) != [1]:
        raise ValueError("not squarefree (rare); handle separately")
    r = M[:]; d = 1; xd = [0, 1]; ddf = []
    while K7.deg(r) >= 2 * d and r != [1]:
        xd = ppow_p(xd, P7, r)
        g = gcd(K7.psub(xd, [0, 1]), r)
        if g != [1]:
            ddf.append((d, g)); r = K7.pdiv(r, g)
        d += 1
    if r != [1]:
        ddf.append((K7.deg(r), r))
    out = []
    for d, g in ddf:
        out.extend(_edz(g, d))
    return [(h, 1) for h in out]

def _edz(g, d):
    if K7.deg(g) == d:
        return [g]
    if K7.deg(g) < d:
        raise ValueError("edz deg < d")
    expo = (P7 ** d - 1) // 2
    tries = 0
    while True:
        tries += 1
        if tries > 200:
            raise RuntimeError("edz stuck")
        a = [random.randrange(P7) for _ in range(K7.deg(g))]
        a = K7.trim(a)
        if a == [0] or a == [1]:
            continue
        b = K7.psub(ppow_p(a, expo, g), [1])
        h = gcd(b, g)
        if h != [1] and h != g:
            return _edz(h, d) + _edz(K7.pdiv(g, h), d)

def enum_divisors_deg(facs, target_deg):
    """facs: list of (poly, exp). yield all monic divisor polys of total degree target_deg."""
    res = [[1]]
    for g, e in facs:
        dg = K7.deg(g)
        new = []
        for cur in res:
            prod = cur[:]
            for s in range(0, e + 1):
                if K7.deg(prod) <= target_deg:
                    new.append(prod[:])
                prod = K7.pmul(prod, g)
        # dedupe
        uniq = []
        seen = set()
        for x in new:
            t = tuple(x)
            if t not in seen:
                seen.add(t); uniq.append(x)
        res = uniq
    return [u for u in res if K7.deg(u) == target_deg]

def attack(C, f, verbose=True):
    C = bytes(C)
    nflag = len(C) - len(SUF)
    assert nflag > 0 and nflag <= 56, "flag len %d unsupported (expect <=56)" % nflag
    Kbytes_v = bytes(a ^ b for a, b in zip(C[56:], SUF))
    vv = list(struct.unpack('<7Q', Kbytes_v))
    assert all(x < P7 for x in vv), "v coeff >= p"
    v = vv
    M = K7.psub(f, K7.pmul(v, v))
    lc = M[-1]
    Mm = K7.pscale(M, pow(lc, P7 - 2, P7))
    facs = factor_monic(Mm)
    us = enum_divisors_deg(facs, 7)
    if verbose:
        print("v:", v)
        print("factor degs:", sorted(K7.deg(g) for g, e in facs), " #u candidates:", len(us))
    cands = []
    for u in us:
        uc = [(u[i] if i < len(u) else 0) for i in range(7)]
        if any(x == 0 or x == 1 for x in uc):
            continue
        if any(x == 0 or x == 1 for x in v):
            continue
        K0 = struct.pack('<7Q', *uc)
        flag = bytes(a ^ b for a, b in zip(K0, C[:56]))
        if all(32 <= c < 127 for c in flag):
            cands.append((u, flag))
    return cands

if __name__ == "__main__":
    random.seed(1)
    # ---- offline test on OLD capture ----
    f = json.load(open("f_recovered.json"))
    hx = open("hexline.txt").read().strip()
    C = bytes.fromhex(hx)
    print("old C len:", len(C))
    cands = attack(C, f)
    print("printable candidates:", len(cands))
    for u, fl in cands:
        print("FLAG:", fl)
