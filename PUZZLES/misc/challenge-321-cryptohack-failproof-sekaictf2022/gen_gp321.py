# Generate corrected Kannan-embedding GP scripts for blocks b0 (with prefix-RHS fix) and mid2.
import ast, os, re, sys
D = os.path.dirname(os.path.abspath(__file__))

def pv(s):
    s = s.strip()
    if s.startswith('Vecsmall('): s = s[len('Vecsmall('):].rstrip(')')
    if s.startswith('[') and s.endswith(']'): s = s[1:-1]
    return [int(x) for x in s.split(',')] if s.strip() else []

txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
import hashlib
state = hashlib.sha256(secret).digest(); pub = []
for _ in range(128):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha256(state).digest()

A = []
raw = open(os.path.join(D, 'A.gp')).read()
body = raw[raw.index('[')+1: raw.rindex(']')]
for row in body.split(';'):
    row = row.strip()
    if row: A.append([int(x) for x in row.split(',')])
assert len(A) == 128 and all(len(r) == 256 for r in A)

def gpvec(v): return '[' + ','.join(str(x) for x in v) + ']'

def gen(variant, blk, fixedbits):
    # fixedbits: dict pos(1..256)->bit for positions that are KNOWN (not in keep)
    K = [pv(l) for l in open(os.path.join(D, f'K_{variant}.txt')) if l.strip()]
    m0 = pv(open(os.path.join(D, f'm0_{variant}.txt')).readline())
    keep = pv(open(os.path.join(D, f'keep_{variant}.txt')).readline())
    d, n2 = len(K), len(keep)
    c = enc[blk]
    # RHS correction: true keep-part satisfies A2 x = c - s, s from fixed bits
    s = [sum(A[j][p-1]*fixedbits.get(p, 0) for p in range(1, 257)) for j in range(128)]
    rhs = [c[j] - s[j] for j in range(128)]
    # consistency checks on old prep
    err_raw = [abs(sum(A[j][keep[i]-1]*m0[i] for i in range(n2)) - c[j]) for j in range(128)]
    err_fix = [abs(sum(A[j][keep[i]-1]*m0[i] for i in range(n2)) - rhs[j]) for j in range(128)]
    Kchk = max(max(abs(sum(A[j][keep[i]-1]*K[r][i] for i in range(n2))) for j in (0, 37, 127)) for r in (0, d//2, d-1))
    print(f'{variant}: d={d} n2={n2} maxerr old-m0 vs raw c: {max(err_raw)} | vs corrected rhs: {max(err_fix)} | kernelcheck(3 rows x 3 eq): {Kchk}')
    gp = []
    gp.append('default(parisize,"2G");')
    # A2 as 128 x n2 rows
    cols = ';\n'.join(gpvec([A[j][keep[i]-1] for i in range(n2)]) for j in range(128))
    gp.append(f'A2 = [\n{cols}\n];')
    gp.append(f'K = [\n' + ';\n'.join(gpvec(r) for r in K) + '\n];')
    gp.append(f'rhs = {gpvec(rhs)};')
    gp.append(f'cc = {gpvec(c)};')
    gp.append(f'beta = 23; nb = {n2};')
    gp.append(f'''
S = matsnf(A2, 1); U_ = S[1]; V_ = S[2]; D_ = S[3];
rk = 0; for(i=1,128, if(D_[i,i]!=0, rk=i));
Ucb = U_ * Mat(rhs);
y = vector(#V_, i, 0);
for(i=1, rk, y[i] = Ucb[i,1] / D_[i,i]);
m0p = Vec(V_ * Mat(y));
maxres = vecmax(vector(128, j, abs(sum(k=1,nb, A2[j,k]*m0p[k]) - rhs[j])));
print("{variant} particular maxres=", maxres);
if(maxres!=0, error("particular solution failed"));
T0 = vector(nb, i, 1 - 2*m0p[i]);
B2 = Mat(vector(d, r, vector(nb, i, 2*K[r,i])));
Bred = qflll(B2~)~;
nearestplane(B, t) = {{
  local(m,n,bs,cs,tt,i,k,v,mu,q);
  m=matsize(B)[1]; n=matsize(B)[2];
  bs=vector(m); cs=vector(m);
  for(i=1,m,
    v=Vec(B[i,]);
    for(k=1,i-1,
      if(cs[k]==0, next());
      mu=(Vec(B[i,])~*bs[k])/cs[k];
      if(mu!=0, v=v-mu*bs[k]));
    bs[i]=v; cs[i]=v~*v);
  tt=Vec(t);
  forstep(i=m,1,-1,
    if(cs[i]==0, next());
    q=round((tt~*bs[i])/cs[i]);
    if(q!=0, tt=tt-q*Vec(B[i,])));
  tt
}};
Tred = nearestplane(Bred, T0);
print("{variant} Tred max|T|:", vecmax(vector(#Tred, i, abs(Tred[i]))), " norm2=", Tred~*Tred);
rows = vector(d+1);
for(r=1,d, rows[r] = concat(Vec(Bred[r,]), [0]));
rows[d+1] = concat(Tred, [beta]);
M = Mat(rows);
Ml = qflll(M~, [0.999])~;
G = Ml*Ml~;
bound = nb + beta*beta;
N = qfminim(G, bound, 1);
print("{variant} qfminim N=", #N[2,]);
found = 0;
for(i=1, #N[2,],
  w = Vec(N[2,i]);
  if(abs(w[nb+1]) != beta, next());
  if(w[nb+1] < 0, for(j=1,nb+1, w[j]=-w[j]));
  wf = vector(nb, j, w[j]);
  vlat = vector(nb, j, Tred[j]-wf[j]);
  bad = 0; for(j=1,nb, if(vlat[j]%2!=0, bad=1));
  if(bad, next());
  m = vector(nb, j, m0p[j] + vlat[j]\2);
  okb = 1; for(j=1,nb, if(m[j]!=0 && m[j]!=1, okb=0));
  if(!okb, next());
  bits = vector(256, i, 0);
  for(j=1,nb, bits[keep[j]] = m[j]);
  FIXEDBITS_PLACEHOLDER
  val = 0; for(j=1,256, val = val*2 + bits[j]);
  chk = 1; for(j=1,128, t2 = 0; for(k=1,256, if(A_[j,k]==1 && bits[k]==1, t2++)); if(t2 != cc[j], chk=0));
  if(chk,
    seg = vector(32, j, frombinary(bitsub(val, (32-j)*8, 8)));
    write(D_ "SEG_{variant}.txt", Str(seg));
    print("{variant} SOLVED seg=", seg);
    found = 1;));
if(!found, print("{variant} FAIL: no binary verified solution"));
''')
    A_full = ';\n'.join(gpvec(r) for r in A)
    fb = 'FIX = vector(256, i, 0);\n  ' + ''.join(f'FIX[{p}]={b}; ' for p, b in sorted(fixedbits.items())) + 'for(j=1,256, if(FIX[j]!=-9, if(bits[j]!=FIX[j], next)));'
    fb = 'FIX = vector(256, i, -9);\n  ' + ''.join(f'FIX[{p}]={b}; ' for p, b in sorted(fixedbits.items())) + '\n  for(j=1,256, if(FIX[j]>=0 && bits[j]!=FIX[j], chk=0));'
    g = '\n'.join(gp).replace('FIXEDBITS_PLACEHOLDER', fb).replace('A_', 'A')
    g = f'D_ "{D}/";\n' + g.replace('{variant}', variant)
    open(os.path.join(D, f'run321_{variant}.gp'), 'w').write(g)

pre = {}
for i, ch in enumerate(b'crypto{'):
    for b in range(8): pre[i*8 + b + 1] = (ch >> (7-b)) & 1
gen('b0', 0, pre)
gen('mid2', 1, {})
print('wrote run321_b0.gp run321_mid2.gp')
