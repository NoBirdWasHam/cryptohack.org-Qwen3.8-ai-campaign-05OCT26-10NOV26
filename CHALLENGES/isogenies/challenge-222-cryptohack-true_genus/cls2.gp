default(parisize,"4G");
p = 38883164557681836128780386500217425544824614969;
q = 14356745447089083514493;
print("q prime? ", isprime(q));
K = bnfinit(x^2 + p, 1);
writeb("bnf.dat", K);
h = K.no;
ls = List();
forprime(l=3,112, listput(ls,l));
listput(ls,139);
g = List();
for(i=1,matsize(ls)[1],
  l = ls[i];
  P = idealprimedec(K, l)[1];
  z = bnfisprincipal(K, P, 0);
  c = z[1][1] % h;
  listput(g, c);
  print(l, " ", c);
);
d = h;
for(i=1,matsize(g)[1], d = gcd(d, g[i]));
print("gcd(all classes, h) = ", d);
print("|G| = h/d = ", h/d);
\ also orders of individual classes
for(i=1,matsize(g)[1], print(ls[i], " order=", h/gcd(h,g[i])));
