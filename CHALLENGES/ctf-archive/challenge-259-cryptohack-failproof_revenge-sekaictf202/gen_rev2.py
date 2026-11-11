# Phase B generator v2: per-block Kannan-CVP GP scripts (321 recipe, revenge dims).
import os, re
D = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(D, f).replace('\\', '/')

TMPL = '''default(parisize,"1500M");
D_ = "PATH/";
nearestplane(B,t) = { local(mm,nn,bs,cs,tt,i,k,v,mu,q); mm=matsize(B)[1]; nn=matsize(B)[2]; bs=vector(mm); cs=vector(mm); for(i=1,mm, v=Vec(B[i,]); for(k=1,i-1, if(cs[k]==0, next()); mu=vecsum(vector(nn, j, B[i,j]*bs[k][j]))/cs[k]; if(mu!=0, v=v-mu*bs[k])); bs[i]=v; cs[i]=vecsum(vector(nn, j, v[j]*v[j]))); tt=Vec(t); forstep(i=mm,1,-1, if(cs[i]==0, next()); q=round(vecsum(vector(nn, j, tt[j]*bs[i][j]))/cs[i]); if(q!=0, tt=tt-q*Vec(B[i,]))); tt };
runblk() = {
  grosstime = 0;
  read(D_ "A.gp");
  read(D_ "rev_keep.txt");
  read(D_ "rev_K.gp");
  read(D_ "BLKFILE");
  nb = #KEEPV;
  d = matsize(K)[1];
  A2 = matrix(256, nb, i, j, A[i, KEEPV[j]]);
  maxres = vecmax(vector(256, j, abs(vecsum(vector(nb, i, A2[j,i]*m0p[i])) - cc[j])));
  print("@@TAG@@ m0 maxres=", maxres, " t=", grosstime);
  if(maxres!=0, error("bad m0"));
  T0 = vector(nb, i, 1 - 2*m0p[i]);
  B2 = matrix(d, nb, r, i, 2*K[r,i]);
  Bred = qflllgram(B2*B2~, 1) * B2;
  Tred = nearestplane(Bred, T0);
  print("@@TAG@@ Tred norm2=", vecsum(vector(nb, i, Tred[i]^2)), " t=", grosstime);
  rows = vector(d+1);
  for(r=1, d, rows[r] = concat(Vec(Bred[r,]), [0]));
  rows[d+1] = concat(Tred, [1]);
  M = matrix(d+1, nb+1, r, c, rows[r][c]);
  Ml = qflllgram(M*M~, 1) * M;
  G = Ml*Ml~;
  bound = nb + 9;
  print("@@TAG@@ qfminim start bound=", bound, " t=", grosstime);
  NV = qfminim(G, bound, 2);
  print("@@TAG@@ qfminim N=", NV[1], " maxn2=", NV[2], " t=", grosstime);
  if(NV[1]==0, print("@@TAG@@ FAIL0 no vectors below bound t=", grosstime); return());
  VV = NV[3];
  found = 0;
  for(i=1, matsize(VV)[2],
    cf = Vec(VV[,i]);
    if(#cf == nb+1, pt = cf, pt = Vec(cf~ * Ml));
    if(abs(pt[nb+1]) != 1, next());
    if(pt[nb+1] < 0, for(j=1,nb+1, pt[j] = -pt[j]));
    bad = 0; for(j=1,nb, if((T0[j]-pt[j])%2!=0, bad=1));
    if(bad, next());
    m = vector(nb, j, m0p[j] + (T0[j]-pt[j])/2);
    okb = 1; for(j=1,nb, if(m[j]!=0 && m[j]!=1, okb=0));
    if(!okb, next());
    chk = 1; for(j=1,256, if(vecsum(vector(nb, i, A2[j,i]*m[i])) != cc[j], chk=0));
    if(!chk, next());
    bits = vector(512, i, 0); for(j=1,nb, bits[KEEPV[j]] = m[j]);
    seg = vector(8, i2, sum(k=1, 8, bits[(23+i2)*8+k] * 2^(9-k)));
    write(D_ "OUTFILE", Str(seg));
    print("@@TAG@@ SOLVED seg=", seg, " t=", grosstime);
    found = 1);
  if(!found, print("@@TAG@@ FAIL no verified binary solution t=", grosstime));
}
runblk()
'''

K = []
for l in open(os.path.join(D,'rev_K.txt')):
    l = l.strip()
    if l: K.append(l.strip('[]'))
assert len(K) == 248
with open(os.path.join(D,'rev_K.gp'),'w') as f:
    f.write('K = [' + ';'.join(K) + '];\n')

def emit(tag, blkfile, outfile):
    s = TMPL.replace('PATH', P('')).replace('BLKFILE', blkfile).replace('OUTFILE', outfile).replace('@@TAG@@', tag)
    with open(os.path.join(D, f'runrev_{tag}.gp'), 'w') as f:
        f.write(s)
    print('wrote', f'runrev_{tag}.gp')

for bi in range(7):
    m0f = os.path.join(D, f'rev_m0_b{bi}.txt')
    if os.path.exists(m0f):
        m0raw = open(m0f).read().strip()
        txt = open(os.path.join(D,'cvecs.gp')).read()
        mline = re.search(rf'^c{bi+1} = (.*)$', txt, re.M).group(1)
        with open(os.path.join(D, f'revb{bi}.gp'), 'w') as f:
            f.write(f'm0p = {m0raw};\ncc = {mline}\n')
        emit(f'b{bi}', f'revb{bi}.gp', f'REVSEG_b{bi}.txt')
    else:
        print('skip real b', bi, '(no m0 yet)')
    emit(f'toy{bi}', f'toy_b{bi}.gp', f'TOYSEG_b{bi}.txt')
print('done')
