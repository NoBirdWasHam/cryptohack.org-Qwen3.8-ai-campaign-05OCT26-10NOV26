default(parisize,"256M");
\\ probe structure of garbage root a1 when Delta=QNR mod p
\\ solve_quad from server, in GP:
sq(r,c,p)=my(e=(p-1)\2, res=[1,0,0], cur=[0,1,0]);
{
  my(mod,pol);
  mod(v)=if(v[3]==0,return(v)); v[2]=Mod(v[2]+v[3]*r,p); v[1]=Mod(v[1]-v[3]*c,p); v[3]=0; v;
  pol(v1,v2)=my(v); v=mod([v1[1]*v2[1], v1[1]*v2[2]+v1[2]*v2[1], v1[2]*v2[2]]); v;
  while(1,
    if(e%2==1, res=pol(res,cur));
    e=e\2; if(e==0, break);
    cur=pol(cur,cur));
  my(a1=-(res[1]-1)/res[2], a2=r-a1);
  [a1,a2]
}
p=nextprime(10^15+39); \\ ensure p%4==3
while(p%4!=3, p=nextprime(p+2));
c=2; while(kronecker(c,p)!=-1, c++);
print("p=",p," c=",c);
for(i=1,12,
  my(r=random(p-1)+1);
  my(D=r^2-4*c);
  if(Mod(D,p)!=0 && kronecker(Mod(D,p),p)==-1,
    my(ab=sq(Mod(r,p),Mod(c,p),p));
    my(a1=ab[1],a2=ab[2]);
    my(e=a1*a2-c);            \\ failure of root property
    my(w=(2*a1-r)^2);         \\ would be Delta for true root
    print("D^((p-1)/2)=",lift(Mod(D, p)^((p-1)/2))==p-1);
    print("  e=",lift(e)," legendre(e)=",kronecker(Mod(e%p,p),p));
    print("  w=",lift(w)," w==e?", lift(w)==lift(e%p), " w==4e?", lift(w)==lift(4*e)%p, " w==-D?", lift(w)==lift(-D)%p, " e==-D?", lift(e)==lift(-D)%p, " e==c?", lift(e)==lift(c)%p, "e==D", lift(e)==lift(D)%p);
  )
);
