default(parisizemax,0); default(parisize,2^30);
pp = 2^192 - 237;
N  = 6277101735386680763835789423072729104060819681027498877478;
t  = 2*pp + 2 - N;
print("twist=", t);
print("bits=", sizebucket(t));
f = factor(t);
for(i=1, matsize(f)[1], print(f[i,1], "^", f[i,2]));
