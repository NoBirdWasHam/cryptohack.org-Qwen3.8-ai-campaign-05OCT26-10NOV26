# Live solver for maybe_someday (Paillier, 20-query batched oracle).
# Usage: python solve.py [--local]
import json, socket, sys, subprocess, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DES = os.environ.get('DESIGN', 'design3.json')
D = json.load(open(os.path.join(HERE, DES)))
QS = [(int(K), int(t)) for K, t in D['qs']]
TABLE = {int(k): v for k, v in D['table'].items()}
DUP = {int(k) for k in D.get('dup', [])}
NQ = len(QS)

def decode(bits):
    # bits: list of 0/1 responses; noise flips only 0->1 (extra zero byte).
    r = 0
    for j, b in enumerate(bits):
        if b: r |= 1 << j
    zeros = None
    best = None; bestpop = -1; amb = 0
    # iterate all submasks of r (noise only adds 1s, so true pattern is a submask)
    s = r
    if r in DUP:
        raise RuntimeError('pattern %05x is a known collision class -> abort session' % r)
    while True:
        c = TABLE.get(s)
        if c is not None:
            pc = bin(s).count('1')
            if pc > bestpop: best, bestpop, amb = c, pc, 1
            elif pc == bestpop: amb += 1
        if s == 0: break
        s = (s - 1) & r
    if best is None or amb > 1:
        raise RuntimeError('decode ambiguous/none r=%05x amb=%d' % (r, amb))
    return best

class Conn:
    def __init__(self, host='archive.cryptohack.org', port=14846):
        self.s = socket.create_connection((host, port), timeout=30)
        self.f = self.s.makefile('rwb')
    def line(self):
        l = self.f.readline()
        if not l: raise EOFError('connection closed')
        return l.decode('utf-8', 'replace').strip()
    def send(self, s):
        self.f.write((s + '\n').encode()); self.f.flush()
    def close(self):
        try: self.s.close()
        except Exception: pass

class Local:
    def __init__(self):
        env = dict(os.environ); env['FLAG'] = 'TEST{local_smoke_ok}'
        self.p = subprocess.Popen(['python3', 'chall.py'], cwd=HERE, env=env,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, text=True, bufsize=1)
    def line(self):
        l = self.p.stdout.readline()
        if not l: raise EOFError('local closed')
        return l.strip()
    def send(self, s):
        self.p.stdin.write(s + '\n'); self.p.stdin.flush()
    def close(self):
        try: self.p.kill()
        except Exception: pass

def grab_int(line):
    return int(line.split('=', 1)[1].strip())

def attempt(conn, max_rounds=16):
    n = grab_int(conn.line()); g = grab_int(conn.line())
    n2 = n * n
    pre = []
    for K, t in QS:
        delta = (K << 1024) | t
        pre.append(pow(pow(g, delta, n2), -1, n2))  # g^{-delta}
    for rnd in range(max_rounds):
        c0 = grab_int(conn.line())
        for j in range(NQ):
            conn.send(str(c0 * pre[j] % n2))
        bits = []
        for j in range(NQ):
            l = conn.line()
            if '\U0001f44b' in l: raise RuntimeError('killed during oracle r%d' % rnd)
            bits.append(1 if '\U0001f600' in l else 0)
        guess = decode(bits)
        conn.send(guess)
        l = conn.line()
        if '\U0001f4a1' not in l:
            raise RuntimeError('round %d no bulb: %r guess=%s...' % (rnd, l, guess[:12]))
        print('round %d ok (%s..)' % (rnd, guess[:10]), flush=True)
    l = conn.line()
    m = re.search(r'(\S*\{[^}]*\})', l)
    if not m: raise RuntimeError('no flag line: %r' % l)
    return m.group(1)

def main():
    local = '--local' in sys.argv
    maxtry = int(os.environ.get('MAXTRY', '10'))
    for att in range(1, maxtry + 1):
        conn = Local() if local else Conn()
        try:
            flag = attempt(conn)
            print('FLAG:', flag, flush=True)
            return flag
        except Exception as e:
            print('attempt %d failed: %s' % (att, e), flush=True)
            conn.close()
    raise SystemExit('all attempts failed')

if __name__ == '__main__':
    main()
