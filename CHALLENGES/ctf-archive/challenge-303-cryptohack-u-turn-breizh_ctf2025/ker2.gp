default(parisize,"512M");
A = Mat(read("Arows.gp"));      \\ 48 x 50
h = read("hvec.gp");             \\ 48x1
K = matkerMod(A, 256);           \\ columns = Z-gens of {x: Ax=0 mod256}
print("ker gens ", matsize(K)[2]);
Lb = List();
for(i=1,matsize(K)[2], listput(Lb, Vec(Mat(K)[,i])));
for(i=1,50, listput(Lb, Vec(256*mathide(50))[i]));
H = mathnf(Mat(Lb));             \\ row-basis of full preimage lattice
print("rank ", matsize(H)[1]);
B = qflll(H~);                   \\ columns, LLL-reduced
n = matsize(B)[2];
\\ exact Gram-Schmidt (columns)
bs = vector(n); mu = Mat(vector(n));
for(i=1,n, bs[i]=B[,i];
  for(j=1,i-1,
    my(c=(B[,i]~*bs[j])/(bs[j]~*bs[j]));
    mu[i,j]=c; bs[i]=bs[i]-c*bs[j]));
xp = matsolveMod(A, h, 256);
t = -xp;                         \\ target, column vector
forstep(i=n,1,-1,
  my(c=(t~*bs[i])/(bs[i]~*bs[i]));
  t = t - round(c)*B[,i]);
xx = -Vec(t);                    \\ x = xp + v = -t_final
res = A*Mat(xx) - h;
ok = 1; for(i=1,48, if(res[i]%256 != 0, ok=0));
print("congruence ok: ", ok, "  maxabs: ", vecmax(vecabs(xx)));
write("x_babai.gp.out", Mat(xx)~);
print("wrote x_babai.gp.out");
