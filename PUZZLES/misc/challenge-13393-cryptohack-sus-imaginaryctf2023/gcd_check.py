import sympy, math
n=None; e=None; c=None
exec(open("output.txt").read().replace(" ",""))
L=math.log2(n)
print("n bits:", n.bit_length(), "log2 n ~", L)
print("XY unshifted bits:", 512+1536, " shifted-tight bits:", 510+1535, " threshold 2/3*log2(n):", 2*L/3)
x,y=sympy.symbols('x y')
f2=sympy.expand((x**2+x+1)*y-n)
f1=sympy.expand((x**3+x**2+x)*y-n)
print("content x:", sympy.content(f2,x), " content y:", sympy.content(f2,y))
print("factor(f2):", sympy.factor(f2))
print("factor(f1):", sympy.factor(f1))
print("gcd(f1,f2):", sympy.gcd(f1,f2))
