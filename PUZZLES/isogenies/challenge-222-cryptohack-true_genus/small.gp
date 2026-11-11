read("orbit.gp");
p = 2309; ls = [3,5,7,11]; d = 2;
K = bnfinit(x^2 + p, 1);
h = K.no;
print("h(-4p)=", h, " cyc=", K.cyc);
for(i=1,#ls,
  l=ls[i];
  P = idealprimedec(K,l)[1];
  z = bnfisprincipal(K,P,0);
  c = z[1][1] % h;
  print("class of ",l," = ",c," order=",h/gcd(h,c));
);
[m,order] = orbitBFS(p, Mod(0,p), Mod(1,p), ls, d, 3000);
