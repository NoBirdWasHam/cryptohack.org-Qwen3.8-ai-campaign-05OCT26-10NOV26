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
        E2 = ellinit(phi[1]);
        print("E2 a4,a6: ", E2.a4, " ", E2.a6);
        Q = elladd(E, P, P);
        img = phi*Q;
        print("phi(2P) = ", img);
        print("on E2: ", img[2]^2 == img[1]^3 + E2.a4*img[1] + E2.a6);
        print("j(E)=", ellj(E), " j(E2)=", ellj(E2));
        return(1);
      )
    );
  ))));
}
find3();
