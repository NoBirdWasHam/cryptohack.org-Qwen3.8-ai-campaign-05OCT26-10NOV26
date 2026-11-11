p = 11;
ea = 3;
for(i=1, ea,
  Q = 2^(ea-i);
  [Fc, phi] = [Q, Q+1];
  print(Fc)
)
print("done");
