A = x^2 + x + 3;
print("coeffs:", polcoeff(A,0), polcoeff(A,1), polcoeff(A,2), polcoeff(A,3));
print("vec:", Vec(A));
B = Pol([3,1,1],x);
print("B==A: ", B==A, " B=",B);
print("vecB:", Vec(B), " polcoeff(B,2)=",polcoeff(B,2));
