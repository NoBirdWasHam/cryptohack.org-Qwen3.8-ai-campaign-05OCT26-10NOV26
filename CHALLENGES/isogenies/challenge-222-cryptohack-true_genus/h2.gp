default(parisize,"4G");
p = 38883164557681836128780386500217425544824614969;
D = -4*p;
K = bnfinit(x^2 + p, 1);
print("CLASSNO=", K.no);
print("CLASSGRP=", K.cyc);
f = factor(K.no);
print("FACTORS:");
for(i=1,matsize(f)[1], print(f[i,1],"^",f[i,2]));
