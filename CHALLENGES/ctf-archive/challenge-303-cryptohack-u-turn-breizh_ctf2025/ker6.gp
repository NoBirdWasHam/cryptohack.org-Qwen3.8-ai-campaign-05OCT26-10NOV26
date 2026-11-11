default(parisize,"512M");
AR = Mat(read("Arows.gp"));       \\ 48 x 50
h = read("hvec.gp");               \\ 48 x 1
xp = Mat(read("xpvec.gp"));        \\ 48? no 50 x 1 particular solution
xp = Mat(read("xpvec.gp"));       \\ column 50x1
Mq = Mat(vector(98, j, vector(48, i, if(j<=50, AR[i,j], if(j==i+50, -256, 0)))~));
K = matker(Mq);                    \\ 98 x m
Lb = List();
for(i=1,matsize(K)[2],
  my(v = Vec(K[,i]));
  my(d = 1);
  for(j=1,98, d = lcm(d, denom(v[j])));
  for(j=1,98, v[j] = v[j]*d);
  listput(Lb, vecextract(v,"1..50")));
for(i=1,50, listput(Lb, Vec(256*matid(50))[i]));
G = Mat(vector(#Lb, i, Lb[i]~));   \\ 50 x #Lb columns = gens
H = mathnf(G~);                    \\ rows basis
print("rank ", matsize(H)[1]);
B = qflll(H~);
n = matsize(B)[2];
bs = vector(n);
for(i=1,n, bs[i]=B[,i];
  for(j=1,i-1,
    my(c=(B[,i]~*bs[j])/(bs[j]~*bs[j]));
    bs[i]=bs[i]-c*bs[j]));
t = Mat(xp);
forstep(i=n,1,-1,
  my(c=(t~*bs[i])/(bs[i]~*bs[i]));
  t = t - round(c)*B[,i]);
xx = xp - Vec(t);
res = AR*Mat(xx) - h;
ok2 = 1; for(i=1,48, if(res[i]%256 != 0, ok2=0));
print("congruence ok: ", ok2, "  maxabs: ", vecmax(vecabs(xx)));
printf("X=%s\n", Str("[", Str(join(Vec(xx),",")), "]"));
