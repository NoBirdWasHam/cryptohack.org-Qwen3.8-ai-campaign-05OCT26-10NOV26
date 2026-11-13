def gf2_solve(eqs, d):
    piv = {}
    for mask, rhs in eqs:
        m, r = mask, rhs
        while m:
            j = m.bit_length() - 1
            if j in piv:
                pm, pr = piv[j]
                m ^= pm; r ^= pr
            else:
                piv[j] = (m, r); break
        else:
            if r: return []
    if len(piv) < d: return None
    x = 0
    for j in sorted(piv, reverse=True):
        pm, pr = piv[j]
        v = pr ^ (bin(pm & ~(1<<j) & x).count("1") & 1)
        if v: x |= 1 << j
    return [x]

import random
random.seed(1)
fails = 0
for t in range(200):
    d = 8
    s = random.getrandbits(d)
    eqs = []
    for _ in range(30):
        a = random.getrandbits(d)
        eqs.append((a, bin(a & s).count("1") % 2))
    r = gf2_solve(eqs, d)
    if r is None or len(r) == 0 or r[0] != s:
        fails += 1
        if fails == 1: print("FAIL", t, r, s)
print("gf2_solve fails:", fails, "/200")
