# FINAL ATTACK: smithing_contest-ecsc_2024_it
# R := Q ; S := [Hm]G2 + Qid_admin ; r := e(C,G2) ; t := e(Q, 2*P_G2 - G2)/e(P_G1, Qid_admin)
import socket, json, re, hashlib, sys
import tower as T
T.discover()
P=T.P; N=T.N
HYP = int(sys.argv[1]) if len(sys.argv)>1 else 0   # 0=plain basis, 1=conjugated basis
CONJ = (T.f2sub if False else None)
def conj2(x):  # Frob_p on Fp2: a -> -1-a
    return T.f2sub((x[0]-x[1], T.F20 and ((x[0]-x[1])%P, (P-x[1])%P)), T.F20)
def conj2(x):
    # c0 + c1 a  ->  c0 + c1(-1-a) = (c0-c1) - c1 a
    return ((x[0]-x[1])%P, (P-x[1])%P)
def conj12(co):
    # co: list of 12 Fp2 coeffs of z; conjugate coeffs AND z->? conj on Fp12/Fp fixes Fp2?? no:
    # server-side model B = conjugate embedding ONLY on Fp2 coefficients (z^6=eps -> conj: z^6=conj(eps): different tower!)
    # For attack purposes: feed conjugated Fp2 points into model-A tower, serialize coeffs conjugated back. z fixed.
    return [conj2(c) for c in co]
CC = (lambda x: conj2(x)) if HYP else (lambda x: x)
CC12 = (lambda co: [conj2(c) for c in co]) if HYP else (lambda co: co)

Hm = lambda b: int.from_bytes(hashlib.sha256(b).digest()[:16], 'big') % N  # bytes=ceil(128/8)=16

def p2(s):
    s = re.sub(r'_delegated[\w^.\-]+','', str(s).replace(' ',''))
    m = re.match(r'^(\d+)\*a\+(\d+)$', s)
    if m: base=(int(m.group(2))%P, int(m.group(1))%P)
    else:
        m2 = re.match(r'^(\d+)$', s); base=(int(m2.group(1))%P, 0)
    return CC(base)
def s2(x):  # serialize Fp2 like sage prints: "c1*a + c0"  (apply hyp map on output)
    y = CC(x)  # conj is involution
    return f"{y[1]}*a + {y[0]}"

def s12(co):  # co: list 12 Fp2 coeffs in z -> sage-parseable string
    terms=[]
    for i,c in enumerate(co):
        if c==(0,0): continue
        cs = s2(c)
        if i==0: terms.append(f"({cs})")
        else: terms.append(f"({cs})*z^{i}")
    return " + ".join(terms)

def p12_to_list(co):  # tower f12 tuple ((a0,a1,a2),(b0,b1,b2)) -> [12] coeffs: z^{i}: a_i at 2i? basis: (a0+a1 w + a2 w^2) + z*(b0+b1 w+b2 w^2), w=z^2
    (a0,a1,a2),(b0,b1,b2)=co
    # w=z^2: a1 w = a1 z^2 ; a2 w^2 = a2 z^4 ; z*b_i w^j = b_i z^{1+2j}
    return [a0,b0,a1,b1,a2,b2]

s=socket.create_connection(("archive.cryptohack.org",25469),timeout=25)
f=s.makefile('rwb')
rl=lambda: f.readline().decode().strip()
sd=lambda l:(f.write((l+"\n").encode()), f.flush())
print('[1]', rl()[:50])
params=json.loads(rl())
rl()  # blank line after params
pg1_raw=params['P_G1']; Qraw=params['Q']; pg2_raw=params['P_G2']
uname="gtf42"
sd(uname)
rl()  # "thanks! here's your private key:"
du0r=json.loads(rl()); du1r=json.loads(rl())
PG1=(p2(str(pg1_raw[0])) if False else (pg1_raw[0]%P,pg1_raw[1]%P), )
PG1=(pg1_raw[0]%P, pg1_raw[1]%P)
Q=(Qraw[0]%P, Qraw[1]%P)
PG2=(p2(pg2_raw[0]), p2(pg2_raw[1]))
du0=(p2(du0r[0]), p2(du0r[1]))
print('[2] points parsed; G2 model:', T.G2X==p2("100774561144590475569157120930767342387*a + 218728496724280042701446122970647661523"))
G2=(T.G2X,T.G2Y)
print('[3] n*du0=O:', T.e2_mul(N,du0) is None, ' P_G2 oncurve:', T.e2_oncurve(PG2))
ok6 = None
for flip in (False, True):
    Qid_ad = T.H0('admin', flip); Qid_me = T.H0(uname, flip)
    print(f'[4] Qid_ad flip={flip}:', str(Qid_ad)[:50])
    print('[5] n*Qid_ad=O:', T.e2_mul(N,Qid_ad) is None)
    # consistency check (basis+h+sqrt): e(P_G1, du0) == e(Q, Qid_me) ?
    lhs = T.ate(PG1, du0)
    rhs = T.ate(Q, Qid_me)
    ok6 = T.f12eq(lhs, rhs)
    print(f'[6] pairing-consistency flip={flip}:', ok6)
    if ok6:
        break
if not ok6:
    print('ABORT: H0/pairing basis mismatch (both roots)'); sys.exit(2)
target = (f"I, the eternal Admin, keeper of all secrets, hereby decree that you, {uname}, "
          f"are worthy to glimpse my deepest and most ancient secret: the flag.")
Htarget = Hm(target.encode())
S = T.e2_add(T.e2_mul(Htarget, G2), Qid_ad)
print('[7] S oncurve:', T.e2_oncurve(S), ' n*S=O:', T.e2_mul(N,S) is None)
t1 = T.ate(Q, T.e2_add(T.e2_double(PG2), T.e2_neg(G2)))
t2 = T.ate(PG1, Qid_ad)
tco = p12_to_list(T.f12mul(t1, T.f12inv(t2)))
rco = None
sig = json.dumps([[Q[0], Q[1]], [s2(S[0]), s2(S[1])]])
print('[8] sig payload len:', len(sig))
sd(sig); sd(target); sd("admin")
C = None
for _ in range(6):
    cl = rl()
    print('[9] srv:', cl[:120])
    mm = re.search(r'C = (\[.*?\])', cl)
    if mm:
        C = json.loads(mm.group(1)); break
if C is None:
    print('ABORT: no C line'); sys.exit(3)
Cpt=(C[0]%P, C[1]%P)
rco = p12_to_list(T.ate(Cpt, G2))
tstr = s12(tco); rstr = s12(rco)
print('[10] t len', len(tstr), ' r len', len(rstr))
sd(json.dumps([tstr, rstr]))
verdict = None
for _ in range(8):
    try:
        ln = rl()
    except Exception as e:
        print('[11] read err', e); break
    if not ln: continue
    print('[11] srv:', ln[:300])
    if any(k in ln for k in ('ECSC{','yep','oh noes','went wrong')):
        verdict = ln; break
mf = re.search(r'ECSC\{[^}]*\}', verdict or '')
print('[12] FLAG:', mf.group(0) if mf else None)
s.close()
