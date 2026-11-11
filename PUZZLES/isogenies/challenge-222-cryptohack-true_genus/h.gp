default(parisize,"2G");
p = 38883164557681836128780386500217425544824614969;
D = -4*p;
print("D=",D);
h = qfbclassno(D);
print("h(-4p)=",h);
f = factor(h);
print("factorization:");
for(i=1, matsize(f)[1], print(f[i,1], "^", f[i,2]));
