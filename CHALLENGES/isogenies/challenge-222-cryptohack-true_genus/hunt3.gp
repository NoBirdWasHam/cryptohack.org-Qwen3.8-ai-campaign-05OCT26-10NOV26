\\ find p' = 2*prod(ls')-1, p' = 1 mod 3, 9 | h(-4p'), cyclic 2/3 structure
default(parisize,"512M");
pr = [5,7,11,13,17,19,23,29,31,37,41,43,47];
my(N = 2^length(pr) - 1);
for(n=1,N,
  my(v=[], pd=1);
  for(i=1,#pr, if(bitand(n,2^(i-1)), (v=concat(v,pr[i]); pd*=pr[i])));
  if(pd>20000, next);
  if(pd%3!=1, next);
  my(pp = 2*pd-1);
  if(!isprime(pp), next);
  my(K=bnfinit(x^2+pp,1));
  if(K.no%9!=0, next);
  print("P ",pp," ls ",v," h ",K.no," cyc ",K.cyc);
);
