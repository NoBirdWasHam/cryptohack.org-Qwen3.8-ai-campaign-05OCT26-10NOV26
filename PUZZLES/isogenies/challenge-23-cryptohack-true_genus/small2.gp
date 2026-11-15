default(parisize,"512M");
read("orbit.gp");
p = 2309; ls = [3,5,7,11]; d = 2;
K = bnfinit(x^2 + p, 1);
h = K.no;
print("h(-4p)=", h, " cyc=", K.cyc);
cs=[];
for(i=1,#ls, my(P = idealprimedec(K, ls[i])[1]); my(z = bnfisprincipal(K, P, 0)); my(c = if(type(z[1])=="t_INT", z[1], z[1][1]) % h); cs=concat(cs,[c]); print("CLS ", ls[i], " ", c, " order=", h/gcd(h,c)));
[m,order] = orbitBFS(p, Mod(0,p), Mod(1,p), ls, d, 3000);
\\\\ compute class exponent for each orbit node from its word
f = fopen("orbit_small.txt","w");
for(k=1,#order,
  my(jj=order[k]);
  my(w=getword(m,jj));
  my(x=0);
  for(t=1,#w, my(l=w[t][1]); my(s=w[t][2]); for(i=1,#ls, if(ls[i]==l, x = x + s*cs[i])));
  my(v); mapisdefined(m,jj,&v);
  fprintf(f, "%d %d %d\n", x % h, v[1], v[2]);
);
fclose(f);
print("WROTE ", #order);
