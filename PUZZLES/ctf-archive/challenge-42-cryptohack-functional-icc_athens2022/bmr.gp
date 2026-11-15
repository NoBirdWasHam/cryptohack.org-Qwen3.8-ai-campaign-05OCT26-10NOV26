default(parisize, "512m");
read("bm_data.gp");
\\ P0,Q0 ascending; this build: Polrev = ascending->pol
P = Polrev(apply(t->Mod(t,p), P0),x); Q = Polrev(apply(t->Mod(t,p), Q0),x);
n = N;
k = 0;
while(n>0, { Qm = subst(Q,x,-x); S = P*Qm; V = Vec(S); D = poldegree(S); if(n%2==0, P = Polrev(vector(D\2+1,k2,V[D-2*k2+3]),x), P = Polrev(vector((D+1)\2,k2,V[D-2*k2+2]),x)); W = Q*Qm; W2 = Vec(W); D2 = poldegree(W); Q = Polrev(vector(D2\2+1,k2,W2[D2-2*k2+3]),x); n = n \ 2; k++; if(k%20==0, print("step ",k," degQ=",poldegree(Q))); });
print("iters=", k);
print("jt=", lift(polcoeff(P,0) / polcoeff(Q,0)));
