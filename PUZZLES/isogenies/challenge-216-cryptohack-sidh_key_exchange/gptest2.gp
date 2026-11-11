p = 11;
i = Mod(x, Mod(x^2+1, p));
one = Mod(1, Mod(x^2+1, p));
E = ellinit([one, 0*one]);
print("E ok: ", E.a4, " ", E.a6);
found = 0;
for(a=0,10, for(b=0,10, for(c=0,10, for(d=0,10,
  if(found, return());
  X = Mod(Mod(c*x + d, p), Mod(x^2+1,p));
  Y = Mod(Mod(a*x + b, p), Mod(x^2+1,p));
  if(Y^2 == X^3 + X,
    P = [X, Y];
    if(ellorder(E, P)==3,
      print("P order3: ", P);
      phi = ellisogeny(E, P);
      print("codomain a4,a6: ", phi.e.a4, " ", phi.e.a6);
      Q = elladd(E, P, P);
      print("phi(2P): ", phi*Q);
      found=1;
      return();
    );
  );
)));
