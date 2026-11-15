default(parisize,"4G");
K = read("bnf.dat");
h = K.no;
q = 14356745447089083514493;
ls = concat(Vecsmall(primes([3,112])), [139]);
for(i=1, #ls,
  my(l = ls[i]);
  my(P = idealprimedec(K, l)[1]);
  my(z = bnfisprincipal(K, P, 0));
  my(c);
  if(type(z)=="t_VEC" && type(z[1])=="t_INT", c = z[1], c = z[1][1]);
  c = c % h;
  print("CLS ", l, " ", c, " mod36=", c%36, " modq=", c%q, " order=", h/gcd(h,c));
);
my(d = h);
for(i=1, #ls, my(P = idealprimedec(K, ls[i])[1]); my(z = bnfisprincipal(K, P, 0)); my(c); if(type(z)=="t_VEC" && type(z[1])=="t_INT", c = z[1], c = z[1][1]); d = gcd(d, c));
print("gcdall=", d);
print("|G|=", h/d);
print("DONE");
