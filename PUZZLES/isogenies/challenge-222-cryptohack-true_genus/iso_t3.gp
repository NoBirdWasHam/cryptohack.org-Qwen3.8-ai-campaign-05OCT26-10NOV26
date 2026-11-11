p = 2309;
E = ellinit([Mod(0,p), Mod(1,p)]);
P = [Mod(2,p), Mod(3,p)];
Q = ellmul(E, P, (p+1)\3);
print("Q=", Q, " 3Q=", ellmul(E,Q,3));
xQ = Q[1];
H = Pol([Mod(-xQ,p), Mod(1,p)], 'x);
E2 = ellisogeny(E, H);
print("E2: a4=", E2[5], " a6=", E2[6], " order=", ellcard(E2));
phi = ellisomap(E, H);
R = ellmul(E, P, 7);
Rp = phi(R);
print("R->", Rp, " on E2? ", ellisoncurve(E2, Rp));
\ check homomorphism: phi(2R) == 2 phi(R)
print("hom ok? ", phi(ellmul(E,R,2)) == ellmul(E2, Rp, 2));
\ j-invariants
print("j(E)=", ellj(E), " j(E2)=", ellj(E2));
