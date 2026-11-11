default(parisize,"1500M");
default(realprecision,120);
D_ = "~/Practice_runs/cryptohack_org/challenge-259-cryptohack-failproof_revenge-sekaictf202/";
read(D_ "rev_keep.txt");
read(D_ "rev_K.gp");
read(D_ "revb1.gp");
nearestplane(B,t) = { local(mm,nn,bs,cs,tt,i,k,v,mu,q); mm=matsize(B)[1]; nn=matsize(B)[2]; bs=vector(mm); cs=vector(mm); for(i=1,mm, v=Vec(B[i,]); for(k=1,i-1, if(cs[k]==0, next()); mu=vecsum(vector(nn, j, B[i,j]*bs[k][j]))/cs[k]; if(mu!=0, v=v-mu*bs[k])); bs[i]=v; cs[i]=vecsum(vector(nn, j, v[j]*v[j]))); tt=Vec(t); forstep(i=mm,1,-1, if(cs[i]==0, next()); q=round(vecsum(vector(nn, j, tt[j]*bs[i][j]))/cs[i]); if(q!=0, tt=tt-q*Vec(B[i,]))); tt };
gsprof(GM, tag) = { local(n,bstar,i,j,dv,mu,vv); n=matsize(GM)[1]; bstar=vector(n); for(i=1,n, bstar[i]=Vec(Vec(GM[i,]))*1.0); for(i=1,n, for(j=1,i-1, dv=vecsum(vector(n,k,bstar[j][k]^2)); if(dv<=1e-30, next()); mu=vecsum(vector(n,k,bstar[i][k]*bstar[j][k]))/dv; bstar[i]=bstar[i]-mu*bstar[j])); vv=vector(n, i, vecsum(vector(n,k,bstar[i][k]^2))); print("@@",tag,"count le 513: ", #select(x->x<=513, vv)); print("@@",tag,"count le 2000: ", #select(x->x<=2000, vv)); print("@@",tag,"count le 50000: ", #select(x->x<=50000, vv)); print("@@",tag,"min: ", vecmin(vv), " max: ", vecmax(vv)); print("@@",tag,"prod n2 (det^2): ", vecprod(Vec(vv))); print("@@",tag,"every20: ", apply(x->round(x), Vec(vv)[Vecsmall(select(i->(i%20==1), [1..n]))])); };
runm() = {
  nb = #KEEPV;
  d = matsize(K)[1];
  T0 = vector(nb, i, 1 - 2*m0p[i]);
  B2 = matrix(d, nb, r, i, 2*K[r,i]);
  Bred = qflllgram(B2*B2~, 1) * B2;
  gsprof(Bred*Bred~, "K");
  Tred = nearestplane(Bred, T0);
  print("@@Tred norm2 = ", vecsum(vector(nb, i, Tred[i]^2)));
  rows = vector(d+1);
  for(r=1, d, rows[r] = concat(Vec(Bred[r,]), [0]));
  rows[d+1] = concat(Tred, [1]);
  M = matrix(d+1, nb+1, r, c, rows[r][c]);
  Ml = qflllgram(M*M~, 1) * M;
  print("@@shortrow n2 = ", vecsum(vector(nb+1, i, Ml[1,i]^2)));
  gsprof(Ml*Ml~, "M");
  print("@@MEASUREDONE@@");
}
runm()
