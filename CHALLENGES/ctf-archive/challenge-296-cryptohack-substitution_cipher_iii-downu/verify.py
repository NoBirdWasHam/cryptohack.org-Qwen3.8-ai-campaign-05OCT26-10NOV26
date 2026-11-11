# Decode every synth solution candidate; check vs ct1/ct2 with conventions from .sage
import re, os
D = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(D,'synth_pub.txt')).read().split('\n')
pub,ct1,ct2 = t[0].strip(), t[1].strip(), t[2].strip()
s = pub[1:-1]; polys=[]; depth=0; cur=''
for ch in s:
    if ch=='(': depth+=1
    elif ch==')': depth-=1
    if ch==',' and depth==0: polys.append(cur); cur=''
    else: cur+=ch
polys.append(cur)
MON=[]
for p in polys:
    terms=[x.strip() for x in p.split('+') if x.strip()]
    MON.append([[] if tm=='1' else [int(tk[1:]) for tk in tm.split('*')] for tm in terms])

def check(bits, ct):
    bad=0
    for i,ms in enumerate(MON):
        v=0
        for m in ms:
            pr=1
            for x in m: pr &= bits[x]
            v^=pr
        if str(v)!=ct[i]: bad+=1
    return bad

def ascii_of(bits):
    # x_{8k+j} = bit(7-j) of char k  (MSB first)
    out=[]
    for k in range(10):
        c=0
        for j in range(8): c = (c<<1) | bits[8*k+j]
        out.append(c)
    return bytes(out)

# candidate 1: synth1gb.out linear GB
cand={}
try:
    body=open(os.path.join(D,'synth1gb.out')).read().split('#---')[2]
    d={int(a):1 if b else 0 for a,b in re.findall(r'1\*x(\d+)\^1(\+1)?', body)}
    if len(d)==80: cand['synth1gb']=[d[j] for j in range(80)]
except Exception as e: print('gb parse',e)

# candidate 2: synth1.out parametrization "[0, [2, 80, 1, [vars], [vals...]]]"
raw=open(os.path.join(D,'synth1.out')).read()
nums=re.findall(r'\[([01,\s]+)\]$', raw.strip().rstrip(']').strip().rstrip(']')+',')
m=re.search(r'\[\s*([01,\s]+)\s*\]\s*\]\s*\]', raw)
if m:
    vals=[int(x) for x in re.findall(r'[01]', m.group(1))]
    print('param tail length', len(vals))
    if len(vals)>=80: cand['synth1param']=vals[:80]

for name,bits in cand.items():
    print(name, 'bad vs ct1:', check(bits,ct1), ' bad vs ct2:', check(bits,ct2))
    a=ascii_of(bits)
    print('   bytes(ct1-order):', a, ' printable:', all(32<=c<127 for c in a))
    rev=bits[::-1]
    print('   reversed-var-order bytes:', ascii_of(rev), all(32<=c<127 for c in ascii_of(rev)))
