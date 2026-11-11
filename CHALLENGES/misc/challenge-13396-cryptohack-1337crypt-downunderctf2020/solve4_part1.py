1|# solve2.py — finish key recovery from bivariate-Coppersmith resultants FAST.
2|# Same lattice build as solve.py (m=8,D=6 produced 48 HG-passing rows, 12 nonzero
3|# resultants in run1.log). Root extraction replaced: dump R polys -> pari gcd ->
4|# modular root-intersection CRT -> integer root u0 -> p = p0+u0.
5|import re, sys, math, os, subprocess, time
6|sys.set_int_max_str_digits(10**7)
7|import gmpy2
8|from fractions import Fraction
9|import sympy as sp
10|from fpylll import IntegerMatrix
11|from fpylll.fplll.lll import lll_reduction
12|
13|t_start = time.time()
14|HERE = os.path.dirname(os.path.abspath(__file__))
15|txt = open(os.path.join(HERE, 'output.txt')).read()
16|hint = int(re.search(r'hint = (\d+)', txt).group(1))
17|D = int(re.search(r'D = (\d+)', txt).group(1))
18|n = int(re.search(r'n = (\d+)', txt).group(1))
19|c = eval(re.search(r'c = (\[.*\])', txt, re.S).group(1))
20|assert D == 63**14
21|
22|S_lo = (hint*hint - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
23|S_hi = ((hint+1)**2 + 1 - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
24|t0 = (S_lo + S_hi)//2
25|d0 = int(gmpy2.isqrt(gmpy2.mpz(t0)*t0 - 4*n))
26|p0 = (t0 + d0)//2
27|q0 = n // p0
28|c0 = p0*q0 - n
29|dSb = (S_hi-S_lo+2).bit_length()
30|amp = max(0, t0.bit_length()-d0.bit_length()+1)
31|X = 1 << 700
32|Y = X
33|print("p0 bits", p0.bit_length(), "| X = 2^", X.bit_length(), "| c0 bits", abs(c0).bit_length(), flush=True)
34|
35|u, v = sp.symbols('u v')
36|fmon = {(1,1): 1, (1,0): q0, (0,1): p0, (0,0): c0}
37|FP = {}
38|def fpow(k):
39|    if k in FP: return FP[k]
40|    out = {(0,0): 1}
41|    for _ in range(k):
42|        nxt = {}
43|        for ma, va in out.items():
44|            for mb, vb in fmon.items():
45|                m = (ma[0]+mb[0], ma[1]+mb[1]); nxt[m] = nxt.get(m, 0) + va*vb
46|        out = nxt
47|    FP[k] = out
48|    return out
49|
50|def build(m, Dd):
51|    K = Dd
52|    mons = sorted([(a,b) for a in range(K+1) for b in range(K+1)])
53|    idx = {mm:i for i,mm in enumerate(mons)}
54|    w = len(mons)
55|    rows = []
56|    for j in range(m+1):
57|        if j > K: break
58|        Np = n**(m-j)
59|        for i2 in range(K-j+1):
60|            for k2 in range(K-j+1):
61|                row = [0]*w
62|                for (ia, ib), vv in fpow(j).items():
63|                    ma, mb = ia+i2, ib+k2
64|                    if ma <= K and mb <= K:
65|                        row[idx[(ma,mb)]] += vv * Np * X**ma * Y**mb
66|                rows.append(row)
67|    M = IntegerMatrix(len(rows), w)
68|    for i, r in enumerate(rows):
69|        for jj, val in enumerate(r):
70|            if val: M[i, jj] = val
71|    M = lll_reduction(M, delta=0.99)
72|    thr = Fraction(n**m) / (Fraction(math.isqrt(w)+1))
73|    cands = []
74|    for i in range(M.nrows):
75|        nr2 = sum(int(M[i, jj])**2 for jj in range(w))
76|        if Fraction(nr2) >= thr*thr:
77|            continue
78|        h = sp.Rational(0); nz = False
79|        for jj in range(w):
80|            val = int(M[i, jj])
81|            if val:
82|                nz = True
83|                (a, b) = mons[jj]
84|                h += sp.Rational(val, X**(a+b)) * u**a * v**b
85|        if not nz: continue
86|        num = sp.numer(sp.expand(sp.together(h)))
87|        if sp.Poly(num, u, v).total_degree() > 0:
88|            cands.append(num)
89|    return cands
90|
91|def resultants(cands):
92|    vf = -(q0*u + c0)/(u + p0)
93|    Rs = []
94|    for h in cands:
95|        hp = sp.Poly(sp.expand(h), u, v)
96|        dv = hp.degree(v)
97|        R = sp.numer(sp.together(sp.expand(hp.as_expr().subs(v, vf) * (u+p0)**(dv+2))))
98|        R = sp.Poly(R, u)
99|        if R.degree() >= 1:
100|            Rs.append(R.as_expr())
101|    return Rs
102|
103|def dump_poly(pexpr, fname):
104|    P = sp.Poly(pexpr, u)
105|    with open(fname, 'w') as fh:
106|        for co in P.all_coeffs()[::-1]:   # ascending
107|            fh.write(str(int(co)) + "\n")
108|
109|GP = r"~\tools\gp64.exe"
110|
111|def gp_run(script, timeout=2400):
112|    p = subprocess.run([GP, "-q"], input=script, capture_output=True, text=True, timeout=timeout)
113|    return p.stdout.strip(), p.stderr.strip()
114|
115|def roots_mod_p(poly_expr, p):
116|    """all roots in GF(p) of squarefree part via gcd with x^p-x"""
117|    R = sp.Poly(poly_expr, u, modulus=p)
118|    if R.degree() < 1: return set()
119|    xpx = sp.Poly(u**p - u, u, modulus=p)
120|    g = sp.gcd(R, xpx