#!/usr/bin/env python3
"""#64 Everything is Still Big — borderline Wiener (d in (N^{1/4}/3, N^{1/4})).

d=getrandbits(512) with (3d)^4>N  =>  d in (2^512/3, 2^512).  This is just ABOVE
the simple Wiener bound (d < N^{1/4}/3), so k/d is a SEMICONVERGENT (intermediate
fraction) of e/N, not a plain convergent.

e*d = k*phi + 1  =>  k/d ~ e/N.  A semiconvergent between convergents
p_{i-1}/q_{i-1} and p_i/q_i has form  (p_{i-1}*s + p_{i-2})/(q_{i-1}*s + q_{i-2}),
s = 1..a_i.  For each i the valid s are those with d in (2^512/3, 2^512) — a small
window only for the i whose q_{i-1} is near 2^512/s.  We test those windows.
"""
import math
from Crypto.Util.number import long_to_bytes

def is_square(x):
    if x < 0: return False
    r = math.isqrt(x); return r*r == x

def read_vals(path):
    v = {}
    for line in open(path):
        if '=' in line:
            a, b = line.split('=', 1); v[a.strip()] = b.strip()
    return int(v['N'],16), int(v['e'],16), int(v['c'],16)

def cf(num, den):
    a_list, conv = [], []
    p0, p1 = 0, 1
    q0, q1 = 1, 0
    while den:
        a = num // den
        a_list.append(a)
        p0, p1 = p1, a*p1 + p0
        q0, q1 = q1, a*q1 + q0
        num, den = den, num - a*den
        conv.append((p1, q1))
    return a_list, conv

N, e, c = read_vals("big2_output.txt")
print("N bits:", N.bit_length(), "| e bits:", e.bit_length(), flush=True)
N_quarter = 1 << 512
d_lo = (N_quarter - 1) // 3
d_hi = N_quarter
print("d range: (%d, %d) bits" % (d_lo.bit_length(), d_hi.bit_length()), flush=True)

a_list, conv = cf(e, N)
print("convergents:", len(conv), flush=True)

def try_phi(k, d):
    if d <= 0 or k <= 0: return None
    num = e*d - 1
    if num % k != 0: return None
    phi = num // k
    s = N - phi + 1
    disc = s*s - 4*N
    if disc < 0 or not is_square(disc): return None
    r = math.isqrt(disc)
    if (s - r) % 2: return None
    p = (s - r)//2; q = (s + r)//2
    if p*q != N: return None
    return phi, p, q

found = None
tested = 0
for i in range(2, len(conv)):
    p_im1, q_im1 = conv[i-1]
    p_im2, q_im2 = conv[i-2]
    a_i = a_list[i-1]
    if q_im1 <= 0: continue
    s_min = max(1, math.ceil((d_lo - q_im2) / q_im1))
    s_max = min(a_i, (d_hi - 1 - q_im2)//q_im1)
    if s_max < s_min: continue
    if s_max - s_min > 1000000:   # window too broad -> q_{i-1} too small, not the answer
        continue
    for s in range(s_min, s_max+1):
        d = q_im1*s + q_im2
        if not (d_lo < d < d_hi): continue
        k = p_im1*s + p_im2
        tested += 1
        res = try_phi(k, d)
        if res:
            phi, p, q = res
            found = (k, d, i, s, a_i, p, q)
            print("FOUND: i=%d s=%d (a_i=%d) k bits %d d bits %d (tested %d)" %
                  (i, s, a_i, k.bit_length(), d.bit_length(), tested), flush=True)
            break
    if found: break

assert found, "no semiconvergent worked (tested %d)" % tested
k, d, i, s, a_i, p, q = found
print("p bits:", p.bit_length(), "q bits:", q.bit_length(), "p*q==N:", p*q==N, flush=True)
print("d in (2^512/3, 2^512):", d_lo < d < d_hi, flush=True)
m = pow(c, d, N)
flag = long_to_bytes(m)
print("FLAG:", flag, flush=True)
open("flag.txt", "wb").write(flag)
