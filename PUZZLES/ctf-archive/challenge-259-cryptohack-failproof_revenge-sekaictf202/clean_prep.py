
import re, os, ast, hashlib
D = os.path.dirname(os.path.abspath(__file__))
keep = []
seen=set()
for x in re.findall(r'\d+', open(os.path.join(D,'keep_mid.txt')).readline()):
    p=int(x)
    if 1<=p<=512 and p not in seen: seen.add(p); keep.append(p)
assert len(keep)==504
with open(os.path.join(D,'rev_keep.txt'),'w') as f: f.write('KEEPV = ['+','.join(map(str,keep))+'];\n')
Kseen=set(); K=[]
for l in open(os.path.join(D,'K_mid.txt')):
    if not l.strip(): continue
    row=[int(x) for x in re.findall(r'-?\d+',l)]
    if len(row)!=504: continue
    t=tuple(row)
    if t not in Kseen: Kseen.add(t); K.append(row)
assert len(K)==248, len(K)
with open(os.path.join(D,'rev_K.txt'),'w') as f:
    for r in K: f.write('['+','.join(map(str,r))+']\n')
# m0 blocks (python idx) 1..5 from m0_mid2..6
for bi in range(1,6):
    m0=[int(x) for x in re.findall(r'-?\d+', open(os.path.join(D,f'm0_mid{bi+1}.txt')).readline())]
    assert len(m0)==504
    with open(os.path.join(D,f'rev_m0_b{bi}.txt'),'w') as f: f.write('['+','.join(map(str,m0))+']\n')
# toy instance under the SAME real A: fake flag 56 chars -> block bytes; c = A2*m0true
txt=open(os.path.join(D,'live_output.txt')).read().splitlines()
secret=bytes.fromhex(txt[0])
state=hashlib.sha512(secret).digest(); pub=[]
for _ in range(256):
    pub.append(int.from_bytes(state,'big')); state=hashlib.sha512(state).digest()
A=[[ (pub[j]>>(511-k))&1 for k in range(512)] for j in range(256)]
import random
random.seed(1337)
fake=b"SEKAI{toy_roundtrip_check_for_revenge_pipeline_do_not_submit}!!"[:56]
assert len(fake)==56 and all(32<=b<128 for b in fake)
lines=[]; m0lines=[]
for bi in range(7):
    mbytes = bytes(random.randrange(256) for _ in range(24)) + fake[8*bi:8*bi+8] + bytes(random.randrange(256) for _ in range(32))
    assert len(mbytes)==64
    bits=[ (mbytes[b]>>(7-k))&1 for b in range(64) for k in range(8) ]  # pos p=b*8+k+1
    m0true=[bits[p-1] for p in keep]
    c=[sum(A[j][keep[i]-1]*m0true[i] for i in range(504)) for j in range(256)]  # dropped bits are flag-MSBs = 0
    m0true=[int(x) for x in m0true]
    lines.append('c_ = ['+','.join(map(str,c))+'];\nm0p = '+str(m0true)+';\n')
    open(os.path.join(D,f'toy_b{bi}.gp'),'w').write('cc = ['+','.join(map(str,c))+'];\nm0p = '+str(m0true)+';\n')
open(os.path.join(D,'toy_expect.txt'),'w').write(fake.decode())
print('clean files written; toy fake flag:', fake.decode())
