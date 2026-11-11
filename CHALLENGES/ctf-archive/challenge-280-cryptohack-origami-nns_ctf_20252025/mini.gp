default(parisize,"512M");
read("pkv128.gp");
n=128;q=127;d=256;
M=matrix(d,d);
for(i=1,n,for(j=1,n,M[i,j]=if(i==j,1,0); M[i,n+j]=pkv[((j-i)%n)+1]; M[n+i,n+j]=if(i==j,q,0)));
T=qflll(M,0); V=M*T;
best=10^9;
for(r=1,300,for(k=1,40,i=random(d)+1; j=random(d)+1; c=random(3)-1; if(i!=j,for(t=1,d,V[i,t]+=c*V[j,t]))); T=qflll(V,0); V=V*T; mn=10^9; for(i=1,d,s=sum(j=1,d,V[i,j]^2); if(s<mn,mn=s)); if(mn<best,best=mn; print("round ",r," best ",best)); if(best<=80,for(k=1,d,if(sum(j=1,d,V[k,j]^2)<=80,print1("DUMP "); for(j=1,n,print1(V[k,j]," ")); print1("| "); for(j=1,n,print1(V[k,n+j]," ")); print(" END")))));
print("done best=",best);
