p = 1019;
E = ellinit(Mod([0,0,0,1,0],p));
ph = ellisogeny(E,[844,833]);
print("cod: ", ph[1]);
print("apply R: ", ellisogenyapply(ph[2], [5,580]));
