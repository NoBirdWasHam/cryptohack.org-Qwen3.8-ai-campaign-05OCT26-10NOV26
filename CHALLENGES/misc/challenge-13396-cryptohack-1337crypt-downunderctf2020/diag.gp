default(parisize,"2G");
P0=Pol(Vec(readvec("r0.txt")));
P1=Pol(Vec(readvec("r1.txt")));
P2=Pol(Vec(readvec("r2.txt")));
print1("deg P0 ",poldegree(P0)," deg P1 ",poldegree(P1),"\n");
g1=gcd(P0,P1); print1("deg gcd01 ",poldegree(g1),"\n");
g2=gcd(g1,P2); print1("deg gcd012 ",poldegree(g2),"\n");
print1("roots gcd01 mod 5: ",Vec(polrootsmod(g1,5)),"\n");
quit();
