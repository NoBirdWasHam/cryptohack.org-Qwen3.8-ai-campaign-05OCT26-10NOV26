# MQ solve helper: build msolve input with CORRECT ASCII constraint (x_{8k}=0),
# run msolve, parse rational parametrization via literal_eval, decode, verify vs ct.
import os, re, ast, subprocess, sys
D=os.path.dirname(os.path.abspath(__file__))
MS=r'~/tools/msolvedir/ucrt64/bin/msolve.exe'

def load_instance(path):
    t=open(path).read().split('\n')
    pub,ct1,ct2=t[0].strip(),t[1].strip(),t[2].strip()
    s=pub[1:-1];polys=[];depth=0;cur=''
    for ch in s:
        if ch=='(':depth+=1
        elif ch==')':depth-=1
        if ch==',' and depth==0:polys.append(cur);cur=''
        else:cur+=ch
    polys.append(cur)
    MON=[]
    for p in polys:
        terms=[x.strip() for x in p.split('+') if x.strip()]
        MON.append([[] if tm=='1' else [int(tk[1:]) for tk in tm.split('*')] for tm in terms])
    return MON,ct1,ct2

def eval_mon(bits,mon):
    v=0
    for m in mon:
        pr=1
        for x in m: pr&=bits[x]
        v^=pr
    return v

def check(MON,bits,ct):
    return sum(1 for i,mon in enumerate(MON) if str(eval_mon(bits,mon))!=ct[i])

def build_input(MON,ct,fixed,out):
    # fixed: set of var indices forced to 0 (ASCII MSBs). free vars keep original names x_j
    free=[j for j in range(80) if j not in fixed]
    lines=[','.join('x%d'%j for j in free),'2']
    pols=[]
    for i,mon in enumerate(MON):
        terms={}
        for m in mon:
            if any(v in fixed for v in m): continue
            key='x%d'%m[0] if m else '1'
            if len(m)==2: key='x%d*x%d'%(m[0],m[1])
            terms[key]=terms.get(key,0)^1
        if ct[i]=='1': terms['1']=terms.get('1',0)^1
        ks=[k for k,v in terms.items() if v]
        if not ks or ks==['1']: continue   # empty(=0) drop; '1'= 1+0 = 0=1?? '1' alone means poly==1 -> unsat
        if ks==['1']:
            open(out,'w').write(varsline(free)+'\n2\n1\n'); return None
        pols.append('+'.join(ks))
    pols+=['x%d^2+x%d'%(j,j) for j in free]
    open(out,'w').write(varsline(free)+'\n2\n'+',\n'.join(pols)+'\n')
    return free
def varsline(free): return ','.join('x%d'%j for j in free)

def run_ms(inp,out,thr=2,tmo=None,verbose=1):
    r=subprocess.run([MS,'-f',inp,'-o',out,'-t',str(thr),'-v',str(verbose)],capture_output=True,text=True,timeout=tmo)
    return r

def parse_param(outpath,free):
    raw=open(outpath).read().strip()
    if not raw: return None,'EMPTY'
    if raw.startswith('[-1]'): return None,'UNSAT'
    if raw.startswith('[1,'): return None,'INFINITE'
    lit=raw[:-1] if raw.endswith(':') else raw
    try:
        obj=ast.literal_eval(lit.replace(' ',''))
    except Exception as e:
        return None,'PARSEFAIL %s: %s'%(e,lit[:120])
    # obj = [0, [2, nvars, N, [varnames], ...stuff]]  explore: find list of 80-ish per-var sparse items
    def find_vallist(o):
        if isinstance(o,list):
            if len(o)>=len(free) and all(isinstance(x,list) and all(isinstance(y,list) and len(y)==2 and isinstance(y[0],int) and isinstance(y[1],list) and all(isinstance(z,int) for z in y[1]) for y in x) for x in o[:3]):
                return o
            for x in o:
                r=find_vallist(x)
                if r is not None: return r
        return None
    vl=find_vallist(obj)
    if vl is None: return ('OBJ',obj),'STRUCT'
    # find univariate poly: a list of ints that is NOT varnames list
    def find_uw(o):
        if isinstance(o,list) and o and all(isinstance(x,int) for x in o):
            return o
        if isinstance(o,list):
            for x in o:
                r=find_uw(x)
                if r is not None and len(r)>1: return r
        return None
    uw=find_uw(obj)
    # roots of uw in GF2: uw is coeffs list? try both orientations later; assume coeffs list index=exp
    def uroot(ue):
        for w in (0,1):
            v=0
            for c,e in ue: v^=(c%2)&(w if e>0 else 1)
            if v==0: return w
        return 0
    # msolve prints univariate as [[c,[exp]],...] maybe; find that
    def find_uw2(o):
        if isinstance(o,list) and len(o)>=2 and all(isinstance(y,list) and len(y)==2 and isinstance(y[0],int) and isinstance(y[1],list) for y in o):
            return o
        if isinstance(o,list):
            for x in o:
                r=find_uw2(x)
                if r is not None: return r
        return None
    w0=0
    # value of each var: sum c*w^e over its terms
    def val(terms):
        tot=0
        for c,es in terms:
            for e in es:
                tot^=(c%2)&(w0 if e>0 else 1)
        return tot&1
    if len(free)==1:
        return [val(vl[0]) if vl else 0],'ONE'
    vals=[val(t) for t in vl[:len(free)]]
    return vals,'OK'

def decode_ascii(bits80):
    out=[]
    for k in range(10):
        c=0
        for j in range(8): c=(c<<1)|bits80[8*k+j]
        out.append(c)
    return bytes(out)
