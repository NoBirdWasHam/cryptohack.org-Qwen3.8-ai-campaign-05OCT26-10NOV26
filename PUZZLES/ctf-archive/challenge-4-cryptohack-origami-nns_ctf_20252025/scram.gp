default(parisize,"4G");
read("pk.gp");
n=512;q=127;d=1024;
M=matrix(d,d);
for(i=1,n,for(j=1,n,M[i,j]=if(i==j,1,0); M[i,n+j]=pkv[((j-i)%n)+1]; M[n+i,n+j]=if(i==j,q,0)));
B=qflll(M,3);
best=10^9;
for(r=1,40,for(k=1,300,i=random(1,d); j=random(1,d); c=random(-3,3); if(i!=j,for(t=1,d,B[t,i]+=c*B[t,j])); B=qflll(B,3); mn=10^9; mi=0; for(i=1,d,s=sum(j=1,d,B[j,i]^2); if(s<mn,mn=s; mi=i)); if(mn<best,best=mn; print("round ",r," best norm2 ",best)); if(best<=200, for(j=1,n,print1(B[j,mi]," ")); print1("| "); for(j=1,n,print1(B[n+j,mi]," ")); print(" END")););
print("chain done best=",best);
