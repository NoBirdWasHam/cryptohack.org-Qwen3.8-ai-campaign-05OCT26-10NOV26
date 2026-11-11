default(parisize,"1024M");
N = read("nval.txt");
print("N bits ", logint(N,2)+1);
M = lcm(vector(50000, i, i));
print("p-1(B=5e4) gcd==1: ", gcd(Mod(2,N)^M - 1, N)==1);
hit=0;
for(i=1,30, my(g2 = ecm(N, 5000, 50000, 1000+i)); if(g2>1, print("ECM HIT ", g2); hit=1));
if(!hit, print("ECM B1=5000 x30: nothing"));
