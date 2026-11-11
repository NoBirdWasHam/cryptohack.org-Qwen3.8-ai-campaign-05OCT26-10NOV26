default(parisize, "512m");
p = 1000000007;
P = Pol([0,1],x); Q = Pol([1,-1,-1],x);
n = 1000;
while(n>0,
  {
  Qm = subst(Q,x,-x);
  V = Vec(P*Qm);
  if(n%2==0, P = Pol(vector(#V\2+1,i,if(2*i-1<=#V,V[2*i-1],0)),x), P = Pol(vector(#V\2,i,V[2*i]),x));
  W = Vec(Q*Qm);
  Q = Pol(vector(#W\2+1,i,W[2*i-1]),x);
  n = n // 2;
  });
print("fib1000=", lift(P[1]/Q[1]), " expect 517691607");
