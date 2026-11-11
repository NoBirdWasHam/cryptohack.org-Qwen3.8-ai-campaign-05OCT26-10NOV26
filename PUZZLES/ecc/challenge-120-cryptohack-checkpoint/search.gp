\\ search.gp — find b such that #E(F_p) for y^2=x^3+a*x+b has a large B-smooth divisor
\\ usage: gp -q search.gp  (edit START/END for ranges)
default(parisize, "2g");
p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF;
a = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC;
B = 65537;
lo = 1; hi = 3000;
for(i = lo, hi,
  b = random(p);
  N = ellap(ellinit([a,b]), p);
  \\ quick reject: smooth part < 2^120  <=>  N \\ 1 (mod ...) — just factor with bound
  F = factor(N, B);
  M = 1;
  for(j=1, matsize(F)[1], if(F[j,1] <= B, M *= F[j,1]^F[j,2]));
  if(M > 2^126,
    print("HIT b=", b, " N=", N, " M=", M);
    write("hit.txt", Str(b " " N " " M));
  ,
    if(i % 500 == 0, print("i=", i, " log2M=", log(M)/log(2)));
  );
);
print("done");
