from mpmath import mp, mpf, sqrt, quad, inf, nstr
mp.dps = 320
import json
d = json.load(open('output.txt'))
gx, gy = mpf(d['gx']), mpf(d['gy'])
px, py = mpf(d['px']), mpf(d['py'])

def u_of_x(x):
    # elliptic log for point (x, +y) on y^2=x^3-x, x>1: u = int_x^inf dt/(2 sqrt(t^3-t))
    f = lambda t: 1/(2*sqrt(t**3-t))
    # split integral for speed: x..M and M..inf via substitution
    M = x + 10
    I1 = quad(f, [x, M])
    # tail: t = M + s, s in [0,inf)
    I2 = quad(lambda s: f(M+s), [0, inf])
    return I1 + I2

omega = 2*u_of_x(mpf(1)+mpf(10)**-300)  # near x=1 -> half period; better compute directly
# better: half period = int_1^inf dt/(2 sqrt(t^3-t)) ; handle singular at 1 via substitution t=1+s^2
f2 = lambda s: 1/(2*sqrt((1+s**2)**3-(1+s**2)))*2*s  # dt = 2s ds
half = quad(f2, [0, 10]) + quad(lambda s: 1/(2*sqrt((1+s**2)**3-(1+s**2)))*2*s, [10, inf])
omega = 2*half
print("omega =", nstr(omega, 60))
uG = u_of_x(gx)
uP = u_of_x(px)
print("uG =", nstr(uG, 80))
print("uP =", nstr(uP, 80))
alpha = uG/omega
beta = uP/omega
print("alpha =", nstr(alpha, 80))
print("beta =", nstr(beta, 80))
print("beta/alpha =", nstr(beta/alpha, 40))
