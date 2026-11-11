# Smithing contest (ECSC 2024 IT) attacker.
# Attack: blind-verification forgery. Send R = Q (G1 master pub), S = dad*Qid_ad + (sg*b)*H(m)*Qid_me,
# answer C with r = e(C, b*Qid_me), t = e(2Q, sg*P_G2) * e(P_G1, sg*dad*Qid_ad)^-1 * e(Q, b*Qid_me)^-1.
# x,y cancel exactly. Enumerate sign conventions (sg, dad, b) in {+-1}^3; server 'oh noes' = oracle.
import socket, json, re, sys, time
from tower import *

HOST, PORT = 'archive.cryptohack.org', 25469
UNAME = 'smithy'
TARGET = ('I, the eternal Admin, keeper of all secrets, hereby decree that you, %s, '
          'are worthy to glimpse my deepest and most ancient secret: the flag.' % UNAME)

def parse_f2(s):
    s = str(s).replace(' ', '')
    if '*a' in s:
        m = re.fullmatch(r'(\d+)\*a\+?(\d*)', s)
        if m:
            c1 = int(m.group(1)); c0 = int(m.group(2)) if m.group(2) else 0
            return (c0 % P, c1 % P)
        m = re.fullmatch(r'\+?(\d+)\*a-(\d+)', s)   # "c1*a - c0" just in case
        if m: return ((P - int(m.group(2))) % P, int(m.group(1)) % P)
        raise ValueError('f2 parse: ' + s)
    return (int(s) % P, 0)

def fmt_f2(c): return '%d * a + %d' % (c[1] % P, c[0] % P)

def fmt_f12(x):
    b = f12_basis(x)
    parts = []
    for d, c in enumerate(b):
        cf = '(%d * a + %d)' % (c[1] % P, c[0] % P)
        if d == 0: parts.append(cf)
        elif d == 1: parts.append(cf + ' * z')
        else: parts.append(cf + ' * z^%d' % d)
    return ' + '.join(parts)

class LineIO:
    def __init__(s, sock): s.f = sock.makefile('rwb'); s.buf = b''
    def readline(s):
        line = s.f.readline()
        if not line: raise EOFError('server closed')
        sys.stdout.write('S> ' + line.decode(errors='replace'))
        sys.stdout.flush()
        return line.decode(errors='replace')
    def sendline(s, txt):
        sys.stdout.write('C< ' + txt[:120] + ('...' if len(txt) > 120 else '') + '\n'); sys.stdout.flush()
        s.f.write((txt + '\n').encode()); s.f.flush()

def e1_from_pt(P1):  # (x,y) tuple or None
    return P1

def attempt(sg, dad, b, g2pair, gad, qm, Q, P_G2, Qid_ad, Qid_me, H):
    t0 = time.time()
    # S = dad*Qid_ad + (sg*b)*H*Qid_me
    S = e2_add(e2_mul(dad, Qid_ad) if dad == 1 else e2_neg(Qid_ad) if False else e2_mul(1, Qid_ad), None)
    A = Qid_ad if dad == 1 else e2_neg(Qid_ad)
    Bc = e2_mul(H % N, Qid_me)
    if sg * b < 0: Bc = e2_neg(Bc)
    S = e2_add(A, Bc)
    assert S is not None and e2_mul(N, S) is None, 'S bad'
    sock = socket.create_connection((HOST, PORT), timeout=90)
    io = LineIO(sock)
    io.readline()  # ### broadcasting...
    line = io.readline()
    params = json.loads(line)
    P_G1s = (params['P_G1'][0] % P, params['P_G1'][1] % P)
    Qs = (params['Q'][0] % P, params['Q'][1] % P)
    P_G2s = (parse_f2(params['P_G2'][0]), parse_f2(params['P_G2'][1]))
    if Qs != Q or P_G2s != P_G2 or P_G1s != G1:
        print('!! params mismatch', Qs == Q, P_G2s == P_G2, P_G1s == G1)
    io.sendline(UNAME)
    io.readline()  # thanks
    io.readline(); io.readline()  # sk0 sk1 jsons
    sig = json.dumps([[Q[0], Q[1]], [fmt_f2(S[0]), fmt_f2(S[1])]])
    io.sendline(sig)
    io.sendline(TARGET)
    io.sendline('admin')
    line = io.readline()  # C = [...]
    Cxy = json.loads(line.split('C = ', 1)[1])
    Cpt = (Cxy[0] % P, Cxy[1] % P)
    # r = e(C, b*Qid_me)
    r = ate(Cpt, Qid_me if b == 1 else e2_neg(Qid_me))
    # t = e(2Q, sg*P_G2) * e(P_G1, sg*dad*Qid_ad)^-1 * qm^-1   (qm = e(Q,Qid_me))
    t = f12_pow(g2pair, sg)
    t = f12mul(t, f12inv(f12_pow(gad, sg * dad)))
    t = f12mul(t, f12inv(qm))
    if not f12eq(f12_pow(r, N), F121) or not f12eq(f12_pow(t, N), F121):
        print('!! t,r not in mu_n')
    if f12eq(r, F121) or f12eq(t, F121):
        print('!! t or r == 1'); return None
    io.sendline(json.dumps([fmt_f12(t), fmt_f12(r)]))
    res = io.readline()
    try: sock.close()
    except Exception: pass
    print('attempt sg=%d dad=%d b=%d -> %r (%.1fs)' % (sg, dad, b, res, time.time() - t0))
    return res

def main():
    discover()
    frob_setup()
    Qid_ad = H0('admin')
    Qid_me = H0(UNAME)
    Q = e1_mul(1, (G2X, G2Y)) if False else None
    print('precomputing pairings...', flush=True)
    t0 = time.time()
    Qpt = None  # Q unknown as dlog; but Q point itself is NOT in params broadcast? it is: params['Q']
    # Q point is public: need it before connecting for precompute -> use fixed known: Q = s*P_G1 unknown s,
    # but the POINT Q must come from server. For precompute we still need its coordinates...
    print('need Q from server first; do precompute after first handshake')
    print('H0 done %.1fs' % (time.time() - t0), flush=True)

if __name__ == '__main__':
    main()
