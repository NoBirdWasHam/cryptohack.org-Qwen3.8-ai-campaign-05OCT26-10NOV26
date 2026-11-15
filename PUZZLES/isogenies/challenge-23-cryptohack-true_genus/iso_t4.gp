p = 2309;
E = ellinit([Mod(0,p), Mod(1,p)]);
Q = [Mod(0,p), Mod(1,p)];
H = Pol([Mod(0,p), Mod(1,p)], 'x);  \ x - 0
E2 = ellisogeny(E, H);
print("E2 = ", E2);
print("matsize: ", matsize(E2));
if(#E2>1, print("E2[1]=", E2[1], " E2[2]=", E2[2]));
