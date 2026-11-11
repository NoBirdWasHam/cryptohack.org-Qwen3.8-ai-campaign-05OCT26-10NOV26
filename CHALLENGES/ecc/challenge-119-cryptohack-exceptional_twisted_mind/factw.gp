default(parisizemax,0); default(parisize,2^31);
f = factor(115792089237316195423570985008687907853306888865655620237644798196568308995683);
for(i=1,matsize(f)[1], print(f[i,1], " ^ ", f[i,2]));
