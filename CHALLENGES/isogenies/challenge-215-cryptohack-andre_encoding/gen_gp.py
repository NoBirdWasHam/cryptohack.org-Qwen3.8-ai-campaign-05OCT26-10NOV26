"""Generate GP script for andre_encoding Weil-pairing byte recovery."""
import json, math

L = 1
for i in range(1, 256):
    L = math.lcm(L, i)
p = 37 * 2**64 * L - 1
m = p + 1

def is_prime(n):
    return all(n % q for q in range(2, int(n**0.5)+1))
primes = sorted(set([d for d in range(2, 256) if is_prime(d)]))

def v_l(nn, l):
    e = 0
    while nn % l == 0:
        nn //= l; e += 1
    return e

ee = [v_l(m, l) for l in primes]
kmax = []
for l in primes:
    k = 0
    while l ** (k + 1) <= 255 and (k + 1) <= ee[primes.index(l)]:
        k += 1
    kmax.append(k)

ct = json.load(open("output.txt"))
rows = []
for e in ct:
    rows.append([e["P"]["x"][0], e["P"]["x"][1], e["P"]["y"][0], e["P"]["y"][1],
                 e["Q"]["x"][0], e["Q"]["x"][1], e["Q"]["y"][0], e["Q"]["y"][1]])

with open("bytes.gp", "w") as f:
    f.write("[" + ",".join("[" + ",".join(str(x) for x in r) + "]" for r in rows) + "]")

with open("params.gp", "w") as f:
    f.write(f"PVAL = {p};\nLVAL = {L};\nPR = {primes};\nEE = {ee};\nKM = {kmax};\n")

gp = r'''
default(parisize, "6g");
read("params.gp");
F = ffinit(PVAL, 2);
W = ffgen(F, 'W);
o1 = W^0; z0 = W*0;
ffsqrt_ts(r) = {
  local(q, e, mm, z, c, x, t, i, b);
  if(r == 0, return(z0));
  q = PVAL^2;
  if(r^((q-1)>>1) != o1, return(-1));
  e = valuation(q-1, 2); mm = (q-1) >> e;
  z = W; while(z^((q-1)>>1) == o1, z = z+1);
  c = z^mm; x = r^((mm+1)>>1); t = r^mm;
  while(t != o1, i = 0; b = t; while(b != o1, b = b^2; i = i+1); b = c^(2^(e-i-1)); c = b^2; x = x*b; t = t*c);
  return(x);
}
mk(re, im) = { re + im*I2 };
DATA = read("bytes.gp");
MVAL = PVAL + 1;
I2 = ffsqrt_ts(-1 + z0);
print("i^2+1 == 0: ", I2^2 + o1 == z0);
FLAG = "";
for(idx = 1, #DATA, d = DATA[idx]; Ax = mk(d[1], d[2]); Ay = mk(d[3], d[4]); Bx = mk(d[5], d[6]); By = mk(d[7], d[8]); RA = Ay^2 - Ax^3; RB = By^2 - Bx^3; a4 = (RA - RB)/(Ax - Bx); a6 = RA - a4*Ax; E = ellinit([0,0,0,a4,a6]); A = [Ax, Ay]; B = [Bx, By]; if(!ellisoncurve(E, A) || !ellisoncurve(E, B), print(idx, " ONCURVE FAIL")); b = 1; for(j = 1, #PR, l = PR[j]; e = EE[j]; Ae = ellmul(E, A, MVAL/l^e); Be = ellmul(E, B, MVAL/l^e); zpl = ellweilpairing(E, Ae, Be, l^e); vv = 0; for(k = 0, e, if(zpl^l^k == o1, vv = k; break)); vl = e - vv; if(l == 2, vl = 7 - vv); if(vl > 0, b = b * l^vl)); FLAG = FLAG || Strchr(b); print(idx, " b=", b, " ", Strchr(b)));
print("FLAG: ", FLAG);
'''
with open("solve.gp", "w") as f:
    f.write(gp)
print("wrote solve.gp, bytes.gp, params.gp; primes:", len(primes))
