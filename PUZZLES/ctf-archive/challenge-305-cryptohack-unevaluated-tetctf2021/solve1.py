# Step 1: parse instance, recover p, verify group structure, get k mod p (p-adic log)
from Crypto.Util.number import isPrime
from Crypto.Cipher import AES
import ast, re

txt = open("output.txt").read()

def parse_complex(s):
    m = re.search(r"re=(\d+),\s*im=(\d+)", s)
    return int(m.group(1)), int(m.group(2))

def cmul(a, b, n):
    return ((a[0]*b[0]-a[1]*b[1]) % n, (a[0]*b[1]+a[1]*b[0]) % n)

def cpow(a, e, n):
    r = (1, 0)
    while e:
        if e & 1: r = cmul(r, a, n)
        a = cmul(a, a, n); e >>= 1
    return r

g = parse_complex(txt)
order = int(re.search(r"order = (\d+)", txt).group(1))
n = int(re.search(r"n = (\d+)", txt).group(1))
pk = parse_complex(txt.split("public_key =")[1])
# encrypted bytes
enc = ast.literal_eval("b'" + txt.split("encrypted_flag = ")[1].strip()[2:].rstrip("'") + "'")

p = int(n**0.5)
# exact isqrt
import math
p = math.isqrt(n)
print("p*p==n:", p*p == n, "p bits:", p.bit_length(), "p%4:", p%4, "p%3:", p%3)
if p % 3 == 2:
    q, r = (p-1)//2, (p+1)//12
else:
    q, r = (p-1)//6, (p+1)//4
print("q prime:", isPrime(q), "r prime:", isPrime(r), "p*q*r==order:", p*q*r == order)
print("g^order==1:", cpow(g, order, n) == (1,1-1))
print("order bits:", order.bit_length())

# p-Sylow: g_p = g^(order/p) has order p, g_p = 1 + p*u in F_p[i]
gp_ = cpow(g, order//p, n)
print("g_p:", gp_)
assert gp_ != (1,0)
def plog(x, p):  # x = 1+p*u mod p^2 -> u in F_p[i]
    assert (x[0]-1) % p == 0 and x[1] % p == 0
    return ((x[0]-1)//p % p, x[1]//p % p)
ug = plog(gp_, p)
X = cpow(pk, order//p, n)  # = g_p^k = 1 + p*k*u_g
uX = plog(X, p)
# invert ug in F_p[i]
def cinv(a, p):
    norm = (a[0]*a[0] + a[1]*a[1]) % p
    inv = pow(norm, p-2, p)
    return (a[0]*inv % p, (-a[1])*inv % p)
uginv = cinv(ug, p)
k0 = (uX[0]*uginv[0] - uX[1]*uginv[1]) % p
def cadd(a,b,p): return ((a[0]+b[0])%p,(a[1]+b[1])%p)
def cmulp(a,b): return ((a[0]*b[0]-a[1]*b[1])%p,(a[0]*b[1]+a[1]*b[0])%p)
print("k0 (=k mod p) bits:", k0.bit_length(), "check:", cmulp((k0%p,0),ug)==uX)

# T = pk * g^-k0 = g^(k-k0) = g^(p*c1)
g0inv = pow((g[0]*g[0]+g[1]*g[1]) % n, -1, n)
ginv = (g[0]*g0inv % n, (-g[1])*g0inv % n)
T = cmul(pk, cpow(ginv, k0, n), n)
print("T ok (T == cpow(g,p, n)^c1): ord check T^order==1:", cpow(T, order, n)==(1,0))
qpart = cpow(T, r, n)   # order q element
rpart = cpow(T, q, n)   # order r element
print("qpart^q==1:", cpow(qpart,q,n)==(1,0), " qpart!=1:", qpart!=(1,0))
print("rpart^r==1:", cpow(rpart,r,n)==(1,0))
# c1 bound
c1max = (2**256-1-k0)//p
print("c1max bits:", c1max.bit_length(), " q bits:", q.bit_length(), " c1max/q approx:", float(c1max)/q)
print("generator for q-DLP a_q = g^(p*r) order q: a_q^q==1:", cpow(cpow(g,p*r,n),q,n)==(1,0))
print("a_q:", cpow(g, p*r, n))
print("target q-DLP:", qpart)
# is qpart in F_p-ish? check imag mod p
print("qpart im mod p:", qpart[1] % p, " re mod p:", qpart[0] % p)
rq = cpow(g, p*q, n)
print("a_r = g^(p*q) order r:", cpow(rq,r,n)==(1,0), "im mod p:", rq[1]%p)
print("target r-DLP:", rpart)
aq = cpow(g, p*r, n)
tq = cpow(T, r, n)
print("F_p q-DLP base:", aq[0] % p)
print("F_p q-DLP target:", tq[0] % p)
import json
json.dump({"p":str(p),"q":str(q),"r":str(r),"k0":str(k0),"a_q":[str(qpart[0]),str(qpart[1])],"g_pr":[str(cpow(g,p*r,n)[0]),str(cpow(g,p*r,n)[1])],"T":[str(T[0]),str(T[1])],"enc":enc.hex()}, open("instance.json","w"))
print("saved instance.json, enc len:", len(enc))
