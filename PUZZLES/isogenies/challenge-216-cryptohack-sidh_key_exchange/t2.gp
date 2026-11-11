p = 11;
f2 = ffinit(p, 2, 0x27x);
w = ffgen(f2, 0x27w);
ea = 3;
E = ellinit([Mod(1,p)+0*w, Mod(0,p)+0*w]);
for(i=1, ea,
  print("iter ", i);
  [Fc, phi] = [1, 2];
  E = ellinit([Mod(Fc,p)+0*w, Mod(phi,p)+0*w]);
);
print("done ", E.a4);
