default(parisize,"4G");
K = read("bnf.dat");
h = K.no;
ls = concat(Vecsmall(primes([3,112])), [139]);
g = [];
for(i=1,#ls,
  l = ls[i];
  P = idealprimedec(K, l)[1];
  z = bnfisprincipal(K, P, 0);
  c = z[1][1] % h;
  g = concat(g, [c]);
  print("CLS ", l, " ", c, " order=", h/gcd(h,c));
);
d = h;
for(i=1,#g, d = gcd(d, g[i]));
print("gcdall=", d);
print("|G|=", h/d);
print("DONE");
