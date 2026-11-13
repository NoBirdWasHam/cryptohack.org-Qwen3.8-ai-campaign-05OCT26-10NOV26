import random, subprocess, os
from Crypto.Util.number import bytes_to_long, long_to_bytes
os.chdir(os.path.dirname(os.path.abspath(__file__)))
n, q = 512, 127
def cm(a, b):
    o = [0]*n
    nz = [(j, bj) for j, bj in enumerate(b) if bj]
    for i, ai in enumerate(a):
        if ai:
            for j, bj in nz: o[(i+j) % n] += ai*bj
    return o
rng = random.Random(12345)
def rp(d):
    v = [0]*n
    for i in rng.sample(range(n), d): v[i] = 1
    return v
f, g, r = rp(35), rp(35), rp(22)
open("pt_f.txt","w").write("[" + ",".join(map(str,f)) + "]")
open("pt_g.txt","w").write("[" + ",".join(map(str,g)) + "]")
open("pt_h.gp","w").write(
 'f=read("pt_f.txt");g=read("pt_g.txt");F=Pol(f,x);G=Pol(g,x);T=x^512-1;'
 'hi=FpXQ_inv(Mod(F,127),Mod(T,127));'
 'h=FpX_rem(lift(hi)*lift(G),T,127);'
 'v=concat(Vec(h),vector(512-length(Vec(h)),i,0));'
 'for(i=1,512,print1(v[i]," "));print("");\n')
r_ = subprocess.run(["gp64","-q","pt_h.gp"], capture_output=True, text=True)
if r_.returncode != 0:
    print("GP FAIL", r_.stderr[:300]); raise SystemExit(1)
h = [int(x) for x in r_.stdout.split()]
assert len(h) == n
flag = b"NNS{parity_test_round_trip_flag_for_decrypt_check!}"
val = bytes_to_long(flag)
m = [(val >> i) & 1 for i in range(n)]
hr = cm(h, r)
ct = [(2*hr[i] + m[i]) % q for i in range(n)]
S = [2*a + b for a, b in zip(cm(g, r), cm(f, m))]
print("max S coeff:", max(S), "(needs <127), min:", min(S))
A = [x % q for x in cm(f, ct)]
print("lift [0,q) == S exactly:", A == S)
def gf2_solve_unit(fbits, B):
    rows = []
    for c in range(n):
        bits = 0
        for i in range(n):
            if fbits[(c-i) % n] & 1: bits |= 1 << i
        rows.append([bits, B[c] & 1])
    piv = {}
    for rw in rows:
        while rw[0]:
            col = (rw[0] & -rw[0]).bit_length() - 1
            if col in piv:
                rw[0] ^= piv[col][0]; rw[1] ^= piv[col][1]
            else:
                piv[col] = rw; break
        if not rw[0] and rw[1]: return None
    x = 0
    for col in range(n-1, -1, -1):
        if col not in piv: continue
        bits, t = piv[col]
        val2 = t
        rest = bits & ~(1 << col)
        while rest:
            c2 = (rest & -rest).bit_length() - 1
            val2 ^= (x >> c2) & 1
            rest &= rest - 1
        if val2: x |= 1 << col
    return x
def try_f(fv, gv):
    if sum(map(abs, fv)) + 2*sum(map(abs, gv)) >= q: return None
    if sum(1 for c in fv if c) % 2 == 0: return None
    Aa = [x % q for x in cm(fv, ct)]
    Bb = [a & 1 for a in Aa]
    x = gf2_solve_unit([abs(c) & 1 for c in fv], Bb)
    return None if x is None else long_to_bytes(x)
for tag, fv, gv in (("f,g", f, g), ("neg", [-c for c in f], [-c for c in g]),
                    ("swap", g, f), ("swapneg", [-c for c in g], [-c for c in f])):
    out = try_f(fv, gv)
    print(tag, "->", "MATCH" if out == flag else ("None" if out is None else "WRONG " + repr(out[:24])))
