default(parisize, "512m");
p = 1000000007;
P = Pol([Mod(0,p),Mod(1,p)],x); Q = Pol([Mod(1,p),Mod(-1,p),Mod(-1,p)],x);
n = 1000;
while(n>0, { Qm = subst(Q,x,-x); V = Vec(P*Qm); if(n%2==0, P = Pol(vector((#V+1)\2,i,V[2*i-1])), P = Pol(vector(#V\2,i,V[2*i]))); W = Vec(Q*Qm); Q = Pol(vector((#W+1)\2,i,W[2*i-1])); n = n \ 2; });
print("fib1000=", lift(polcoeff(P,0) / polcoeff(Q,0)), " expect 517691607");
