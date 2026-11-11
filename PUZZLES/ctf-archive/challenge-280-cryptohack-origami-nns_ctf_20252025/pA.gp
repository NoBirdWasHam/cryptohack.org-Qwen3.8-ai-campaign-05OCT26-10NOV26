n=64;d=128;
M=matrix(d,d);
for(i=1,n,for(j=1,n,M[i,j]=if(i==j,1,0); M[i,n+j]=random(127); M[n+i,n+j]=if(i==j,127,0)));
print("built ",gettime());
B=qflll(M~,3);
print("qflll T done ",gettime());
mn=10^9; for(i=1,d,s=sum(j=1,d,B[j,i]^2); if(s<mn,mn=s)); print("minnorm2 ",mn);
