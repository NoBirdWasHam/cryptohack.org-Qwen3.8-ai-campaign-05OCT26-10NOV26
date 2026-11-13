# Smithing contest forge. Conn1: signer oracle => A=e([x]P_G1,P_G2), B=e(C_A,du1).
# Conn2: verifier => C_B; local: e(C_B,du1)=B^{y2/y1}; r=B_f^{x*invHm*y2}; t=A.
import socket, json, re, hashlib
import tower as T
T.discover()

P = T.P; N = T.N
HOST, PORT = "archive.cryptohack.org", 25469
H = lambda b: int.from_bytes(hashlib.sha256(b).digest()[:33], "big") % N

def conn():
    s = socket.create_connection((HOST, PORT), timeout=25)
    f = s.makefile('rwb')
    return s, f
def rl(f):
    l = f.readline().decode().strip()
    if l == '': raise RuntimeError('server closed')
    return l
def sd(f, l):
    f.write((l + "\n").encode()); f.flush()

def parse_int(s):
    s = str(s).strip()
    m = re.match(r'^(-)?(0x[0-9a-fA-F]+|\d+)'); v = int(m.group(2), 16) if m.group(2).startswith('0x') else int(m.group(2))
    return -v if m.group(1) else v

def parse_fp2(s):
    s = re.sub(r'_delegated[\w^.\-]+', '', str(s).replace(' ', ''))
    toks = re.split(r'([+-])', s); c0 = c1 = 0; sign = 1 if not s.startswith('-') else -1
    s = s.lstrip('+-')
    for tk in toks:
        if tk in ('', '+'):
            if tk == '+': sign = 1
            continue
        if tk == '-': sign = -1; continue
        if 'a' in tk:
            coef = tk.split('*a')[0]
            v = parse_int(coef) if coef not in ('', '+', '-') else 1
            c1 += sign * v
        else:
            c0 += sign * parse_int(tk)
    return (c0 % P, c1 % P)

def parse_fp12(s):
    s = re.sub(r'_delegated[\w^.\-]+', '', str(s)).replace(' ', '')
    parts = []; depth = 0; cur = ''; sign = '+'
    for ch in s:
        if ch == '(': depth += 1; cur += ch
        elif ch == ')': depth -= 1; cur += ch
        elif ch in '+-' and depth == 0 and cur:
            parts.append((sign, cur)); sign = ch; cur = ''
        else: cur += ch
    if cur: parts.append((sign, cur))
    co = [T.F20] * 12
    for sgn, term in parts:
        if not term: continue
        s2 = term[1:] if (term[0] in '+-' and term != '+z' and term != '-z') else term
        sgn2 = term[0] if term[0] in '+-' else '+'
        if '*z^' in s2: cl, pw = s2.split('*z^'); pw = int(pw)
        elif s2.endswith('*z'): cl, pw = s2[:-2], 1
        elif s2 == 'z': cl, pw = '1', 1
        elif 'z^' in s2: cl, pw = s2.split('z^'); pw = int(pw)
        else: cl, pw = s2, 0
        c = parse_fp2(cl) if cl not in ('', '+', '-') else (1, 0)
        if sgn2 == '-': c = T.f2neg(c)
        co[pw] = T.f2add(co[pw], c)
    return co

def ser_fp2(x): return f"{x[1]}*a + {x[0]}"
def ser_fp12(co):
    terms = []
    for i, cc in enumerate(co):
        if cc == (0, 0): continue
        if i == 0: terms.append(ser_fp2(cc))
        elif i == 1: terms.append(f"({ser_fp2(cc)})*z")
        else: terms.append(f"({ser_fp2(cc)})*z^{i}")
    return ' + '.join(terms) if terms else '0'
def f12pow(co, e):
    r = [T.F21] + [T.F20] * 11
    for bit in bin(e)[2:]:
        r = T.f12mul(r, r)
        if bit == '1': r = T.f12mul(r, co)
    return r
def f12is1(co): return co[0] == (1, 0) and all(c == (0, 0) for c in co[1:])

