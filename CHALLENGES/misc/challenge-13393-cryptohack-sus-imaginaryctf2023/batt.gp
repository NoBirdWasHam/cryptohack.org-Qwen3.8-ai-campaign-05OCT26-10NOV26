default(parisize,"1024M");
N = eval(Str(read("nval.txt")));
print("N bits ", bitsize(N));
print("p-1 B1=1e6: ", gcd(Mod(2,N)^lcm([1..1000000]) - 1, N));
