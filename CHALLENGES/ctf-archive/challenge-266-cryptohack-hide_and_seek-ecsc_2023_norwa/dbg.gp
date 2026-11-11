default(parisize,"1G");
read("data.gp");
p = 1789850433742566803999659961102071018708588095996784752439608585988988036381340404632423562593;
print("p_bits=", logint(p,2)+1);
aa = Mod(62150203092456938230366891668382702110196631396589305390157506915312399058961554609342345998, p);
bb = Mod(1005820216843804918712728918305396768000492821656453232969553225956348680715987662653812284211, p);
E = ellinit([0,0,0,aa,bb]);
t = 16093597302722077219468084775737143208134062101;
n = p+1-t;
print("n_bits=", logint(n,2)+1);
R1 = [Mod(data[1][3][1],p), Mod(data[1][3][2],p)];
\ on-curve check via ellisoncurve? use elladd(E,R1,R1) != [] and manual:
x=R1[1]; y=R1[2];
print("oncurve=", y^2 == x^3 + aa*x + bb);
print("nR1_inf=", ellmul(E,R1,n) == []);
G0 = ellgenerators(E);
print("#E check gens order: ", ellmul(E,G0[1],n) == []);
o1 = ellorder(E, G0[1]);
print("ord(G0[1])=", o1 == n);
