# Generate corrected Kannan-embedding GP scripts for blocks b0 (with prefix-RHS fix) and mid2.
import ast, os, hashlib
D = os.path.dirname(os.path.abspath(__file__))

def pv(s):
    s = s.strip()
    if s.startswith('Vecsmall('): s = s[len('Vecsmall('):].rstrip(')')
    if s.startswith('[') and s.endswith(']'): s = s[1:-1]
    return [int(x) for x in s.split(',')] if s.strip() else []

txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
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

NPDEF = ("nearestplane(B,t) = { local(mm,nn,bs,cs,tt,i,k,v,mu,q); mm=matsize(B)[1]; nn=matsize(B)[2]; "
         "bs=vector(mm); cs=vector(mm); "
         "for(i=1,mm, v=Vec(B[i,]); for(k=1,i-1, if(cs[k]==0, next()); "
         "mu=vecsum(vector(nn, j, B[i,j]*bs[k][j]))/cs[k]; "
         "if(mu!=0, v=v-mu*bs[k])); bs[i]=v; cs[i]=vecsum(vector(nn, j, v[j]*v[j]))); "
         "tt=Vec(t); forstep(i=mm,1,-1, if(cs[i]==0, next()); "
         "q=round(vecsum(vector(nn, j, tt[j]*bs[i][j]))/cs[i]); "
         "if(q!=0, tt=tt-q*Vec(B[i,]))); tt };")

TMPL = r'''
{
S = matsnf(A2, 1); U_ = S[1]; V_ = S[2]; DD = S[3];
cnz = vector(nb, i, sum(k=1,128, DD[k,i]^2));
nzcols = select(i -> cnz[i] != 0, [1..nb]);
Ucb = U_ * Mat(rhs~);
y = vector(#V_, i, 0);
for(j=1, #nzcols, jj = nzcols[j]; y[jj] = Ucb[j,1] / DD[j,jj]);
m0p = Vec((V_ * Mat(y~))[,1]);
maxres = vecmax(vector(128, j, abs(sum(k=1,nb, A2[j,k]*m0p[k]) - rhs[j])));
print("@@VAR@@ particular maxres=", maxres);
if(maxres!=0, error("particular solution failed"));
T0 = vector(nb, i, 1 - 2*m0p[i]);
B2 = matrix(d, nb, r, i, 2*K[r,i]);
Bred = qflllgram(B2*B2~, 1) * B2;
@@NP@@
Tred = nearestplane(Bred, T0);
print("@@VAR@@ Tred max:", vecmax(vector(#Tred, i, abs(Tred[i]))), " norm2=", vecsum(vector(#Tred, i, Tred[i]^2)));
rows = vector(d+1);
for(r=1,d, rows[r] = concat(Vec(Bred[r,]), [0]));
rows[d+1] = concat(Tred, [beta]);
M = matrix(d+1, nb+1, r, c, rows[r][c]);
Ml = qflllgram(M*M~, 1) * M;
G = Ml*Ml~;
bound = nb + beta*beta + 8;
NV = qfminim(G, bound, 2);
NV2 = NV[3];
print("@@VAR@@ qfminim N=", NV[1], " cands=", #NV2[1,]);
FIX = vector(256, i, -9);
@@FIXINIT@@
found = 0;
read(D_ "A.gp");
for(i=1, #NV2[1,],
  cf = NV2[,i];
  if(#cf == nb+1, pt = cf, pt = Vec(cf~ * Ml));
  if(abs(pt[nb+1]) != beta, next());
  if(pt[nb+1] < 0, for(j=1,nb+1, pt[j]=-pt[j]));
  vlat = vector(nb, j, T0[j]-pt[j]);
  bad = 0; for(j=1,nb, if(vlat[j]%2!=0, bad=1));
  if(bad, next());
  m = vector(nb, j, m0p[j] + vlat[j]/2);
  okb = 1; for(j=1,nb, if(m[j]!=0 && m[j]!=1, okb=0));
  if(!okb, next());
  bits = vector(256, i2, 0);
  for(j=1,nb, bits[KEEPV[j]] = m[j]);
  chk = 1;
  for(j=1,256, if(FIX[j]>=0 && bits[j]!=FIX[j], chk=0));
  if(!chk, next());
  for(j=1,128, if(sum(k=1,256, A[j,k]*bits[k]) != cc[j], chk=0));
  if(chk,
    seg = vector(32, j, sum(k=1,8, bits[(j-1)*8+k] * 2^(9-k)));
    write(D_ "SEG_@@VAR@@.txt", Str(seg));
    print("@@VAR@@ SOLVED seg=", seg);
    found = 1;));
if(!found, print("@@VAR@@ FAIL: no binary verified solution"));
}
'''

def gen(variant, blk, fixedbits, kfile=None):
    kfile = kfile or variant
    K = [pv(l) for l in open(os.path.join(D, f'K_{kfile}.txt')) if l.strip()]
    m0 = pv(open(os.path.join(D, f'm0_{kfile}.txt')).readline())
    keep = pv(open(os.path.join(D, f'keep_{kfile}.txt')).readline())
    d, n2 = len(K), len(keep)
    c = enc[blk]
    s = [sum(A[j][p-1]*fixedbits.get(p, 0) for p in range(1, 257)) for j in range(128)]
    rhs = [c[j] - s[j] for j in range(128)]
    err_raw = max(abs(sum(A[j][keep[i]-1]*m0[i] for i in range(n2)) - c[j]) for j in range(128))
    err_fix = max(abs(sum(A[j][keep[i]-1]*m0[i] for i in range(n2)) - rhs[j]) for j in range(128))
    Kchk = max(max(abs(sum(A[j][keep[i]-1]*K[r][i] for i in range(n2))) for j in (0, 37, 127)) for r in (0, d//2, d-1))
    print(f'{variant}: d={d} n2={n2} old-m0 maxerr vs raw c: {err_raw} | vs corrected rhs: {err_fix} | kernelcheck: {Kchk}')
    fixinit = ''.join(f'FIX[{p}]={b}; ' for p, b in sorted(fixedbits.items()))
    g = TMPL.replace('@@VAR@@', variant).replace('@@FIXINIT@@', fixinit).replace('@@NP@@', '')
    pre = ['default(parisize,"2G");', f'D_ = "{D.replace(chr(92), "/")}/";']
    def matrix_assign(name, rows):
        return f'{name} = [' + ';'.join(','.join(str(x) for x in r) for r in rows) + '];'
    pre.append(matrix_assign('A2', [[A[j][keep[i]-1] for i in range(n2)] for j in range(128)]))
    pre.append(matrix_assign('K', K))
    pre.append(NPDEF)
    pre.append(f'KEEPV = {gpvec(keep)};')
    pre.append(f'rhs = {gpvec(rhs)};')
    pre.append(f'cc = {gpvec(c)};')
    pre.append(f'beta = 1; nb = {n2}; d = {d};')
    body = g.strip()
    if body.startswith('{'): body = body[1:]
    if body.endswith('}'): body = body[:-1]
    body = ' '.join(body.split())
    script = '\n'.join(pre) + '\n' + f'runme() = {{ {body} }};\nrunme();\n'
    open(os.path.join(D, f'run321_{variant}.gp'), 'w', newline='\n').write(script)

pre_bits = {}
for i, ch in enumerate(b'crypto{'):
    for b in range(8): pre_bits[i*8 + b + 1] = (ch >> (7-b)) & 1
gen('b0', 0, pre_bits)
gen('b0free', 0, {}, 'mid2')
gen('mid2', 1, {})
print('wrote run321_b0.gp run321_b0free.gp run321_mid2.gp')
