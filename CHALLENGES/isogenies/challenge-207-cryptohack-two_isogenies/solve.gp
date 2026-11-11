/* two_isogenies — Vélu 2-isogeny y2=x3+x, kernel (i,0), p=2^18*3^13-1
   PARI: authoritative ellisogeny. j(E') = 287496 (bare flag). */
K=bnfinit(t^2+1);
i=Mod(t,t^2+1);
E=ellinit([0,0,0,1,0],K);
ph=ellisogeny(E,[i,0]);
Cc=ellinit(ph[1]);
print("codomain a4=",ph[1][4]," a6=",ph[1][5],"\n");
print("j(E') = ",Cc[13],"\n");
