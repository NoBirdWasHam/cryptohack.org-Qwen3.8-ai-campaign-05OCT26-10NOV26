n=3;
s=0;
for(i=1,n,
  for(j=1,n,
    s+=i*j;
  );
);
print(s);
