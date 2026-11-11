\\ Bostan-Mori for j(ITERS) mod p, data in bm_data.gp (p, N, P0, Q0)
default(parisize, "512m");
read("bm_data.gp");
P = Pol(apply(t->Mod(t,p), P0), x);
Q = Pol(apply(t->Mod(t,p), Q0), x);
n = N;
k = 0;
while(n > 0,
  Qm = subst(Q, x, -x);
  S = P*Qm;
  V = Vec(S);
  \\ take even or odd coefficients
  if(n%2==0,
    P = Pol(vector(#V\2+1, i, if(2*i-1<=#V, V[2*i-1], 0)), x),
    P = Pol(vector(#V\2,   i, V[2*i]), x)
  );
  W = Vec(Q*Qm);
  Q = Pol(vector(#W\2+1, i, W[2*i-1]), x);
  n = n // 2; k++;
  if(k%20==0, print("step ", k, " degQ=", poldegree(Q)));
);
print("iters=", k, " degQ=", poldegree(Q));
print("jt=", lift(polcoeff(P,0) / polcoeff(Q,0)));
