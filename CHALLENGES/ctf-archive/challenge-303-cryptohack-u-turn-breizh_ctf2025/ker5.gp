default(parisize,"512M");
AR = Mat(read("Arows.gp"));       \\ 48 x 50
h = read("hvec.gp");               \\ 48 x 1
Mq = Mat(vector(98, j, vector(48, i, if(j<=50, AR[i,j], if(j==i+50, -256, 0)))~));
print("Mq ", matsize(Mq));
S = matsnf(Mq, 3);                 \\ [D,U,V]
D = S[1]; U = S[3]; V = S[2];
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
K = matker(Mq);                    \\ 98 x m columns
Lb = List();
for(i=1,matsize(K)[2], listput(Lb, Vec(K[,i])));
for(i=1,50, listput(Lb, Vec(256*matid(50))[i]));
G = Mat(vector(#Lb, i, Lb[i]~));   \\ 50 x #Lb (columns = gens)
H = mathnf(G~);                    \\ row-basis of x-part lattice
print("rank ", matsize(H)[1]);
B = qflll(H~);                     \\ LLL-reduced columns
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
