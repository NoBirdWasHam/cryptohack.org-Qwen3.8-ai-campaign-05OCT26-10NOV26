p=419
inv=lambda v: pow(v%p,-1,p)
def issq(v):
    v%=p
    return v==0 or pow(v,(p-1)//2,p)==1
def isqrt(v):
    v%=p
    return pow(v,(p+1)//4,p) if issq(v) else None
# PARI ellisogeny(E, (185,73)) codomain: y2 = x3 + 269x + 82
a,b=269,82
roots=[x for x in range(p) if (x*x*x+a*x+b)%p==0]
v=roots[0]                       # 23
c2=(3*v)%p                       # X^2 coeff after x=X+v
c1=(3*v*v+a)%p                   # X coeff = 180
u2=isqrt(c1)                     # 173, u2^2=c1
A=(c2*inv(u2))%p                 # 199
# twist check: the explicit isomorphism must send real points to y2=x3+A x2+x
u=isqrt(u2); u3=u2*u%p
ok=0; tot=0
for x in range(p):
    v2=(x*x*x+a*x+b)%p
    if not issq(v2): continue
    y=isqrt(v2)
    Xp=(x-v)*inv(u2)%p; Yp=y*inv(u3)%p
    tot+=1
    if (Yp*Yp - (Xp*Xp*Xp+A*Xp*Xp+Xp))%p==0: ok+=1
assert ok==tot and tot>100, (ok,tot)
print("Montgomery A =",A,"  (isomorphism verified on",tot,"points)")
