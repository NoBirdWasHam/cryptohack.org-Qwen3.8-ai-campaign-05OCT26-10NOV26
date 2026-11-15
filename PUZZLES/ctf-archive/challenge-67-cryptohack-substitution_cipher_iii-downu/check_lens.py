import re
body=open('synth1gb.out').read().split('#---')[2]
entries=re.findall(r'1\*x(\d+)\^1(\+1)?', body)
vals={int(a):1 if b else 0 for a,b in entries}
bits=[vals[j] for j in range(80)]
def ev(p):
    v=0
    for tm in p.split('+'):
        tm=tm.strip()
        if tm=='1': v^=1; continue
        prod=1
        for tk in tm.split('*'): prod&=bits[int(tk[1:])]
        v^=prod
    return v
s=open('synth_pub.txt').read().split('\n'); ct1=s[1]
ss=s[0][1:-1];depth=0;polys=[];cur=''
for ch in ss:
    if ch=='(':depth+=1
    elif ch==')':depth-=1
    if ch==',' and depth==0:polys.append(cur);cur=''
    else:cur+=ch
polys.append(cur)
nb=[];no=[]
for i,p in enumerate(polys):
    full=p+('+1' if ct1[i]=='1' else '')
    ok = (str(ev(full))=='0')
    (nb if not ok else no).append((len(full),full.count('*')))
print('BAD count',len(nb))
print('BAD sorted:', sorted(nb)[:4], sorted(nb)[-4:])
print('OK len range:', min(x[0] for x in no), max(x[0] for x in no))
print('OK nterm range:', min(x[1] for x in no), max(x[1] for x in no))
