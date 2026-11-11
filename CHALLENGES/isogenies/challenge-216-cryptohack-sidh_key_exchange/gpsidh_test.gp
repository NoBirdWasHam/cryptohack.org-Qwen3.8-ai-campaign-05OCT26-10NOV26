p = 11;
f = ffinit(p, 2, 'x);
w = ffgen(f, 'w);
a1 = lift(polcoeff(f, 1)) % p;
a0 = lift(polcoeff(f, 0)) % p;
D = (a1*a1 - 4*a0) % p;
beta = lift(sqrt(Mod(-4, p) / Mod(D, p)));
alpha = (a1 * beta / 2) % p;
i_gp = Mod(alpha, p) + Mod(beta, p)*w;
print("i^2 check (want p-1=", p-1, "): ", lift(i_gp^2));
E = ellinit([Mod(1,p) + 0*w, Mod(0,p) + 0*w]);
find3() = {
  for(a=0,10, for(b=0,10, for(c=0,10, for(d=0,10,
    X = Mod(c,p)*w + Mod(d,p);
    Y = Mod(a,p)*w + Mod(b,p);
    P = [X, Y];
    if(Y^2 == X^3 + X,
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
