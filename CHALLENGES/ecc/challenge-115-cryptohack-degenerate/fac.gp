default(parisizemax,0); default(parisize,2^30);
f = factor(110791754886372871786646216601736686131170149361165602787891589423789760286950);
for(i=1,matsize(f)[1], print(f[i,1], " ^ ", f[i,2]));
