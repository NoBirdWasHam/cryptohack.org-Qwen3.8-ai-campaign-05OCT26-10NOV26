cs=[];
for(p=1001,6000, if(isprime(p)&&p%4==1&&p%3==2, my(f=factor(p+1)); if(vecmax(f[,1])<=139, my(K=bnfinit(x^2+p,1)); if(K.no%36==0&&K.no<500, print(p," h=",K.no," cyc=",K.cyc," p1fac=",Vecsmall(f[,1]))))));
print("END");
