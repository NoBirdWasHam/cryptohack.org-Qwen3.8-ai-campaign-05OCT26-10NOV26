p = 11;
f = ffinit(p, 2, 'x);
print("f = ", f);
w = ffgen(f, 'w);
a1 = polcoeff(f, 1); a0 = polcoeff(f, 0);
D = (a1*a1 - 4*a0) % p;
b2 = sqrtMod((-4 * Mod(1,p)) / Mod(D, p), p);
print("i_gp candidate check: ", lift(b2)^2 % p, " should be related");
\\ i = alpha + beta*w with beta^2*D = -4: (alpha+beta w)^2 = -1
beta = b2;
alpha = a1*beta/2;
i2 = (alpha + beta*w)^2;
print("i^2 = ", lift(i2), " (want -1 = ", p-1, ")");
\\ find order-3 point and isogeny over this Fq
E = ellinit([Mod(1,p)*w^0, Mod(0,p)*w]);
print("E ok");
find3() = {
  for(a=0,10, for(b=0,10, for(c=0,10, for(d=0,10,
    X = Mod(c,p)*w + Mod(d,p);
    Y = Mod(a,p)*w + Mod(b,p);
    P = [X, Y];
    if(ellisintegral(E, P) == 1,
      if(ellorder(E, P)==3,
        print("P order3 found");
        phi = ellisogeny(E, P);
        print("codomain a4,a6: ", phi.e.a4, " ", phi.e.a6);
        Q = elladd(E, P, P);
        print("phi(2P): ", phi*Q);
        return(1);
      )
    );
  ))));
}
find3();
