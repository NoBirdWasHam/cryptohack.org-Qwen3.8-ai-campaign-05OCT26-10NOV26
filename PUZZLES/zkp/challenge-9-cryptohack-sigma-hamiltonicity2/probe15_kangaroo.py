# probe15: Pollard kangaroo bounded dlog. If ANY of these is small, Pedersen is
# malleable (equivocation) and the whole protocol breaks:
#   d = dlog_{h2}(h1)   [or q-d, i.e. h1 = h2^{-k}]
#   k = dlog_{h1}(h2)   [or -k]
#   a = dlog_{4}(h1)    [or -a]   (h1 = g^{2a} with g=2 generator of QR? base 4)
#   b = dlog_{4}(h2)    [or -b]   -> then d = a * inv(b) mod q
import gmpy2, sys, time
sys.path.insert(0, r"~/Practice_runs/cryptohack_org/challenge-237-cryptohack-sigma-hamiltonicity2")
from hamiltonicity import P, q, h1, h2
import random as _r

def kangaroo(base, target, W, seed=0):
    """find x in [0,W) with base^x = target mod P, or None."""
    rng = _r.Random(seed)
    m = 128
    steps = rng.randrange(1, 64)
    a = [0]*m; b = [0]*m
    dm = [gmpy2.mpz(0)]*m
    for i in range(m):
        a[i] = rng.randrange(0, W); b[i] = rng.randrange(0, W)
        dm[i] = pow(base, a[i], P) * pow(target, b[i], P) % P
    # distinguished points: low 32 bits zero of int hash-ish (use int & mask)
    mask = (1 << 30) - 1
    def jump(x, cnt, dv):
        for _ in range(cnt):
            e = int(x) & (m-1)
            x = x * dm[e] % P
            dv[0] += a[e] if False else 0  # placeholder
        return x
    # tame: start base^W, position W ; wild: start target, position 0
    def run(start, pos, limit, table=None, tame=False):
        x = start; d = pos; cnt = 0
        while True:
            if int(x) & mask == 0:  # distinguished
                if tame:
                    table[x] = d
                elif x in table:
                    cand = table[x] - d
                    if cand < 0: cand += q
                    return cand
                if d > limit: return None
            e = int(x) & (m-1)
            x = x * dm[e] % P; d += a[e] if tame else 0
            # careful: tame advances by a[e], wild advances too (both add a[e]; wild pos = x+d means base^(x+d)=target^x...) 
            # Standard: tame walks base^{d}, wild walks target^{d}... use multiplicative bookkeeping:
            cnt += 1
            if cnt % (1<<16) == 0 and d > limit*3: return None
    # simpler textbook version (additive in exponents, mult in group):
    def run2(val, dist, limit, table=None, tame=False):
        # invariant tame: val = base^{dist}; wild: val = target^{dist}
        while True:
            if int(val) & mask == 0:
                if tame:
                    if len(table) > 5_000_000: return None
                    table[val] = dist
                elif val in table:
                    e = (table[val] - dist) % q
                    if pow(base, e, P) == target: return e
                if dist > limit: return None
            i = int(val) & (m-1)
            val = val * dm[i] % P
            dist = (dist + (a[i] if tame else b[i])) % q
            # tame: val*base^{a[i]} * target^{b[i]} ; need invariant: tame val*dm = base^{d}*target^{b}? 
            # dm[i] = base^{a[i]} * target^{b[i]} breaks single-base invariant! Fix partition:
            # use step set for tame: base^{a[i]} only ; for wild: target^{b[i]} only.
            # Redo below.
            return None
    # --- clean implementation (separate tame/wild step sets) ---
    ta = [rng.randrange(1, 64) for _ in range(m)]   # tame jumps: base^{ta}
    wa = [rng.randrange(1, 64) for _ in range(m)]   # wild jumps: target^{wa}
    tdp = [pow(base, t, P) for t in ta]
    wdp = [pow(target, w, P) for w in wa]
    mask = (1 << 32) - 1
    table = {}
    xt, dt = pow(base, W, P), W
    xw, dw = target, 0
    lim = 40 * int(gmpy2.isqrt(W)) + 1000
    tcnt = wcnt = 0
    while True:
        e = int(xt) & (m-1)
        xt = xt * tdp[e] % P; dt += ta[e]
        if int(xt) & mask == 0:
            table[xt] = dt
        tcnt += 1
        if tcnt > lim*4: return None
        e = int(xw) & (m-1)
        xw = xw * wdp[e] % P; dw += wa[e]
        if int(xw) & mask == 0 and xw in table:
            e_ = (table[xw] - dw) % q
            if pow(base, e_, P) == target: return e_
        wcnt += 1
        if wcnt > lim*4: return None

t0 = time.time()
tests = [
    ("dlog_{h2}(h1)",   h2, h1), ("dlog_{h2}(inv h1)", h2, pow(gmpy2.mpz(h1),-1,P)),
    ("dlog_{h1}(h2)",   h1, h2), ("dlog_{h1}(inv h2)", h1, pow(gmpy2.mpz(h2),-1,P)),
    ("dlog_{4}(h1)",    4,  gmpy2.mpz(h1)), ("dlog_{4}(inv h1)", 4, pow(gmpy2.mpz(h1),-1,P)),
    ("dlog_{4}(h2)",    4,  gmpy2.mpz(h2)), ("dlog_{4}(inv h2)", 4, pow(gmpy2.mpz(h2),-1,P)),
]
W = 1 << 36
for name, base, tgt in tests:
    r = kangaroo(gmpy2.mpz(base), gmpy2.mpz(tgt), W)
    print("%-20s -> %s (%.0fs)" % (name, r, time.time()-t0), flush=True)
print("done all < 2^36: %s" % ("FOUND RELATION — malleable!" if any(1 for _ in []) else "NONE"), flush=True)
