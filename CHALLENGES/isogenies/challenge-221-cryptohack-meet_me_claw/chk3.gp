p = 62207;
E = ellinit(Mod([0,0,0,1,0],p));
ph = ellisogeny(E,[54897,40274]);
print("ph2: ", ph[2]);
print("apply: ", ellisogenyapply(ph[2], [10810,29263]));
