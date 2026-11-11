#!/usr/bin/env python3
# Generate gpsidh.gp: full SIDH key exchange in PARI/GP over F_{p^2} (ffgen basis),
# then convert j back to the i-basis (i^2=-1) for the sage-format shared secret.
import re
src = open("source.sage").read()
def pts(name):
    m = re.search(name + r" = E0\((\d+)\*i \+ (\d+), (\d+)\*i \+ (\d+)\)", src)
    g = [int(m.group(i)) for i in (1,2,3,4)]
    # x = g1*i + g2, y = g3*i + g4
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
\\ sanity: points on E0
RA = elladd(E0, P2, ellmul(E0, Q2, sA));
RB = elladd(E0, P3, ellmul(E0, Q3, sB));
\\ Alice chain: 2-isogenies with kernel <RA>, track P3,Q3
E = E0; R = RA; p3 = P3; q3 = Q3;
for(i=1, ea,
  Q = ellmul(E, R, 2^(ea-i));
  iso = ellisogeny(E, Q); Fc = iso[1]; phi = iso[2];
  R = ellisogenyapply(phi, R);
  p3 = ellisogenyapply(phi, p3);
  q3 = ellisogenyapply(phi, q3);
  E = ellinit(Fc)
);
EA = E; P3A = p3; Q3A = q3;
print("Alice chain done, j(EA) = ", ellj(EA));
\\ Bob chain: 3-isogenies with kernel <RB>, track P2,Q2
E = E0; R = RB; p2 = P2; q2 = Q2;
for(i=1, eb,
  Q = ellmul(E, R, 3^(eb-i));
  iso = ellisogeny(E, Q); Fc = iso[1]; phi = iso[2];
  R = ellisogenyapply(phi, R);
  p2 = ellisogenyapply(phi, p2);
  q2 = ellisogenyapply(phi, q2);
  E = ellinit(Fc)
);
EB = E; P2B = p2; Q2B = q2;
print("Bob chain done, j(EB) = ", ellj(EB));
\\ shared E_AB: from EB, kernel <P2B + sA*Q2B>, 2-chain
E = EB; R = elladd(EB, P2B, ellmul(EB, Q2B, sA));
for(i=1, ea,
  Q = ellmul(E, R, 2^(ea-i));
  iso = ellisogeny(E, Q); Fc = iso[1]; phi = iso[2];
  R = ellisogenyapply(phi, R);
  E = ellinit(Fc)
);
jAB = ellj(E);
print("j(EAB) raw w-basis: ", jAB);
\\ shared E_BA: from EA, kernel <P3A + sB*Q3A>, 3-chain
E = EA; R = elladd(EA, P3A, ellmul(EA, Q3A, sB));
for(i=1, eb,
  Q = ellmul(E, R, 3^(eb-i));
  iso = ellisogeny(E, Q); Fc = iso[1]; phi = iso[2];
  R = ellisogenyapply(phi, R);
  E = ellinit(Fc)
);
jBA = ellj(E);
print("j(EBA) raw w-basis: ", jBA);
if(jAB != jBA, print("MISMATCH"));
\\ convert j from w-basis to i-basis: j = u + v*w ; w = (i_gp - alpha)/beta
uj = lift(jAB);
u = polcoeff(uj, 0) % p;
v = polcoeff(uj, 1) % p;
jreal = (u - v * alpha % p * lift(Mod(beta, p)^(p-2))) % p;
jimag = v * lift(Mod(beta, p)^(p-2)) % p;
print("JREAL ", jreal);
print("JIMAG ", jimag);
"""
open("gpsidh.gp", "w").write(gp)
print("gpsidh.gp written,", len(gp), "bytes")
