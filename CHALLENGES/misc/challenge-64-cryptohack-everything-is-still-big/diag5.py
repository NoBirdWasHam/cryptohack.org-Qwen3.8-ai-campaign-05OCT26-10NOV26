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
N,e,c=read_vals('big2_output.txt')
a_list,conv=cf(e,N)
d_lo=(1<<512)//3; d_hi=1<<512
# Correct semiconvergents: between conv[i-1] and conv[i], t=1..a_list[i]
#   (p_{i-1}*t + p_{i-2}) / (q_{i-1}*t + q_{i-2})
# Also test the convergents themselves (t=a_list[i] gives conv[i]).
found=[]
for i in range(1,len(conv)):
    p_im1,q_im1=conv[i-1]
    p_im2,q_im2=conv[i-2]
    a_i=a_list[i]          # CORRECT index
    for t in range(1,a_i+1):
        d=t*q_im1+q_im2
        k=t*p_im1+p_im2
        if not (d_lo<d<d_hi):
            continue
        if (e*d-1)%k==0:
            phi=(e*d-1)//k
            # verify phi via factorization
            s=N-phi+1
            disc=s*s-4*N
            ok = disc>=0 and math.isqrt(disc)**2==disc and (s-math.isqrt(disc))%2==0
            if ok:
                r=math.isqrt(disc); p=(s-r)//2; q=(s+r)//2
                found.append((i,t,d,k,p,q))
                print("HIT i=%d t=%d (a_i=%d) d bits=%d k bits=%d | p*q==N=%s"%(
                    i,t,a_i,d.bit_length(),k.bit_length(), p*q==N))
if found:
    i,t,d,k,p,q=found[0]
    print("DECRYPTING with d bits=%d"%d.bit_length())
    m=pow(c,d,N)
    from Crypto.Util.number import long_to_bytes
    flag=long_to_bytes(m)
    print("FLAG:",flag)
    open('flag.txt','wb').write(flag)
else:
    print("no semiconvergent hit in window; dumping the in-window candidates (correct index)")
    for i in range(1,len(conv)):
        p_im1,q_im1=conv[i-1]; p_im2,q_im2=conv[i-2]; a_i=a_list[i]
        for t in range(1,a_i+1):
            d=t*q_im1+q_im2
            if not (d_lo<d<d_hi): continue
            k=t*p_im1+p_im2
            print("  i=%d t=%d a_i=%d d bits=%d k bits=%d div=%s |e*d-k*N| bits=%d"%(
                i,t,a_i,d.bit_length(),k.bit_length(),(e*d-1)%k==0,(e*d-k*N).bit_length()))
