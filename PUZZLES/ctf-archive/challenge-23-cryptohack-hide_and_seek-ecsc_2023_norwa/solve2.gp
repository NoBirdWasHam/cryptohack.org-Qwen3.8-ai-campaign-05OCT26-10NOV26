\\ hide_and_seek GP solver v2: recover P,X from tuple pairs; PH+BSGS per factor
default(parisize,"1G"); default(parisizemax,"2G");
read("data.gp");
p = 1789850433742566803999659961102071018708588095996784752439608585988988036381340404632423562593;
aa = Mod(62150203092456938230366891668382702110196631396589305390157506915312399058961554609342345998, p);
bb = Mod(1005820216843804918712728918305396768000492821656453232969553225956348680715987662653812284211, p);
E = ellinit([0,0,0,aa,bb]);
t = 16093597302722077219468084775737143208134062101;
n = p+1-t;
facs = [12775224751,13026062843,18511195699,24508446437,25961704469,28450356619,31034521019,31982226581,32337773063];
prodok = 1; for(i=1,#facs, prodok *= facs[i]);
print("facprod_ok=", prodok==n);

Rv = vector(#data, i, [Mod(data[i][3][1],p), Mod(data[i][3][2],p)]);

recover(i,j) = { my(ai,bi,aj,bj,D,S,Tm,Dinv,r1,r2);
  ai=data[i][1]; bi=data[i][2]; aj=data[j][1]; bj=data[j][2];
  D = (aj*bi - ai*bj) % n;
  if(D==0, return(0));
  S = elladd(E, ellmul(E,Rv[j],bi), ellmul(E,Rv[i],-bj));
  Tm = elladd(E, ellmul(E,Rv[i],aj), ellmul(E,Rv[j],-ai));
  if(S == [], return(0));
  Dinv = lift(Mod(D,n)^-1);
  r1 = ellmul(E,S,Dinv);
  r2 = ellmul(E,Tm,Dinv);
  return([r1,r2]);
}

key(Pt) = if(Pt==[], "inf", Str(lift(Pt[1]), ";", lift(Pt[2])));

bsgs(Q,Y,q) = { my(m,T,acc,ng,xi,cur,jj,cand,j2);
  m = ceil(sqrt(q));
  T = Map(); acc = [];
  for(jj=0,m-1, if(!mapisdefined(T,key(acc)), mapput(T,key(acc),jj)); acc = elladd(E,acc,Q));
  ng = ellmul(E,Q,-m);
  xi = -1; cur = Y;
  for(jj=0,m-1,
    if(xi<0,
      if(mapisdefined(T,key(cur)),
        j2 = mapget(T,key(cur));
        cand = jj*m + j2;
        if(cand < q, if(ellmul(E,Q,cand)==Y, xi = cand));
      );
      if(xi<0, cur = elladd(E,cur,ng));
    );
  );
  return(xi);
}

P = 0; X = 0;
for(k=1,#data-1,
  if(P==0,
    my(r);
    r = recover(k, k+1);
    if(r!=0, P=r[1]; X=r[2]);
  );
);
if(P==0, error("no pair"));
print("order_check=", ellmul(E,P,n) == []);

xs = [];
for(k=1,#facs,
  my(q,xi);
  q = facs[k];
  xi = bsgs(ellmul(E,P,n\q), ellmul(E,X,n\q), q);
  if(xi<0, error("bsgs fail k=",k));
  print("q=",q," x=",xi);
  xs = concat(xs,xi);
);
x = 0; M = 1;
for(k=1,#facs,
  my(q,d,r);
  q = facs[k];
  d = lift(Mod(M,q)^-1);
  r = ((xs[k]-x) * d) % q;
  x = x + M*r; M = M*q;
);
x = x % n;
print("verify_dlp=", ellmul(E,P,x)==X);
print("XFLAG=",x);
