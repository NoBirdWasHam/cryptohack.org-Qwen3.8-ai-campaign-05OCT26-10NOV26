# Pure-python MI generator over GF(2)^n, mirrors substitution-cipher-iii.sage (self-derived).
import random, sys

def pmul(a,b):
    r=0
    while b:
        if b&1: r^=a
        a<<=1; b>>=1
    return r
def pmod(a,i,n):
    for e in range(a.bit_length()-1, n-1, -1):
        if a>>e&1: a ^= i << (e-n)
    return a
def pdeg_mod(a,b):
    bb=b.bit_length()-1
    while a and a.bit_length()-1>=bb:
        a^=b<<(a.bit_length()-1-bb)
    return a
def pgcd(a,b):
    while b: a,b=b,pdeg_mod(a,b)
    return a
def primes_of(n):
    r=[];d=2
    while d*d<=n:
        while n%d==0: r.append(d); n//=d
        d+=1
    if n>1: r.append(n)
    return r
def is_irred(i,n):
    a=2
    for _ in range(n): a=pmod(pmul(a,a),i,n)
    if a!=2: return False
    for p in primes_of(n):
        m=n//p; a=2
        for _ in range(m): a=pmod(pmul(a,a),i,n)
        if pgcd(i,a^2)!=1: return False
    return True
def irreducible(n,rnd):
    while True:
        i=(1<<n)|1
        for e in set(rnd.randint(1,n-1) for _ in range(rnd.randint(1,12))): i^=1<<e
        if is_irred(i,n): return i

class MI:
    def __init__(self,n,i,MS,vs,r,MT,vt):
        self.n=n;self.i=i;self.MS=MS;self.vs=vs;self.r=r;self.MT=MT;self.vt=vt
    def eval_bits(self,bint):
        n=self.n
        y=0
        for j in range(n):
            if ((self.MS[j]&bint).bit_count()&1)^self.vs[j]: y|=1<<j
        a2=pmod(pmul(y,y),self.i,n)
        q=pmod(pmul(pmod(pmul(a2,y),self.i,n),self.r),self.i,n)
        out=0
        for j in range(n):
            if ((self.MT[j]&q).bit_count()&1)^self.vt[j]: out|=1<<j
        return out
    def polys(self):
        n=self.n
        f0=self.eval_bits(0)
        fe=[self.eval_bits(1<<k) for k in range(n)]
        pairs={}
        for j in range(n):
            for k in range(j+1,n):
                pairs[(j,k)]=self.eval_bits((1<<j)|(1<<k))
        out=[]
        for i in range(n):
            b0=(f0>>i)&1
            terms=[]
            if b0: terms.append('1')
            for k in range(n):
                if ((fe[k]>>i)&1)^b0: terms.append('x%d'%k)
            for (j,k),v in pairs.items():
                if ((v>>i)&1)^b0^((fe[j]>>i)&1)^((fe[k]>>i)&1): terms.append('x%d*x%d'%(j,k))
            out.append('+'.join(terms) if terms else '0')
        return out
    def ct(self,msgbytes):
        b=0; pos=0
        for c in msgbytes:
            for j in range(7,-1,-1):
                b |= ((c>>j)&1)<<pos; pos+=1
        return ''.join(str((self.eval_bits(b)>>i)&1) for i in range(self.n))

def is_invertible(rows,n):
    cur=list(rows)
    for col in range(n-1,-1,-1):
        p=None
        for idx,r in enumerate(cur):
            if (r>>col)&1: p=idx;break
        if p is None: return False
        cur[0],cur[p]=cur[p],cur[0]
        cur=[r^cur[0] if (idx and (r>>col)&1) else r for idx,r in enumerate(cur)][1:]
    return True

def gen(n,seed,path):
    rnd=random.Random(seed)
    i=irreducible(n,rnd)
    while True:
        RA=[rnd.getrandbits(n) for _ in range(n)]
        if is_invertible(RA,n): break
    while True:
        RB=[rnd.getrandbits(n) for _ in range(n)]
        if is_invertible(RB,n): break
    vs=[1 if rnd.getrandbits(1) else 0 for _ in range(n)]
    vt=[1 if rnd.getrandbits(1) else 0 for _ in range(n)]
    r=0
    for j in range(n):
        if rnd.getrandbits(1): r|=1<<j
    if r==0: r=1
    mi=MI(n,i,RA,vs,r,RB,vt)
    pols=mi.polys()
    nch=n//8
    msg1=bytes(rnd.randrange(33,127) for _ in range(nch))
    msg2=bytes(rnd.randrange(33,127) for _ in range(nch))
    s='('+','.join(pols)+')'
    open(path,'w').write(s+'\n'+mi.ct(msg1)+'\n'+mi.ct(msg2)+'\n')
    return msg1,msg2

if __name__=='__main__':
    n=int(sys.argv[1]); seed=int(sys.argv[2]); path=sys.argv[3]
    msg1,msg2=gen(n,seed,path)
    print('n',n,'msg1',repr(msg1),'msg2',repr(msg2))
