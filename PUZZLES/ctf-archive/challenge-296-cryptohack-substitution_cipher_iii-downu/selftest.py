# Self-test: synth_pub.txt -> msolve -> recover known msgs
import os, re, subprocess
D=os.path.dirname(os.path.abspath(__file__))
CH=os.path.dirname(D)
MS=r'~/tools/msolvedir/ucrt64/bin/msolve.exe'
t=open(os.path.join(D,'synth_pub.txt')).read().split('\n')
pub,ct1,ct2=t[0].strip(),t[1].strip(),t[2].strip()
s=pub[1:-1];polys=[];depth=0;cur=''
for ch in s:
    if ch=='(':depth+=1
    elif ch==')':depth-=1
    if ch==',' and depth==0:polys.append(cur);cur=''
    else:cur+=ch
polys.append(cur)
print('n polys', len(polys))
def gen(path, ct, extra_lin=None):
    vars=','.join('x%d'%i for i in range(80))
    lines=[vars,'2']
    pols=[]
    for i,p in enumerate(polys):
        terms=[x.strip() for x in p.split('+') if x.strip()]
        if ct[i]=='1':
            if terms==['1']: terms=[]
            else: terms.append('1')
        pols.append('+'.join(terms) if terms else '0')
    if extra_lin: pols+=extra_lin
    pols+=['x%d^2+x%d'%(v,v) for v in range(80)]
    open(path,'w').write('\n'.join(lines)+'\n'+',\n'.join(pols)+'\n')
def check(bits, ct):
    for i,terms in enumerate(polys):
        v=0
        for tm in terms:
            prod=1
            for tk in tm.split('*'):
                if tk=='1': continue
                prod&=bits[int(tk[1:])]
            v^=prod
        if str(v)!=ct[i]: return False
    return True
gen(os.path.join(D,'synth1.in'), ct1)
r=subprocess.run([MS,'-f',os.path.join(D,'synth1.in'),'-o',os.path.join(D,'synth1.out'),'-t','4'],capture_output=True,text=True,timeout=1200)
out=open(os.path.join(D,'synth1.out')).read() if os.path.exists(os.path.join(D,'synth1.out')) else ''
print('rc',r.returncode,'out head:',out[:200])
# if parametrization: decode; try both conventions
m=re.match(r'\[\[1,80,1,\[\]\],\[(.*)\]\]$', out.strip().replace(' ',''))
if m:
    rest=m.group(1); depth=0;parts=[];cur=''
    for ch in rest:
        if ch=='[':depth+=1
        elif ch==']':depth-=1
        if ch==',' and depth==0:parts.append(cur);cur=''
        else:cur+=ch
    parts.append(cur)
    uw=parts[0];xlist=parts[1].strip('[]').split(',')
    w0=0
    for tm in uw.split('+'):
        if tm=='1': w0^=1
    # w0 is value making uw zero? evaluate properly
    def ev(pl,w):
        tot=0
        for tm in pl.split('+'):
            if tm=='1': tot^=1
            elif 'x0' in tm: tot^=w
        return tot
    w0=0 if ev(uw,0)==0 else 1
    def evx(pl):
        tot=0
        for tm in pl.split('+'):
            if tm=='1': tot^=1
            elif 'x0' in tm: tot^=w0
        return tot
    vals=[w0]+[evx(pl) for pl in xlist]
    print('vals bits:', ''.join(map(str,vals)))
    # note: replica convention x0 = LSB = last bit of msg; convert
    b=vals
    msg=bytes(int(''.join(str(b[7-k]) for k in range(8))[::-1][i] if False else ''.join(str(b[7-k]) for k in range(8)),2) for _ in [0])
    # simpler: int x with bit j = vals[j]; msg bytes = big-endian of x >> 0
    x=0
    for j,v in enumerate(vals):
        if v: x|=1<<j
    msg=x.to_bytes(10,'big')
    print('recovered msg1 (int conv):', msg)
    print('check:', check(vals, ct1))
