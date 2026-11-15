print("type x:", type(x), " value:"); print(x);
f = x^2+x; print("deg=",poldegree(f)," lead=",pollead(f)," vec=",Vec(f));
g = z^2+z; print("zg deg=",poldegree(g)," vecz=",Vec(g, 'z') );
print("Pol([0,1],x)=", Pol([0,1],x), " vec=", Vec(Pol([0,1],x)));
print("1*x=", 1*x, " 0+x=", 0+x);
