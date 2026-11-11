default(parisize,"4G");
read("pk.gp");
n=512;q=127;d=1024;
M=matrix(d,d);
for(i=1,n,
  for(j=1,n,
    M[i,j]=if(i==j,1,0);
    M[i,n+j]=pkv[((j-i)%n)+1];
    M[n+i,n+j]=if(i==j,q,0);
  );
);
print("built ",clock());
B=lll(M);
print("lll done ",clock());
for(i=1,d,
  v=B[i,];
  mx=0; w0=0; w1=0;
  for(j=1,d, if(abs(v[j])>mx,mx=abs(v[j])) );
  if(mx<=1,
    for(j=1,n, if(v[j]!=0,w0++));
    for(j=1,n, if(v[n+j]!=0,w1++));
    print("SMALL row ",i," w0=",w0," w1=",w1);
  );
);
write("smallrows.txt", B[1,]);
