default(parisize,"512M");
AR = Mat(read("Arows.gp"));
Mq = Mat(vector(48, i, Vecrev(vector(98, j, if(j<=50, AR[i,99-j], if(j==i+1, -256, 0)))~))~;
h = read("hvec.gp");
S = matsnf(Mq, 3);                         \\ [D,U,V]
D = S[1]; U = S[2]; V = S[3];
uh = U*h;
z = vector(98);
for(i=1,48,
  if(uh[i] % D[i,i] != 0, print("divfail ",i); return());
  z[i] = uh[i] \ D[i,i]);
w0 = V*z;
xp = vecextract(Vec(w0),"1..50");
chk = AR*Mat(xp) - h; ok=1; for(i=1,48, if(chk[i]%256!=0, ok=0));
print("xp ok:", ok);
printf("XP=%s\n", Str("[", Str(join(xp,",")), "]"));
\\ ---- lattice of x-parts ----
K = matker(Mq);
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
t = Mat(xp);
forstep(i=n,1,-1,
  my(c=(t~*bs[i])/(bs[i]~*bs[i]));
  t = t - round(c)*B[,i]);
xx = xp - Vec(t);
res = AR*Mat(xx) - h;
ok2 = 1; for(i=1,48, if(res[i]%256 != 0, ok2=0));
print("congruence ok: ", ok2, "  maxabs: ", vecmax(vecabs(xx)));
printf("X=%s\n", Str("[", Str(join(Vec(xx),",")), "]"));
