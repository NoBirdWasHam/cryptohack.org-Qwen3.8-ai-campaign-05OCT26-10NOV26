default(parisizemax,"1g");
default(parisize,"512m");
p=0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF;
a=0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC;
for(i=1,3, b=random(p); N=ellap(ellinit([a,b]),p); F=factor(N,65537); nf=matsize(F)[1]; M=1; for(j=1,nf, pp=F[j,1]; ee=F[j,2]; if(pp<=65537, M=M*pp^ee)); print(i," log2M=",log(M)/log(2)));
