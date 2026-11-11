default(parisize,"4G");
D_ = "~/Practice_runs/cryptohack_org/challenge-259-cryptohack-failproof_revenge-sekaictf202/";
read(D_ "A.gp");
read(D_ "cvecs.gp");
print("read done ", matsize(A));
R = matsnf(A, 1);  \\ [U,V,D] with U*A*V = D
U_ = R[1]; V_ = R[2]; Dm = R[3];
print("matsnf done ", matsize(U_), matsize(V_), matsize(Dm));
n = matsize(A)[2]; m = matsize(A)[1];
cnz = vector(n, i, sum(k=1,m, Dm[k,i]^2));  \\ zero iff column of D is zero
kcols = select(i->cnz[i]==0, [1..n]);
nzcols = select(i->cnz[i]!=0, [1..n]);
print("kernel dim: ", #kcols, " rank cols: ", #nzcols);
dvec = vector(m, j, Dm[j, nzcols[j]]);
print("divisors: ", dvec);
Kraw2 = concat(apply(i->Mat([Vec(V_[,i])]), kcols));  \\ rows = ker vectors (big)
print("Kraw2 size ", matsize(Kraw2));
Uk = qflll(Kraw2~);         \\ columns=ker vecs; reduced basis = Kraw2~ * Uk
Kred = (Kraw2~ * Uk)~;      \\ rows = reduced ker vectors
print("qflll done");
write(D_ "Kred.gp", Str(Kred), "\n");
\\ particular solutions per block: y[nz_j] = (U c)_j / d_j ; x = V y
for(b=1, NB,
  cb = eval(Str("c",b));
  Uc = U_*Vec(cb);
  y = vector(n, i, 0);
  for(j=1, m,
    if(Uc[j] % dvec[j] != 0, print("NONEXACT block ", b, " row ", j));
    y[nzcols[j]] = Uc[j] \ dvec[j];
  );
  m0 = V_*y;
  write(D_ "m0.gp", Str(m0), "\n");
  print("block ", b, " done");
);
print("ALLDONE");
