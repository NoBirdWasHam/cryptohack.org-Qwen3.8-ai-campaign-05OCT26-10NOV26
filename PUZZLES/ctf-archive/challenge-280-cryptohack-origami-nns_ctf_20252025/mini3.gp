default(parisize,"2G");
read("pkv128.gp");
n=128;q=127;d=256;
M=matrix(d,d);
for(i=1,n,for(j=1,n,M[i,j]=if(i==j,1,0); M[i,n+j]=pkv[((j-i)%n)+1]; M[n+i,n+j]=if(i==j,q,0)));
T=qflll(M~,0); V=M~*T;
mn=10^9; mi=0; for(i=1,d,s=sum(j=1,d,V[j,i]^2); if(s<mn,mn=s; mi=i));
print("minnorm2 col ",mn," ",mi);
for(j=1,n,print1(V[j,mi]," ")); print1("| "); for(j=1,n,print1(V[n+j,mi]," ")); print(" END");
