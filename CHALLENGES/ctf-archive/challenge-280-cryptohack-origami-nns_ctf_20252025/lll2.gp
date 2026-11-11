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
  mx=0;
  for(j=1,d, if(abs(B[i,j])>mx,mx=abs(B[i,j])));
  if(mx<=1,
    w0=0; w1=0;
    for(j=1,n, if(B[i,j]!=0,w0++));
    for(j=1,n, if(B[i,n+j]!=0,w1++));
    print("SMALL row ",i," w0=",w0," w1=",w1);
  );
);
w=open("gprows.txt","w");
for(i=1,8,
  for(j=1,d, print1(B[i,j]," "));
  print1("\n");
);
close(w);
