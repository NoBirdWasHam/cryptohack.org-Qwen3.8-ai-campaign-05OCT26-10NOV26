print("PARI version: ", version);
p = 2309;
ls = [3,5,7,11];
\ base curve y^2 = x^3 + 1 over Fp
E = ellinit([Mod(0,p), Mod(1,p)]);
print("E order: ", ellcard(E));
\ find a point of order 3: E(Fp) has order p+1=2310=2*3*5*7*11
P = ellgenerators(E);
print("gens: ", P);
Q = ellmul(E, P[1], (p+1)\3);
print("3Q=O? ", elliszero(E, ellmul(E,Q,3)));
\ kernel polynomial for <Q> of order 3: (x - xQ)
xQ = Q[1];
H = [Mod(-xQ,p), Mod(1,p)];  \ x - xQ
E2 = ellisogeny(E, H);
print("E2 coeffs: ", E2);
print("E2 order: ", ellcard(E2));
