default(parisize,"256M");
p = 62207;
E = ellinit(Mod([0,0,0,1,0],p));
Q = Mod([54897,40274],p);
ph = ellisogeny(E,[Q[1],Q[2]]);
Cc = ellinit(ph[1]);
print("codomain a4,a6 = ", Cc[4], " ", Cc[6]);
print("j = ", Cc[13]);
