#!/usr/bin/env python3
# unrandom_dsa FINAL attack:
#  q=3 (real prime), p = 4-prime STRONG CARMICHAEL pseudoprime (passes pycryptodome
#  test_probable_prime: all MR bases liars + Lucas), p % 3 == 1, g of order 3 with
#  g=1 mod r1. x=randint(1,2); choose s parity so 3 | u2 -> y^{u2}=1 -> v indep of x.
#  r := v computed locally; send (r,s) -> FLAG.
import itertools, random, time, json
from sympy import isprime
from Crypto.Math.Primality import test_probable_prime, lucas_test, PROBABLY_PRIME, COMPOSITE
from Crypto.Math.Numbers import Integer

def v2(x): return (x & -x).bit_length()-1

ODD = [o for o in range(1, 80, 2)]
PATTERNS = None

def patterns():
    global PATTERNS
    if PATTERNS: return PATTERNS
    P = []
    for pat in itertools.combinations(ODD, 4):
        E2 = sum(a*b for a,b in itertools.combinations(pat,2))
        ok = True
        for i in range(4):
            oi = pat[i]; rest=[pat[j] for j in range(4) if j!=i]
            E2i = sum(a*b for a,b in itertools.combinations(rest,2))
            if (2*E2i) % oi: ok=False; break
        if ok: P.append(pat)
    PATTERNS = P
    return P

def try_m(pat, m, rbits=256):
    # r_i = 2*o_i*m + 1 all prime?
    rs=[]
    for o in pat:
        r = 2*o*m+1
        if r.bit_length()!=rbits: return None,None
        if not isprime(r): return None,None
        rs.append(r)
    p = rs[0]*rs[1]*rs[2]*rs[3]
    if p.bit_length()!=1024: return None,None
    cs=[r-1 for r in rs]
    if any((p-1)%c for c in cs): return None,None      # Korselt
    if max(v2(c) for c in cs) >= v2(p-1): return None,None  # strict 2-adic
    return p, rs

def build(timeout_s=3600, seedbits=3, verbose=True):
    P = patterns()
    if verbose: print('patterns:', len(P), flush=True)
    rng=random.Random(2026)
    t0=time.time()
    while time.time()-t0 < timeout_s:
        for pat in P:
            for scale in range(60, 140):
                base=1<<(scale+121)   # m ~ 2^(scale+121): r ~ 2^(122+scale)
                for _ in range(300):
                    m = base + rng.randrange(base//2)
                    m |= 1
                    p, rs = try_m(pat, m)
                    if p is None: continue
                    if test_probable_prime(p) != PROBABLY_PRIME: continue
                    if lucas_test(Integer(p)) != PROBABLY_PRIME: continue
                    if p % 3 != 1:
                        # rare: p%3 depends on pattern/m mod3; resample
                        continue
                    return p, rs, pat, m
            if verbose and (time.time()-t0)>60:
                print('elapsed', round(time.time()-t0), 's no hit yet (pat', pat, ')', flush=True); break
    return None

if __name__ == '__main__':
    import sys
    res = build(timeout_s=int(sys.argv[1]) if len(sys.argv)>1 else 600)
    if res:
        p, rs, pat, m = res
        print('FOUND p=', p); print('rs=', rs); print('pat', pat, 'm', m)
        json.dump({'p':str(p),'rs':[str(r) for r in rs],'pat':list(pat),'m':str(m)}, open('carm_p.json','w'))
    else:
        print('no hit')
