default(parisize,"512M");
A = Mat(read("Arows.gp"));
h = read("hvec.gp");
xp = Mat(read("xpvec.gp"));
Mq = Mat(concat(A~, -256*matid(48))~);  \\ 48 x 98 : [A | -256I] rows
K = matker(Mq);                            \\ 98 x 50 columns kernel
Lb = List();
for(i=1,50, listput(Lb, vecextract(Vec(K[,i]),"1..50")));
for(i=1,50, listput(Lb, Vec(256*matid(50))[i]));
H = mathnf(Mat(Lb));
print("rank ", matsize(H)[1]);
B = qflll(H~);
n = matsize(B)[2];
bs = vector(n);
for(i=1,n, bs[i]=B[,i];
  for(j=1,i-1,
    my(c=(B[,i]~*bs[j])/(bs[j]~*bs[j]));
    bs[i]=bs[i]-c*bs[j]));
t = xp;                                    \\ target: closest lattice point v to xp
forstep(i=n,1,-1,
  my(c=(t~*bs[i])/(bs[i]~*bs[i]));
  t = t - round(c)*B[,i]);
xx = Vec(xp) - Vec(t);                     \\ x = xp - v  (v = xp - t_final)
res = A*Mat(xx) - h;
ok = 1; for(i=1,48, if(res[i]%256 != 0, ok=0));
print("congruence ok: ", ok, "  maxabs: ", vecmax(vecabs(xx)));
printf("%s\n", Str("[", Str(join(Vec(xx), ",")), "]"));
