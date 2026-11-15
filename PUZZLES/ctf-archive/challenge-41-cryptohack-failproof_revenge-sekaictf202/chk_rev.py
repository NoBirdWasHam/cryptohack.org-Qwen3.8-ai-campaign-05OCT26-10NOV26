import ast, hashlib, os, sys
D = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(D,'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha512(secret).digest(); pub=[]
for _ in range(256):
    pub.append(int.from_bytes(state,'big')); state=hashlib.sha512(state).digest()
A = [[(pub[j]>>(511-k))&1 for k in range(512)] for j in range(256)]
import re
keep_raw = [int(x) for x in re.findall(r'\d+', open(os.path.join(D,'keep_mid.txt')).readline())]
seen=set(); keep=[p for p in keep_raw if 1<=p<=512 and not (p in seen or seen.add(p))]
skip_expected = set(8*b+1 for b in range(24,32))
print('len keep', len(keep), 'excluded ok', set(range(1,513))-set(keep)==skip_expected)
Kseen=set(); K=[]
for l in open(os.path.join(D,'K_mid.txt')):
    if not l.strip(): continue
    row = [int(x) for x in re.findall(r'-?\d+', l)]
    t = tuple(row)
    if t not in Kseen: Kseen.add(t); K.append(row)
print('K dims', len(K), len(K[0]))
A2 = [[A[j][p-1] for p in keep] for j in range(256)]
bad=0
for r in list(range(0,len(K),53))+[len(K)-1]:
    for j in (0,37,91,127,200,255):
        if sum(A2[j][i]*K[r][i] for i in range(len(keep)))!=0: bad+=1
print('kernel check bad:', bad)
for bi in range(len(enc)):
    fn = os.path.join(D, f'm0_mid{bi+1}.txt')
    if not os.path.exists(fn):
        print(f'block {bi}: m0 MISSING'); continue
    m0 = [int(x) for x in re.findall(r'-?\d+', open(fn).readline())]
    err = max(abs(sum(A2[j][i]*m0[i] for i in range(len(keep))) - enc[bi][j]) for j in (0,1,63,127,199,255))
    errfull = max(abs(sum(A2[j][i]*m0[i] for i in range(len(keep))) - enc[bi][j]) for j in range(256)) if err==0 else None
    print(f'block {bi}: m0 len {len(m0)} maxerr-sample {err} maxerr-full {errfull}')
print('K row norm2 max/first20', max(sum(x*x for x in row) for row in K[:20]))
