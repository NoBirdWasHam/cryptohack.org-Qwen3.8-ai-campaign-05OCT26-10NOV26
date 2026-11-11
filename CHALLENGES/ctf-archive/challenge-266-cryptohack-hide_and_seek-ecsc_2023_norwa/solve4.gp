\\ hide_and_seek GP solver v4
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
  my(D,S,Tm,Dinv,ai,bi,aj,bj,res);
  ai=data[ii][1]; bi=data[ii][2]; aj=data[jj][1]; bj=data[jj][2];
  D = (aj*bi - ai*bj) % n;
  if(D==0, return(0));
  S = elladd(E, ellmul(E,Rv[jj],bi), ellmul(E,Rv[ii],-bj));
  Tm = elladd(E, ellmul(E,Rv[ii],aj), ellmul(E,Rv[jj],-ai));
  if(S == [], return(0));
  Dinv = lift(Mod(D,n)^-1);
  res = [ellmul(E,S,Dinv), ellmul(E,Tm,Dinv)];
  return(res);
}

key(Pt) = if(Pt==[], "inf", Str(lift(Pt[1]), ";", lift(Pt[2])));

bsgs(Q,Y,q) = {
  my(m,Tb,acc,ng,xi,cur,jj,j2,cand);
  m = ceil(sqrt(q));
  Tb = Map();
  acc = [];
  for(jj=0,m-1,
    if(!mapisdefined(Tb,key(acc)), mapput(Tb,key(acc),jj));
    acc = elladd(E,acc,Q);
  );
  ng = ellmul(E,Q,-m);
  xi = -1;
  cur = Y;
  for(jj=0,m-1,
    if(xi<0,
      {
      if(mapisdefined(Tb,key(cur)),
        {
        j2 = mapget(Tb,key(cur));
        cand = jj*m + j2;
        if(cand < q && ellmul(E,Q,cand)==Y, xi = cand);
        }
      );
      if(xi<0, cur = elladd(E,cur,ng));
      }
    )
  );
  return(xi);
}

my(P,X,r);
P = 0; X = 0;
for(k=1,#data-1,
  if(P==0,
    {
    r = recover(k,k+1);
    if(r!=0, [P,X] = r);
    }
  )
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
  xs = concat(xs,xi)
);
x = 0; M = 1;
for(k=1,#facs,
  my(q,d,r2);
  q = facs[k];
  d = lift(Mod(M,q)^-1);
  r2 = ((xs[k]-x) * d) % q;
  x = x + M*r2;
  M = M*q
);
x = x % n;
print("verify_dlp=", ellmul(E,P,x)==X);
print("XFLAG=",x);