def fp_add(A, B):
    if A is None: return B
    if B is None: return A
    x1, y1 = A; x2, y2 = B
    if x1 == x2:
        if (y1 + y2) % P == 0: return None
        lam = 3 * x1 * x1 * pow(2 * y1, P - 2, P) % P
    else:
        lam = (y2 - y1) * pow(x2 - x1, P - 2, P) % P
    x3 = (lam * lam - x1 - x2) % P
    return (x3, (lam * (x1 - x3) - y1) % P)
def fp_mul(k, Q):
    R = None
    for b in bin(k)[2:]:
        R = fp_add(R, R)
        if b == '1': R = fp_add(R, Q)
    return R

G2 = (T.G2X, T.G2Y)
def dummy_sig(R): return json.dumps([[R[0], R[1]], [ser_fp2(G2[0]), ser_fp2(G2[1])]])

UNAME = "gtfanon42"
x = H(b"session-x") % N
if x == 0: x = 1
mA = b"dummy-sign-me"

# ---------- conn 1: signer oracle ----------
s1, f1 = conn()
rl(f1); params = json.loads(rl(f1))
pg1 = tuple(params['P_G1']); Q = tuple(params['Q'])
sd(f1, UNAME)
du0 = json.loads(rl(f1)); du1 = json.loads(rl(f1))
print('[c1] params/keys in')
R = fp_add(fp_mul(x, pg1), (Q[0], (-Q[1]) % P))
assert R is not None and (R[0]**3 + 11 - R[1]**2) % P == 0
sd(f1, dummy_sig(R)); sd(f1, mA.decode()); sd(f1, UNAME)
CA = tuple(json.loads(rl(f1)[4:]))
sd(f1, dummy_sig(R)); sd(f1, mA.decode()); sd(f1, UNAME)
tr = json.loads(rl(f1))
tstr, rstr = tr
print('[c1] t fmt:', tstr[:60]); print('[c1] r fmt:', rstr[:60])
Aco = parse_fp12(tstr); Bco = parse_fp12(rstr)
s1.close()
print('[c1] done. A,B parsed; A==1?', f12is1(Aco), 'B==1?', f12is1(Bco))

# ---------- conn 2: verifier + forge ----------
s2, f2 = conn()
rl(f2); p2 = json.loads(rl(f2))
assert [int(v) for v in p2['P_G1']] == list(pg1)
sd(f2, UNAME)
du0b = json.loads(rl(f2)); du1b = json.loads(rl(f2))
print('[c2] keys in (same?) du1 same as before:', du1b == du1)
target = (f"I, the eternal Admin, keeper of all secrets, hereby decree that you, {UNAME}, "
          f"are worthy to glimpse my deepest and most ancient secret: the flag.")
sd(f2, dummy_sig(R)); sd(f2, target); sd(f2, "admin")
CB = tuple(json.loads(rl(f2)[4:]))
# recover y1,y2 from C=xy*R (R order n prime, known)
Rx, Ry = R
def dl_R(Cpt):
    # baby-step giant-step over order n
    import math
    m = math.isqrt(N) + 1
    table = {}
    Pp = (0,0)
    cur = None
    for j in range(m):
        if j: cur = fp_add(cur, R)
        else: cur = None
        if cur is None: table[None] = j; continue
        if cur not in table: table[cur] = j
    fmulR = fp_mul(m, R)
    gamma = Cpt
    for i in range(m + 1):
        if gamma in table: return i * m + table[gamma]
        gamma = fp_add(gamma, fp_neg(fmulR))
    return None
def fp_neg(Qq): return None if Qq is None else (Qq[0], (-Qq[1]) % P)
vA = dl_R(CA); vB = dl_R(CB)
print('[c2] x*y1 =', vA, ' x*y2 =', vB)
y2 = (vB * pow(vA, -1, N)) % N   # y2/y1 (x cancels!)
Hm = H(target.encode())
expB = y2
Bf = f12pow(Bco, expB)           # e(C_B, du1)
expR = (x * pow(Hm, -1, N) * y2) % N
r = f12pow(Bf, expR)             # e(C_B,du1)^{x/(Hm*y2inv)}... = ^{x*invHm*y2}
rstr_f = ser_fp12(r)
print('[c2] forged r len:', len(rstr_f))
sd(f2, json.dumps([tstr, rstr_f]))
out = rl(f2); print('[c2] SERVER:', out)
s2.close()
