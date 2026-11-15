# solve3.py — finish from dumped resultants r0..r11.txt (coeffs ascending).
# pari gcd of 6 resultants -> squarefree g(u); roots of g mod primes ->
# CRT-intersect in python -> u0 candidates -> p0+/-u0 | n ? -> decrypt GM bits.
import os, sys, subprocess
sys.set_int_max_str_digits(10**7)
import gmpy2
HERE = os.path.dirname(os.path.abspath(__file__))

import re
txt = open(os.path.join(HERE, 'output.txt')).read()
hint = int(re.search(r'hint = (\d+)', txt).group(1))
D = int(re.search(r'D = (\d+)', txt).group(1))
n = int(re.search(r'n = (\d+)', txt).group(1))
c = eval(re.search(r'c = (\[.*\])', txt, re.S).group(1))
S_lo = (hint*hint - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
S_hi = ((hint+1)**2 + 1 - int(gmpy2.isqrt(gmpy2.mpz(4)*D**4*n))) // D**2
t0 = (S_lo + S_hi)//2
d0 = int(gmpy2.isqrt(gmpy2.mpz(t0)*t0 - 4*n))
p0 = (t0 + d0)//2
X = 1 << ((S_hi-S_lo+2).bit_length() + max(0, t0.bit_length()-d0.bit_length()+1) + 4)

GP = r"~\tools\gp64.exe"
k = 6
scr = ['default(parisize,"2G");']
for i in range(k):
    f = os.path.join(HERE, f"r{i}.txt").replace("\\", "/")
    scr.append(f'P{i}=Pol(Vec(readvec("{f}")));')
scr.append('g=P0;')
for i in range(1, k):
    scr.append(f'g=gcd(g,P{i});')
scr.append('g=g/content(g);')
scr.append('print1("GCDDEG ",poldegree(g),"\\n");')
scr.append('forprime(p=5,2000, my(rs=polrootsmod(g,p)); print1("R ",p); for(i=1,#rs,print1(" ",lift(rs[i]))); print1("\\n"); );')
scr.append('quit();')
p = subprocess.run([GP, "-q"], input="\n".join(scr), capture_output=True, text=True, timeout=1800)
lines = p.stdout.splitlines()
if p.stderr.strip(): print("gp stderr:", p.stderr[:300])
deg = int(lines[0].split()[1]); print("gcd deg:", deg, flush=True)
rootmap = {}
for L in lines[1:]:
    parts = L.split()
    if parts and parts[0] == 'R':
        rootmap[int(parts[1])] = set(int(x) for x in parts[2:])

cands = None; M = 1
for pr in sorted(rootmap):
    rp = rootmap[pr]
    if cands is None:
        cands = set(rp); M = pr
    else:
        new = set()
        for a in cands:
            ra = a % pr
            if ra in rp:
                t = ((ra - a) * int(gmpy2.invert(M, pr))) % pr
                new.add(a + M*t)
        cands = new; M *= pr
    if not cands:
        print("no common root -> DEAD"); sys.exit(1)
    if M.bit_length() > 600: break
print("cands after CRT:", len(cands), "M bits:", M.bit_length(), flush=True)
found = None
for a in cands:
    for u0 in {a % M, a % M - M}:
        for pp in (p0 + u0, p0 - u0):
            if pp > 1 and n % pp == 0:
                found = pp
if not found:
    print("FAILED: no divisor among candidates"); sys.exit(1)
p_ = found; q_ = n // p_
print("FACTORED", p_.bit_length(), q_.bit_length(), p_*q_ == n, flush=True)
bits = [1 if pow(ci, (p_-1)//2, p_) == 1 else 0 for ci in c]
val = int(''.join(map(str, bits)), 2)
flag = val.to_bytes((val.bit_length()+7)//8, 'big')
print("FLAG:", flag)
open(os.path.join(HERE, 'flag_1337crypt-downunderctf2020.txt'), 'wb').write(flag)
