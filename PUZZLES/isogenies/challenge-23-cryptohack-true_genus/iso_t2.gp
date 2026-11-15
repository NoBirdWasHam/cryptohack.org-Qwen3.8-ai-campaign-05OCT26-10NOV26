p = 2309;
E = ellinit([Mod(0,p), Mod(1,p)]);
print("order: ", ellcard(E));
P = [Mod(2,p), Mod(3,p)];
print("on E? ", ellisoncurve(E, P));
Q = ellmul(E, P, (p+1)\3);
print("Q=", Q, " order3? ", elliszero(E, ellmul(E,Q,3)));
xQ = Q[1];
H = Pol([Mod(-xQ,p), Mod(1,p)], 'x);
print("H=", H);
E2 = ellisogeny(E, H);
print("E2: ", E2[5], " ", E2[6]);
print("E2 order: ", ellcard(E2));
\ and the map on a point
R = ellmul(E, P, 7);
phi = ellisomap(E, H);
Rp = phi(R);
print("R=", R, " -> ", Rp, " on E2? ", ellisoncurve(E2, Rp));
