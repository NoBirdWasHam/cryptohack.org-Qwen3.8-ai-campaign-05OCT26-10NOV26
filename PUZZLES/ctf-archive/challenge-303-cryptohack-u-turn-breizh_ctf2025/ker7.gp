default(parisize,"512M");
AR = Mat(read("Arows.gp"));       \\ 48 x 50
h = read("hvec.gp");
xp = Mat(read("xpvec.gp"));       \\ 50 x 1
\\ T = rowspace lattice of [A ; 256 I] (96 x 50)
T = Mat(vector(50, j, vector(98, i, if(i<=48, AR[i,j], if(j==i-48, 256, 0)))~));
print("T ", matsize(T));
H = mathnf(T);
print("H ", matsize(H));
Hsq = Mat(Vec(vector(matsize(H)[1], i, H[i,])));
\\ keep nonzero rows only
nz = List();
for(i=1,matsize(H)[1], if(H[i,]*H[i,]~ != 0, listput(nz, H[i,])));
Hsq = Mat(vector(#nz, i, nz[i]~))~;
print("Hsq ", matsize(Hsq));
if(matsize(Hsq)[1] != 50, print("rank != 50"); return());
\\ L = {x : x*H^T in 256 Z} = rowspace(256 * H^{-1})
Lb = 256*matinv(Hsq);
print("det check: det(Lb)*det(Hsq) = ", round(matdet(Lb)*matdet(Hsq)));
B = qflll(Lb~);                  \\ reduced columns
n = matsize(B)[2];
bs = vector(n);
for(i=1,n, bs[i]=B[,i];
  for(j=1,i-1,
    my(c=(B[,i]~*bs[j])/(bs[j]~*bs[j]));
    bs[i]=bs[i]-c*bs[j]));
t = xp;
forstep(i=n,1,-1,
  my(c=(t~*bs[i])/(bs[i]~*bs[i]));
  t = t - round(c)*B[,i]);
xx = Vec(t);                     \\ x = xp - v (small)
res = AR*Mat(xx) - h;
ok2 = 1; for(i=1,48, if(res[i]%256 != 0, ok2=0));
print("congruence ok: ", ok2, "  maxabs: ", vecmax(vecsmall(abs.(xx))));
printf("X=%s\n", Str("[", Str(join(xx,",")), "]"));
