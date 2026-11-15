default(parisize, "512m");
p = 1000000007;
\\ NOTE: this GP build: Vec(POL) = DESCENDING coeffs; Pol(list)=descending; Polrev=ascending.
P = Polrev([Mod(0,p),Mod(1,p)],x); Q = Polrev([Mod(1,p),Mod(-1,p),Mod(-1,p)],x);
n = 1000;
while(n>0, { Qm = subst(Q,x,-x); S = P*Qm; V = Vec(S); D = poldegree(S); if(n%2==0, P = Polrev(vector(D\2+1,k,V[D-2*k+3]),x), P = Polrev(vector((D+1)\2,k,V[D-2*k+2]),x)); W = Q*Qm; W2 = Vec(W); D2 = poldegree(W); Q = Polrev(vector(D2\2+1,k,W2[D2-2*k+3]),x); n = n \ 2; });
print("fib1000=", lift(polcoeff(P,0) / polcoeff(Q,0)), " expect 517691607");
