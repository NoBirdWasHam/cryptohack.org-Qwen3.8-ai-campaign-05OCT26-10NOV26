default(parisize,"1900M");
D_ = "~/Practice_runs/cryptohack_org/challenge-259-cryptohack-failproof_revenge-sekaictf202/";
read(D_ "A.gp");
read(D_ "rev_keep.txt");
read(D_ "cvecs.gp");
A2G = 0; U_ = 0; V_ = 0; DD = 0; nzcols = 0;
genm0(b) = {
  cv = eval(Str("c",b));
  Ucb = U_ * Mat(Vec(cv)~);
  y = vector(504, i, 0);
  for(j=1,256, jj = nzcols[j]; y[jj] = Ucb[j,1] / DD[j,jj]);
  m0p = Vec((V_ * Mat(y~))[,1]);
  maxres = vecmax(vector(256, j, abs(vecsum(vector(504, i, A2G[j,i]*m0p[i])) - cv[j])));
  print("@@m0 b", b-1, " maxres=", maxres, " t=", grosstime);
  fnm = Str(D_, "rev_m0_b", b-1, ".txt.new");
  write(fnm, Str(apply(i->m0p[i], [1..504])));
};
snfmain() = {
  grosstime = 0;
  A2G = matrix(256, 504, i, j, A[i, KEEPV[j]]);
  print("@@SNFstart@@", grosstime);
  S = matsnf(A2G, 1);
  U_ = S[1]; V_ = S[2]; DD = S[3];
  print("@@SNFdone@@", grosstime);
  cnz = vector(504, i, sum(k=1,256, DD[k,i]^2));
  nzcols = select(i->cnz[i]!=0, [1..504]);
  print("@@rank@@", #nzcols);
  maxdd = 1; for(j=1,256, dd = DD[j,nzcols[j]]; if(abs(dd)>maxdd, maxdd=abs(dd)));
  print("@@maxDD@@", maxdd);
  genm0(1);
  genm0(7);
  print("@@SNFALLDONE@@", grosstime);
}
snfmain()
