\\ hide_and_seek GP solver: recover P,X from tuple pairs; PH+BSGS per factor
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
\\ recover P and X
P = 0; X = 0;
for(i=1,#data,
 for(j=i+1,#data,
  if(P==0,
    ai=data[i][1]; bi=data[i][2]; aj=data[j][1]; bj=data[j][2];
    D = (aj*bi - ai*bj) % n;
    if(D!=0,
      S = elladd(E, ellmul(E,Rv[j],bi), ellmul(E,Rv[i],-bj));
      Tm = elladd(E, ellmul(E,Rv[i],aj), ellmul(E,Rv[j],-ai));
      if(S != [],
        Dinv = lift(Mod(D,n)^-1);
        P = ellmul(E,S,Dinv); X = ellmul(E,Tm,Dinv);
      );
    );
  );
 ));
);
if(P==0, error("no pair"));
print("order_check=", ellmul(E,P,n) == []);
\\ sanity: all R in <P>: check n*R==[] trivially true on curve; stronger: check R1 == (a1+b1*x)P later.

key(Pt) = if(Pt==[], "inf", Str(lift(Pt[1]))","Str(lift(Pt[2])));
xs = [];
for(k=1,#facs,
  q = facs[k];
  h = n\q;
  Q = ellmul(E,P,h); Y = ellmul(E,X,h);
  m = ceil(sqrt(q));
  T = Map();
  acc = [];
  for(j=0,m-1, if(!mapisdefined(T,key(acc)), mapput(T,key(acc),j)); acc = elladd(E,acc,Q); );
  ng = ellmul(E,Q,-m);
  xi = -1; cur = Y;
  for(i=0,m-1,
    if(xi<0 && mapisdefined(T,key(cur)),
      j = mapget(T,key(cur));
      cand = i*m + j;
      if(cand < q && ellmul(E,Q,cand)==Y, xi = cand);
    );
    if(xi<0, cur = elladd(E,cur,ng));
  );
  if(xi<0, error("bsgs fail k=",k));
  print("q=",q," x=",xi);
  xs = concat(xs,xi);
);
\\ CRT
x = 0; M = 1;
for(k=1,#facs,
  q = facs[k];
  d = lift(Mod(M,q)^-1);
  r = ((xs[k]-x) * d) % q;
  x = x + M*r; M = M*q;
);
x = x % n;
print("verify_dlp=", ellmul(E,P,x)==X);
print("XFLAG=",x);
