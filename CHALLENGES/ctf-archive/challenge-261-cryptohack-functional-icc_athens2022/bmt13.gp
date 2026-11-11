default(parisize, "512m");
p = 1000000007;
\\ ascending coeff input via Polrev
P = Polrev([Mod(0,p),Mod(1,p)],x); Q = Polrev([Mod(1,p),Mod(-1,p),Mod(-1,p)],x);
n = 1000;
\\ ascending extract: E/S selection by power parity, then compress 2k->k
while(n>0, { Qm = subst(Q,x,-x); V = Vec(P*Qm); D = #V-1; if(n%2==0, P = Polrev(vector(D\2+1,k,polcoeff(P*Qm,2*k-2)),x), P = Polrev(vector((D+1)\2,k,polcoeff(P*Qm,2*k-1)),x)); W = Vec(Q*Qm); Q = Polrev(vector(poldegree(W)\2+1,k,polcoeff(W,2*k-2)),x); n = n \ 2; });
print("fib1000=", lift(polcoeff(P,0) / polcoeff(Q,0)), " expect 517691607");
