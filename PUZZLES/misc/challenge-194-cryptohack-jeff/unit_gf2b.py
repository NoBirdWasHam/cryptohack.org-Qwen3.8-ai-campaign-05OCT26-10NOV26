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
d = 8
s = random.getrandbits(d)
eqs = []
for _ in range(30):
    a = random.getrandbits(d)
    eqs.append((a, bin(a & s).count("1") % 2))
r = gf2_solve(eqs, d)
print("sol", r, "true", s)
# check sol against all eqs
if r:
    x = r[0]
    bad = sum(1 for a, b in eqs if (bin(a & x).count("1") % 2) != b)
    print("violations of returned sol:", bad)
# dump pivots
piv = {}
for mask, rhs in eqs:
    m, rr = mask, rhs
    while m:
        j = m.bit_length() - 1
        if j in piv:
            pm, pr = piv[j]
            m ^= pm; rr ^= pr
        else:
            piv[j] = (m, rr); break
for j in sorted(piv, reverse=True):
    pm, pr = piv[j]
    print(j, format(pm, "08b"), pr, " check:", (bin(pm & s).count("1") % 2) == pr)
