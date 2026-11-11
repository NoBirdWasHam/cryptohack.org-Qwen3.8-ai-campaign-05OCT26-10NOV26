import math
def read_vals(path):
    v={}
    for line in open(path):
        if '=' in line:
            a,b=line.split('=',1); v[a.strip()]=b.strip()
    return int(v['N'],16), int(v['e'],16), int(v['c'],16)
def cf(num,den):
    a_list,conv=[],[]
    p0,p1=0,1; q0,q1=1,0
    while den:
        a=num//den; a_list.append(a)
        p0,p1=p1,a*p1+p0; q0,q1=q1,a*q1+q0
        num,den=den,num-a*den
        conv.append((p1,q1))
    return a_list,conv
def is_square(x):
    if x<0: return False
    r=math.isqrt(x); return r*r==x
N,e,c=read_vals('big2_output.txt')
a_list,conv=cf(e,N)
d_lo=(1<<512)//3; d_hi=1<<512
# For each j (>=1), semiconvergents between C_{j-1} and C_j: (s*p_{j-1}+p_{j-2})/(s*q_{j-1}+q_{j-2}), s=1..a_j
def try_phi(k,d):
    num=e*d-1
    if num%k!=0: return None
    phi=num//k
    s=N-phi+1
    disc=s*s-4*N
    if disc<0 or not is_square(disc): return None
    r=math.isqrt(disc)
    if (s-r)%2: return None
    p=(s-r)//2; q=(s+r)//2
    if p*q!=N: return None
    return phi,p,q
print("Testing semiconvergents whose denominator d in (d_lo,d_hi):")
hits=0
for j in range(1,len(conv)):
    p_jm1,q_jm1=conv[j-1]
    p_jm2,q_jm2=conv[j-2]
    a_j=a_list[j]
    for s in range(1,a_j+1):
        d=s*q_jm1+q_jm2
        if not (d_lo<d<d_hi):
            continue
        k=s*p_jm1+p_jm2
        hits+=1
        res=try_phi(k,d)
        tag="<<< HIT" if res else ""
        if hits<=30 or res:
            print("j=%4d s=%3d a_j=%4d  d bits=%d  k bits=%d  %s"%(j,s,a_j,d.bit_length(),k.bit_length(),tag))
        if res:
            phi,p,q=res
            print("  *** p bits",p.bit_length(),"q bits",q.bit_length(),"p*q==N",p*q==N)
            m=pow(c,d,N)
            from Crypto.Util.number import long_to_bytes
            print("  FLAG:", long_to_bytes(m))
            open('flag.txt','wb').write(long_to_bytes(m))
            raise SystemExit
print("total d-in-window semiconvergents:",hits)
