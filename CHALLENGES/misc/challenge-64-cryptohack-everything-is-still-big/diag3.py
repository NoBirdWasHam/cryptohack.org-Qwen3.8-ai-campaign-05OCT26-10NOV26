#!/usr/bin/env python3
"""#64 Everything is Still Big — Boneh-Durfee / Coppersmith small-root.

d = getrandbits(512) with (3d)^4 > N  =>  d in (N^{1/4}/3, N^{1/4}) = (2^512/3, 2^512).
That is just ABOVE the simple Wiener bound, so k/d is not a convergent/semiconvergent of
e/N. Use Coppersmith on  f(X) = (1 + X/M)^j mod N,  M = N^{1/4}, j = 4,  which finds a
small root x < M^{1/2} = 2^256.  Then d = d0 + x where d0 is a convergent denominator of
e/N (the nearest one to the true d).  Search convergent denominators near the d-window.
"""
import math
from gmpy2 import mpz, isqrt, gcd, sqrt
from Crypto.Util.number import long_to_bytes

def read_vals(path):
    v={}
    for line in open(path):
        if '=' in line:
            a,b=line.split('=',1); v[a.strip()]=b.strip()
    return int(v['N'],16), int(v['e'],16), int(v['c'],16)

def cf(num, den):
    a_list, conv = [], []
    p0,p1 = 0,1; q0,q1 = 1,0
    while den:
        a = num//den; a_list.append(a)
        p0,p1 = p1, a*p1+p0; q0,q1 = q1, a*q1+q0
        num, den = den, num - a*den
        conv.append((p1,q1))
    return a_list, conv

def lll2(b1, b2):
    """LLL reduction for a 2x2 integer lattice (lists [a,b]). Returns reduced list."""
    import gmpy2
    b1=[mpz(b1[0]),mpz(b1[1])]; b2=[mpz(b2[0]),mpz(b2[1])]
    def det(x,y): return x[0]*y[1]-x[1]*y[0]
    # ensure |det|>0
    D = det(b1,b2)
    while True:
        # size-reduce b2 with respect to b1
        if b1[0]!=0:
            mu = mpz((b2[0]*2 + b1[0])/(2*b1[0]))  # round(b2[0]/b1[0])
            if mu != 0: b2 = [b2[0]-mu*b1[0], b2[1]-mu*b1[1]]
        # size-reduce b1 with respect to b2 (only if b2 shorter)
        if b2[0]!=0:
            mu = mpz((b1[0]*2 + b2[0])/(2*b2[0]))
            if mu != 0:
                b1 = [b1[0]-mu*b2[0], b1[1]-mu*b2[1]]
        # swap if needed
        if (b2[0]*b2[0]+b2[1]*b2[1]) < (b1[0]*b1[0]+b1[1]*b1[1]):
            b1,b2 = b2,b1
        # stability check
        if b1[0]!=0:
            mu12 = mpz((b2[0]*2 + b1[0])/(2*b1[0]))
        else:
            mu12 = mpz(0)
        # Gram-Schmidt
        if b1[0]==0:
            break
        lam1 = b1[0]*b1[0]+b1[1]*b1[1]
        # b2' = b2 - mu12*b1
        b2x = b2[0]-mu12*b1[0]; b2y = b2[1]-mu12*b1[1]
        lam2 = b2x*b2x + b2y*b2y
        # LLL condition: lam2 >= (1-1/4) lam1
        if lam2*4 >= lam1*3:
            break
        b1,b2 = [b2x,b2y], b1
    return [[int(b1[0]),int(b1[1])], [int(b2[0]),int(b2[1])]]

N, e, c = read_vals("big2_output.txt")
print("N bits:", N.bit_length(), "| e bits:", e.bit_length(), flush=True)
M = 1 << (N.bit_length()//4)   # N^{1/4} = 2^512
j = 4
# f(X) = (1 + X/M)^j mod N = sum binom(j,r) X^r / M^r  (M^j divides N? no). 
# Coppersmith 2x2: polynomial P(X)= (1 + X/N')^j with N'=M. Coefficients c_r = binom(j,r) * M^{-r} mod N
# We clear denominators: P(X)*M^j = (M + X)^j mod N^... use the standard: 
# f(x) = (1 + x/M)^j = sum_{r} C(j,r) x^r M^{-r}. Multiply by M^j: (x+M)^j mod (N * M^j)? 
# Standard 2x2 lattice for root x of f(X) mod N with bound X0:
#   L rows: [X0, N] and [X0^2, 0]  with f scaled.
# We use the classical construction: f(X) = (1+X/M)^j, X0=M^{1/2}.
# Build polynomial g(X) = M^j * f(X) = (M+X)^j  (mod N). Coeffs g_r = binom(j,r) M^{j-r}.
# Lattice basis (2x2): B = [[X0, X0*N], [0, N*X0]] won't work for degree j.
# For j=4 it's a 2x2 only if we reduce. Use the standard Boneh-Durfee 2x2:
#   u = (x+M)^j  -> keep only terms, lattice with rows [X0, X0^j*N] and [X0^2, 0]? 
# Simpler robust path: use the "find x with (M+x)^j ≡ 0 mod N" via the 2x2 trick:
#   h(X) = (1 + X/M)^j ;  lattice vectors v1=(X0, 0), v2=(0, N) in 2D won't encode degree.
# => Use the well-known 2x2 for j: rows [X0, X0*N] , [X0^2, N*X0] is only degree-1.
#
# Correct standard (Boneh-Durfee) 2x2:
#   Let f(X) = (1 + X/N')^j, N' = N^{1/4}.  We seek x < X0 = N'^{1/2}.
#   Lattice basis (2 rows): 
#       b1 = (X0, N' * X0)   ->  corresponds to  X0 * (1 + X/N')
#       b2 = (X0^2, 0)        ... not right.
#
# I'll instead use the DIRECT approach: enumerate candidate x via the convergent structure is
# overkill. Use a clean Coppersmith with a 2x2 lattice for the polynomial (1+X/M)^j by
# taking the first two coefficients only is invalid.
#
# FINAL: use the proven 2x2 Boneh-Durfee matrix:
#   B = [[ M^{j-1} * X0 ,  N * X0 ],
#        [ X0^2        ,  0      ]]  ... 
# This is getting error-prone. I'll just try the convergent-denominator + small-x brute:
# find d0 = convergent denominator nearest the window, then brute x in a small band.
print("M (N^1/4) bits:", M.bit_length(), flush=True)
a_list, conv = cf(e, N)
d_lo = M//3; d_hi = M
print("d window: (%d,%d) bits" % (d_lo.bit_length(), d_hi.bit_length()), flush=True)
# list convergent denominators with bitlen in 500..515
near = []
for idx,(pp,qq) in enumerate(conv):
    if 499 <= qq.bit_length() <= 515:
        near.append((idx, qq))
print("convergent denominators 499..515 bits:", len(near))
for idx,qq in near:
    # x = d - qq, d in (d_lo,d_hi)
    xlo = d_lo - qq; xhi = d_hi - qq
    if xhi < xlo: continue
    # we need x small to brute; check range size
    size = xhi - xlo
    print("  idx=%4d d0 bits=%d  x range width=%d bits=%d" % (idx, qq.bit_length(), size, size.bit_length()), flush=True)
