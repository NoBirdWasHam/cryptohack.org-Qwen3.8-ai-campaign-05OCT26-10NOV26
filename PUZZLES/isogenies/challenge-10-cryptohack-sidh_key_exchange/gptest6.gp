p = 11;
f = ffinit(p, 2, 'x);
print("f = ", f);
w = ffgen(f, 'w);
a1 = lift(polcoeff(f, 1)) % p; a0 = lift(polcoeff(f, 0)) % p;
D = (a1*a1 - 4*a0) % p;
beta = sqrt(Mod(-4 * lift(Mod(1, p)) / lift(Mod(1,p)) * Mod(1,p) - 0 + (-4) * 0 + (-4), p)); \\ placeholder
beta = sqrt(Mod((-4 * Mod(1,p)) * lift(Mod(lift(Mod(1,p)), p)) , p));
print("unused");
