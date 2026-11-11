# Smithing contest (ECSC 2024 IT) attacker.
# Forgery: R = Q (G1 master pub, dlog unknown -- not needed). S = dad*Qid_ad + (sg*b)*H(m)*Qid_me.
# Answer C with r = e(C, b*Qid_me); t = e(2Q, sg*P_G2) * e(P_G1, sg*dad*Qid_ad)^-1 * e(Q, b*Qid_me)^-1.
# (server-side x,y cancel; sg = pairing-convention sign, dad = server H0('admin') sign: enumerate +-1).
import socket, json, re, sys, time, threading
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
            return (int(m.group(2)) % P if m.group(2) else 0, int(m.group(1)) % P)
        m = re.fullmatch(r'\+?(\d+)\*a-(\d+)', s)
        if m: return ((P - int(m.group(2))) % P, int(m.group(1)) % P)
        raise ValueError('f2 parse: ' + s)
    return (int(s) % P, 0)

def fmt_f2(c): return '%d * a + %d' % (c[1] % P, c[0] % P)

def fmt_f12(x):
    b = f12_basis(x)
    parts = []
    for d, c in enumerate(b):
        cf = '(%d * a + %d)' % (c[1] % P, c[0] % P)
        parts.append(cf if d == 0 else (cf + ' * z' if d == 1 else cf + ' * z^%d' % d))
    return ' + '.join(parts)

class LineIO:
    def __init__(s, sock): s.f = sock.makefile('rwb')
    def readline(s, tag=''):
        line = s.f.readline()
        if not line: raise EOFError('server closed')
        txt = line.decode(errors='replace').rstrip('\r\n')
        sys.stdout.write('S>%s %s\n' % (tag, txt if len(txt) < 300 else txt[:300] + '...'))
        sys.stdout.flush()
        return txt
    def sendline(s, txt, tag=''):
        sys.stdout.write('C<%s %s\n' % (tag, txt if len(txt) < 200 else txt[:200] + '...'))
        sys.stdout.flush()
        s.f.write((txt + '\n').encode()); s.f.flush()

def attempt(sg, dad, b, Qid_ad, Qid_me, H, log):
    t_start = time.time()
    A = Qid_ad if dad == 1 else e2_neg(Qid_ad)
    Bc = e2_mul(H, Qid_me)
    if sg * b < 0: Bc = e2_neg(Bc)
    S = e2_add(A, Bc)
    assert S is not None and e2_mul(N, S) is None, 'S not valid n-torsion'
    sock = socket.create_connection((HOST, PORT), timeout=110)
    io = LineIO(sock)
    io.readline('#')
    params = json.loads(io.readline('#'))
    P_G1 = (params['P_G1'][0] % P, params['P_G1'][1] % P)
    Q    = (params['Q'][0] % P, params['Q'][1] % P)
    P_G2 = (parse_f2(params['P_G2'][0]), parse_f2(params['P_G2'][1]))
    log.append([P_G1, Q, P_G2])
    box = {}
    def worker():
        try:
            qm  = ate(Q, Qid_me)
            g2p = f12sq(ate(Q, P_G2))
            gad = ate(P_G1, Qid_ad)
            box.update(qm=qm, g2p=g2p, gad=gad)
        except Exception as e:
            box['err'] = e
    th = threading.Thread(target=worker); th.start()
    io.sendline(UNAME)
    io.readline(); io.readline(); io.readline()
    io.sendline(json.dumps([[Q[0], Q[1]], [fmt_f2(S[0]), fmt_f2(S[1])]]))
    io.sendline(TARGET)
    io.sendline('admin')
    line = io.readline('C')
    Cxy = json.loads(line.split('C = ', 1)[1])
    Cpt = (Cxy[0] % P, Cxy[1] % P)
    r = ate(Cpt, Qid_me if b == 1 else e2_neg(Qid_me))
    th.join()
    if 'err' in box: raise box['err']
    gad = box['gad']
    g2p = box['g2p'] if sg == 1 else f12inv(box['g2p'])
    gadp = gad if dad * sg == 1 else f12inv(gad)
    qm = box['qm'] if b == 1 else f12inv(box['qm'])
    t = f12mul(f12mul(g2p, f12inv(gadp)), f12inv(qm))
    assert f12eq(f12_pow(r, N), F121) and f12eq(f12_pow(t, N), F121)
    assert not f12eq(r, F121) and not f12eq(t, F121)
    io.sendline(json.dumps([fmt_f12(t), fmt_f12(r)]), 'tr')
    res = io.readline('R')
    try: sock.close()
    except Exception: pass
    print('attempt sg=%+d dad=%+d b=%+d -> %r  (%.1fs)' % (sg, dad, b, res, time.time() - t_start))
    return res

def main():
    discover(); frob_setup()
    Qid_ad = H0('admin'); Qid_me = H0(UNAME)
    H = Hm(TARGET.encode())
    print('Qid_ad =', Qid_ad, 'Qid_me =', Qid_me, 'H =', H, flush=True)
    log = []
    combos = [(1,1,1)]
    if len(sys.argv) > 1:
        combos = [tuple(int(v) for v in a.split(',')) for a in sys.argv[1:]]
    for sg, dad, b in combos:
        try:
            res = attempt(sg, dad, b, Qid_ad, Qid_me, H, log)
        except Exception as e:
            print('EXC', repr(e)); continue
        if res.startswith('ECSC{'):
            print('FLAG:', res); return
        if 'went wrong' in res:
            print('SERVER ERROR (serialization?) - stop'); return
    print('no flag in tried combos')

if __name__ == '__main__':
    main()
