p = 11;
f = ffinit(p, 2, 'x);
w = ffgen(f, 'w);
E = ellinit([Mod(1,p) + 0*w, Mod(0,p) + 0*w]);
find3() = {
  for(a=0,10, for(b=0,10, for(c=0,10, for(d=0,10,
    X = Mod(c,p)*w + Mod(d,p);
    Y = Mod(a,p)*w + Mod(b,p);
    P = [X, Y];
    if(Y^2 == X^3 + X,
      if(ellorder(E, P)==3,
        phi = ellisogeny(E, P);
        print("type: ", type(phi), " len: ", #phi);
        for(i=1, #phi, print(i, ": ", type(phi[i]), " = ", phi[i]));
        return(1);
      )
    );
  ))));
}
find3();
