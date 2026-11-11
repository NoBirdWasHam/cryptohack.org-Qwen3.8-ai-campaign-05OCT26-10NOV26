X = [1,2; 1,-1; 0,3];
Y = qflll(X);
print("size ", matsize(Y), " Y=", Y);
Z = qflll(X~);
print("size2 ", matsize(Z), " Z=", Z);
