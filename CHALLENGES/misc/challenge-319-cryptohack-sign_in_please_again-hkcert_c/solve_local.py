# End-to-end self-test against a LOCAL CLONE of chall.py (subprocess pipe driver).
import os, sys, io, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solve_core import solve_connection
from sbase import fast_pow
import base64, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

class Pipe:
    def __init__(self, flag):
        env = dict(os.environ)
        env['FLAG'] = flag
        env['PYTHONUNBUFFERED'] = '1'
        env['PYTHONIOENCODING'] = 'utf-8'
        self.p = subprocess.Popen([PY, 'local_run.py'], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  cwd=HERE, env=env)
        self.fd = self.p.stdout.fileno()
        self.buf = b''
    def until(self, marker):
        m = marker.encode() if isinstance(marker, str) else marker
        while m not in self.buf:
            d = os.read(self.fd, 4096)
            if not d:
                raise EOFError('closed; buf=' + self.buf[-120:].decode(errors='replace'))
            self.buf += d
        i = self.buf.index(m) + len(m)
        out, self.buf = self.buf[:i], self.buf[i:]
        return out.decode(errors='replace')
    def send(self, s):
        self.p.stdin.write((s + '\n').encode())
        self.p.stdin.flush()
    def line_after(self, marker):
        """Read until marker, then continue to the next newline (payload may arrive split)."""
        self.until(marker)
        return self.until('\n')
    def handshake(self):
        self.until('\U0001f527 ')                   # wrench emoji
        greet = self.line_after('')                 # the b64 challenge line tail
        chal = base64.b64decode(greet.strip().split()[0])
        r = fast_pow(chal)
        self.send(base64.b64encode(r.to_bytes(4, 'big')).decode())
        self.until('\U0001f916 ')                  # robot prompt
    def spy(self, pbox, salt_bytes):
        self.send('\U0001f575\ufe0f')
        self.until('\U0001f635 ')
        self.send('[%s]' % ','.join(map(str, pbox)))
        self.until('\U0001f9c2 ')
        self.send(base64.b64encode(salt_bytes).decode())
        out = self.until('\n').strip()
        assert out.startswith('\U0001f511'), out
        return out.split()[1]
    def begin_auth(self):
        self.send('\U0001f5a5\ufe0f')
        import ast
        seg = self.until('\U0001f511 ')            # "😵 [..]\n🧂 b64..\n🔑 "
        pbox = ast.literal_eval(seg.split('\U0001f635')[1].split('\U0001f9c2')[0])
        salt = base64.b64decode(seg.split('\U0001f9c2')[1].split()[0])
        return pbox, salt
    def answer(self, digest):
        self.send(digest)
        return self.until('\n').strip()
    def close(self):
        try:
            self.p.stdin.close(); self.p.kill()
        except Exception:
            pass

def trial(flag, log=False):
    c = Pipe(flag)
    try:
        c.handshake()
        return solve_connection(c.spy, c.begin_auth, c.answer,
                                log=(print if log else lambda *a: None))
    finally:
        c.close()

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    wins = 0
    for i in range(n):
        t0 = time.time()
        try:
            f = trial('TESTFLAG{local_only_not_real}', log=(i == 0))
        except Exception as e:
            print(f'trial {i}: EXCEPTION {type(e).__name__}: {e}')
            continue
        dt = time.time() - t0
        if f:
            wins += 1
            print(f'trial {i}: WIN in {dt:.1f}s -> {f}')
        else:
            print(f'trial {i}: miss in {dt:.1f}s')
    print(f'local success: {wins}/{n}')
