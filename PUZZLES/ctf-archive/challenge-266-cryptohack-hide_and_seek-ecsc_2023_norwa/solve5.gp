\\ hide_and_seek GP solver v5 (flat GP statements only)
default(parisize,"1G"); default(parisizemax,"2G");
read("data.gp");
p = 1789850433742566803999659961102071018708588095996784752439608585988988036381340404632423562593;
aa = Mod(62150203092456938230366891668382702110196631396589305390157506915312399058961554609342345998, p);
bb = Mod(1005820216843804918712728918305396768000492821656453232969553225956348680715987662653812284211, p);
E = ellinit([0,0,0,aa,bb]);
t = 16093597302722077219468084775737143208134062101;
n = p+1-t;
facs = [12775224751,13026062843,18511195699,24508446437,25961704469,28450356619,31034521019,31982226581,32337773063];
prodok = 1;
for(i=1,#facs, prodok *= facs[i]);
print("facprod_ok=", prodok==n);

Rv = vector(#data, r0, [Mod(data[r0][3][1],p), Mod(data[r0][3][2],p)]);

recover(ii,jj) = {
  my(D,S,Tm,Dinv,ai,bi,aj,bj);
  ai=data[ii][1]; bi=data[ii][2]; aj=data[jj][1]; bj=data[jj][2];
  D = (aj*bi - ai*bj) % n;
  if(D==0, return(0));
  S = elladd(E, ellmul(E,Rv[jj],bi), ellmul(E,Rv[ii],-bj));
  Tm = elladd(E, ellmul(E,Rv[ii],aj), ellmul(E,Rv[jj],-ai));
  if(S == [0] || Tm == [0], return(0));
  Dinv = lift(Mod(D,n)^-1);
  return([ellmul(E,S,Dinv), ellmul(E,Tm,Dinv)]);
}

key(Pt) = if(Pt==[0], "inf", Str(lift(Pt[1]), ";", lift(Pt[2])));

\\ globals used by bsgs
TB = Map(); MM = 0; GQ = 0; GY = 0; GCUR = 0; GNG = 0; GS = -1; QL = 0;

gstep(jj) = { my(j2,cand);
  if(GS>=0, return(GS));
  if(!mapisdefined(TB,key(GCUR)), return(-1));
  j2 = mapget(TB,key(GCUR));
  cand = jj*MM + j2;
  if(cand >= QL, return(-1));
  if(ellmul(E,GQ,cand) != GY, return(-1));
  return(cand);
}

bsgs(Q,Y,q) = {
  my(jj,acc);
  MM = ceil(sqrt(q)); QL = q; GQ = Q; GY = Y; GS = -1;
  TB = Map(); acc = [0];
  for(jj=0,MM-1, if(!mapisdefined(TB,key(acc)), mapput(TB,key(acc),jj)); acc = elladd(E,acc,Q));
  GNG = ellmul(E,Q,-MM);
  GCUR = Y;
  for(jj=0,MM-1, GS = gstep(jj); if(GS<0, GCUR = elladd(E,GCUR,GNG)));
  return(GS);
}

P = 0; X = 0; RREC = 0;
for(k=1,#data-1, if(P==0 && (RREC = recover(k,k+1)) != 0, [P,X] = RREC));
if(P==0, error("no pair"));
print("order_check=", ellmul(E,P,n) == [0]);

xs = [];
for(k=1,#facs, xi = bsgs(ellmul(E,P,n\facs[k]), ellmul(E,X,n\facs[k]), facs[k]); if(xi<0, error("bsgs fail k=",k)); print("q=",facs[k]," x=",xi); xs = concat(xs,xi));
print("xs=",xs);
x = 0; M = 1;
for(k=1,#facs, d = lift(Mod(M,facs[k])^-1); r2 = ((xs[k]-x) * d) % facs[k]; x = x + M*r2; M = M*facs[k]);
x = x % n;
print("verify_dlp=", ellmul(E,P,x)==X);
print("XFLAG=",x);
