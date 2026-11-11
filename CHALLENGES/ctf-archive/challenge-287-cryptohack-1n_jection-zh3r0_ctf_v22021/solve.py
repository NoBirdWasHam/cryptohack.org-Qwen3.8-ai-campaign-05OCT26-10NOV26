# Invert nk2n: Cantor pairing tree over flag bytes. Try candidate lengths.
from math import isqrt

N = 2597749519984520018193538914972744028780767067373210633843441892910830749749277631182596420937027368405416666234869030284255514216592219508067528406889067888675964979055810441575553504341722797908073355991646423732420612775191216409926513346494355434293682149298585

def unpair(z):
    w = (isqrt(8*z + 1) - 1) // 2
    # guard: ensure w(w+1)/2 <= z < (w+1)(w+2)/2
    assert w*(w+1)//2 <= z
    t = w*(w+1)//2
    j = z - t
    i = w - j
    assert i >= 0 and j >= 0
    return i, j

def rec(val, L):
    if L == 1:
        return [val]
    if L == 2:
        return list(unpair(val))
    l1 = L - L//2
    i, j = unpair(val)
    return rec(i, l1) + rec(j, L - l1)

for L in range(4, 130):
    try:
        bs = rec(N, L)
        if all(0 <= b < 256 for b in bs):
            s = bytes(bs)
            try:
                t = s.decode('ascii')
            except Exception:
                continue
            if all(32 <= ord(c) < 127 for c in t) and '{' in t and '}' in t:
                print("LEN", L)
                print("FLAG", t)
    except Exception:
        pass
