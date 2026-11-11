# Generate msolve input files from output.txt
import os, re
D=os.path.dirname(os.path.abspath(__file__))
t=open(os.path.join(D,'output.txt')).read().split('\n')
pub,ct1,ct2=t[0].strip(),t[1].strip(),t[2].strip()
s=pub[1:-1]; polys=[];depth=0;cur=''
for ch in s:
    if ch=='(':depth+=1
    elif ch==')':depth-=1
    if ch==',' and depth==0: polys.append(cur);cur=''
    else: cur+=ch
polys.append(cur)
polys=[re.sub(r'x(\d+)', lambda m:'x%d'%int(m.group(1)), p.strip()) for p in polys]

def gen(path, ct, nun):
    # free vars x0..x(nun-1); x(nun..79)=0 padding; drop polys that become const 1 (unsat-free: means 0=1 -> skip? keep as '1')
    lines=[str(max(nun,1))]
    keep=0
    for i,p in enumerate(polys):
        terms=p.split('+'); newt=[]
        for tm in terms:
            tm=tm.strip()
            if not tm: continue
            vs=[] if tm=='1' else [int(tk[1:]) for tk in tm.split('*')]
            if any(v>=nun for v in vs): continue
            newt.append(tm)
        if ct[i]=='1': newt.append('1')
        from collections import Counter
        c=Counter(newt); k=[x for x,v in c.items() if v%2==1]
        if not k: continue
        if k==['1']: continue  # would be 1=0; skip (shouldn't happen)
        lines.append('+'.join(k)); keep+=1
    # Boolean field equations x^2+x for free vars
    for v in range(nun):
        lines.append(f'x{v}^2+x{v}')
    open(path,'w').write('\n'.join(lines)+'\n')

os.makedirs(os.path.join(D,'ms'),exist_ok=True)
for b in range(5,11):
    gen(os.path.join(D,'ms',f'msg2_b{b}.in'), ct2, 8*b)
gen(os.path.join(D,'ms','msg1_full.in'), ct1, 80)
print('ok')
