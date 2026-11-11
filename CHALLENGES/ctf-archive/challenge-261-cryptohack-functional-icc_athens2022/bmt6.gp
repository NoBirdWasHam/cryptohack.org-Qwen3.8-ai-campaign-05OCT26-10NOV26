p=1000000007;
print("v=",Vec([Mod(0,p),Mod(1,p)]));
print("pol of list:", Pol([Mod(0,p),Mod(1,p)],x));
print("vec back:", Vec(Pol([Mod(0,p),Mod(1,p)],x)));
print("1+x:", Vec(Pol([Mod(1,p),Mod(1,p)],x)));
A = Mod(0,p) + Mod(1,p)*x; print("A=",Vec(A));
