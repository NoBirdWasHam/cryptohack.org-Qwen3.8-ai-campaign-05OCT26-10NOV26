default(parisizemax,0); default(parisize,2^30);
f = factor(110791754886372871786646216601736686131457908663834453133932404548926481065302);
for(i=1,matsize(f)[1], print(f[i,1], " ^ ", f[i,2]));
