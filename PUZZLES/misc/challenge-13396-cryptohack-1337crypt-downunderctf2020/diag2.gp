default(parisize,"2G");
P0=Pol(Vec(readvec("r0.txt")));
P1=Pol(Vec(readvec("r1.txt")));
P2=Pol(Vec(readvec("r2.txt")));
P3=Pol(Vec(readvec("r3.txt")));
g=gcd(gcd(P0,P1),gcd(P2,P3)); g=g/content(g);
print1("GCDDEG ",poldegree(g),"\n");
forprime(p=5,100, my(rs=polrootsmod(g,p)); print1("R ",p); for(i=1,#rs,print1(" ",lift(rs[i]))); print1("\n"); );
quit();
