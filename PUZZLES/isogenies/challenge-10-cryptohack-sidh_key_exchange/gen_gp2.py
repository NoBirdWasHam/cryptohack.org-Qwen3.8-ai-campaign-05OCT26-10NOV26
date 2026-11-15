#!/usr/bin/env python3
# Generate gpsidh.gp: full SIDH key exchange in PARI/GP over F_{p^2} (ffgen basis),
# convert j back to the i-basis (i^2=-1) for the sage-format shared secret.
import re
src = open("source.sage").read()
def pts(name):
    m = re.search(name + r" = E0\((\d+)\*i \+ (\d+), (\d+)\*i \+ (\d+)\)", src)
    g = [int(m.group(i)) for i in (1,2,3,4)]
    return (g[1], g[0], g[3], g[2])  # xre, xim, yre, yim
P2 = pts("P2"); Q2 = pts("Q2"); P3 = pts("P3"); Q3 = pts("Q3")
sA = 225902606209514408534212339057054
sB = 38410379124791756271891302485727

def conv(re_, im):
    if im == 0:
        return f"Mod({re_}, p) + 0*w"
    return f"Mod({re_}, p) + Mod({im}, p)*i_gp"

gp = r"""
p = 2^110 * 3^67 - 1;
ea = 110; eb = 67;
f2 = ffinit(p, 2, 'x);
w = ffgen(f2, 'w);
a1 = lift(polcoeff(f2, 1)) % p;
a0 = lift(polcoeff(f2, 0)) % p;
D = (a1*a1 - 4*a0) % p;
beta = lift(sqrt(Mod(-4, p) / Mod(D, p)));
alpha = (a1 * beta * ((p+1) \ 2)) % p;
i_gp = Mod(alpha, p) + Mod(beta, p)*w;
if(lift(i_gp^2) != p-1, print("BAD i basis"));
"""
for nm, (xr, xi, yr, yi) in [("P2",P2),("Q2",Q2),("P3",P3),("Q3",Q3)]:
    gp += f"{nm}x = {conv(xr, xi)};\n{nm}y = {conv(yr, yi)};\n"
gp += rf"""
P2 = [P2x, P2y]; Q2 = [Q2x, Q2y]; P3 = [P3x, P3y]; Q3 = [Q3x, Q3y];
sA = {sA}; sB = {sB};
E0 = ellinit([Mod(1,p) + 0*w, Mod(0,p) + 0*w]);
\\ generic isogeny chain: kernel <R> of order ell^e; track images of extras
chain(E, R, ell, e, extras) = {{
  my(n = #extras);
  for(i=1, e,
    if(1,
      Q = ellmul(E, R, ell^(e-i));
      iso = ellisogeny(E, Q);
      R = ellisogenyapply(iso[2], R);
      for(j=1, n, extras[j] = ellisogenyapply(iso[2], extras[j]));
      E = ellinit(iso[1])
    )
  );
  [E, R, extras]
}}
RA = elladd(E0, P2, ellmul(E0, Q2, sA));
RB = elladd(E0, P3, ellmul(E0, Q3, sB));
resA = chain(E0, RA, 2, ea, [P3, Q3]);
EA = resA[1]; P3A = resA[3][1]; Q3A = resA[3][2];
jinv(E) = {{ 6912 * E.a4^3 / (4*E.a4^3 + 27*E.a6^2) }};
print("Alice done");
resB = chain(E0, RB, 3, eb, [P2, Q2]);
EB = resB[1]; P2B = resB[3][1]; Q2B = resB[3][2];
print("Bob done");
RA2 = elladd(EB, P2B, ellmul(EB, Q2B, sA));
resAB = chain(EB, RA2, 2, ea, []);
jAB = jinv(resAB[1]);
print("EAB done");
RB2 = elladd(EA, P3A, ellmul(EA, Q3A, sB));
resBA = chain(EA, RB2, 3, eb, []);
jBA = jinv(resBA[1]);
print("EBA done");
if(jAB != jBA, print("MISMATCH"));
print("JW ", jAB);
print("ALPHA ", alpha);
print("BETA ", beta);
"""
open("gpsidh.gp", "w").write(gp)
print("gpsidh.gp written,", len(gp), "bytes")
