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
print("e/N ~ %s..." % str(e//N))
# collect ALL convergents + semiconvergents with denominator in (2^508, 2^514)
seen=set()
rows=[]
for i in range(0,len(conv)):
    p,q=conv[i]
    if (1<<508) < q < (1<<514):
        rows.append(('C',i,q,p))
for i in range(1,len(conv)):
    p_im1,q_im1=conv[i-1]; p_im2,q_im2=conv[i-2]
    a_i=a_list[i-1]
    for t in range(1,a_i+1):
        d=t*q_im1+q_im2; k=t*p_im1+p_im2
        if (1<<508) < d < (1<<514):
            rows.append(('S',i,t,d,k))
rows.sort(key=lambda r:r[2])
print("candidates with d in (2^508,2^514):",len(rows))
best=None
for typ,i,t,d,k in rows:
    # approximation error |e/N - k/d|
    err = e*d - k*N          # = (e/N - k/d)*N*d ... sign
    # exact test
    ok = (e*d-1)%k==0
    inwin = d_lo < d < d_hi
    mark = "<<< IN-WINDOW" if inwin else ""
    if inwin:
        print("  %s i=%d t=%s d bits=%d k bits=%d (ed-1)%%k==%s  |e*d-k*N| bits=%d %s"%(typ,i,t,d.bit_length(),k.bit_length(),ok,(e*d-k*N).bit_length(),mark))
    # track best approximation in window
    if inwin:
        score = abs(err)
        if best is None or score<best[0]:
            best=(score,typ,i,t,d,k)
if best:
    score,typ,i,t,d,k=best
    print("\nBEST in-window approx: %s i=%d t=%s d bits=%d  (ed-1)%%k==%s"%(typ,i,t,d.bit_length(),(e*d-1)%k==0))
    print("d = %s"%d)
    print("k = %s"%k)
    print("(e*d-1)/k = phi?  bits=%d"%( (e*d-1)//k ).bit_length() if (e*d-1)%k==0 else "N/A (not divisible)")
