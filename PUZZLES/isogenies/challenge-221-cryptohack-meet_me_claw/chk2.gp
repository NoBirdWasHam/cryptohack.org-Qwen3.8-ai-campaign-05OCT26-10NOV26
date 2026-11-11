p = 62207;
E = ellinit(Mod([0,0,0,1,0],p));
ph = ellisogeny(E,[54897,40274]);
print("cod: ", ph[1]);
print("apply ph: ", ellisogenyapply(ph, [10810,29263]));
print("apply ph2: ", ellisogenyapply(ph[2], [10810,29263]));
