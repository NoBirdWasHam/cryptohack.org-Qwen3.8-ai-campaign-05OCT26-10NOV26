# probe15b: Pollard lambda (kangaroo) bounded dlog, clean version.
# Finds x in [0,W) with base^x = target mod P. Meeting: tame walks DOWN from
# base^W (invariant val = base^{dt}), wild walks UP (invariant val = target^{dw}).
# On equality: dt = x*dw mod q  ->  x = dt * dw^{-1} mod q  (verified by pow).
# If ANY listed relation is small, Pedersen is malleable (equivocation).
import gmpy2, sys, time
sys.path.insert(0, r"~/Practice_runs/cryptohack_org/challenge-237-cryptohack-sigma-hamiltonicity2")
from hamiltonicity import P, q, h1, h2
import random as _r

def kangaroo(base, target, W, seed=1):
    rng = _r.Random(seed)
    m = 128
    ta = [rng.randrange(1, 64) for _ in range(m)]
    wa = [rng.randrange(1, 64) for _ in range(m)]
    tdp = [pow(base, -t, P) for t in ta]      # tame jumps DOWN
    wdp = [pow(target, w, P) for w in wa]     # wild jumps UP
    mask = (1 << 16) - 1                      # distinguished if low 16 bits == 0
    root = int(gmpy2.isqrt(W)) + 1
    lim  = 16 * root
    table = {}
    xt, dt = pow(base, W, P), W
    xw, dw = target, 1                        # target^1
    for _ in range(lim):
        e = int(xt) & (m-1)
        xt = xt * tdp[e] % P; dt -= ta[e]
        if dt < 0: return None
        if int(xt) & mask == 0: table[xt] = dt
        e = int(xw) & (m-1)
        xw = xw * wdp[e] % P; dw += wa[e]
        if int(xw) & mask == 0 and xw in table:
            cand = (table[xw] * pow(gmpy2.mpz(dw), -1, q)) % q
            if pow(base, cand, P) == target: return cand
    return None

# self-test on a known small exponent first
t0 = time.time()
st = kangaroo(gmpy2.mpz(h2), pow(gmpy2.mpz(h2), 123456789, P), 1 << 30)
print("selftest (expect 123456789):", st, "(%.0fs)" % (time.time()-t0), flush=True)

tests = [
    ("dlog_{h2}(h1)",   h2, h1), ("dlog_{h2}(-h1)", h2, pow(gmpy2.mpz(h1),-1,P)),
    ("dlog_{h1}(h2)",   h1, h2), ("dlog_{h1}(-h2)", h1, pow(gmpy2.mpz(h2),-1,P)),
    ("dlog_{4}(h1)",    4,  gmpy2.mpz(h1)), ("dlog_{4}(-h1)", 4, pow(gmpy2.mpz(h1),-1,P)),
    ("dlog_{4}(h2)",    4,  gmpy2.mpz(h2)), ("dlog_{4}(-h2)", 4, pow(gmpy2.mpz(h2),-1,P)),
    ("dlog_{h1}(4)",    h1, gmpy2.mpz(4)),  ("dlog_{h2}(4)", h2, gmpy2.mpz(4)),
]
W = 1 << 36
hits = []
for name, base, tgt in tests:
    try:
        r = kangaroo(gmpy2.mpz(base), gmpy2.mpz(tgt), W)
    except Exception as ex:
        r = "EXC %s" % ex
    print("%-16s -> %s (%.0fs)" % (name, r, time.time()-t0), flush=True)
    if r: hits.append((name, r))
print("RESULT:", hits if hits else "no small relation < 2^36 (10 tests)")
