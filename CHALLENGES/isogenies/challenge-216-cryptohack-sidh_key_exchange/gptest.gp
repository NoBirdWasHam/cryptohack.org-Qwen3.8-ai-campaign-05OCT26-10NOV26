\ small test: E: y2=x3+x over F_121 = F_11[i], i2=-1
p = 11;
K = Mod(x^2+1, x^2+1)*0 + Mod(1, p);  \ dummy
\ use polmods mod p
i = Mod(x, Mod(x^2+1, p));
one = Mod(1, Mod(x^2+1, p));
E = ellinit([one, 0*one]);
print("E ok: ", E.a4, " ", E.a6);
\ find point of order 3: brute
found = 0;
for(a=0,10, for(b=0,10, for(c=0,10, for(d=0,10,
  if(found, return());
  X = Mod(Mod(c*x + d, p), Mod(x^2+1,p));
  Y = Mod(Mod(a*x + b, p), Mod(x^2+1,p));
  if(ellordinate(E, lift(X))==[], return());
  P = [X, Y];
  if(ellorder(E, P)==3, print("P order3: ", P); found=1;
    phi = ellisogeny(E, P);
    print("codomain a4,a6: ", phi.e.a4, " ", phi.e.a6);
    Q = elladd(E, P, P);
    print("phi(2P): ", phi*Q);
    return();
  );
)));
