# Calm Down HKCERT2020: boundary binary-search attack (few k queries).
# Oracle: YES(s) on ct=c*s^e mod n  <=>  (s*m mod n) mod 256 == 46.
# For mu=46: YES <=> 46(s-1) = Q*n (mod 256) with Q=floor(s*m/n).
# Q=0 region (s*m<n): solvable iff Q even -> YES <=> s = 1 (mod 128) AND s*m < n.
# So probe aligned s(t)=128t+1: P(t)=[s(t)*m<n] is monotone in t.
# First NOPE t*: m/n in [1/s*, 1/(s*-128)) -> width*n ~ 128*m^2/n << 1
# -> unique integer m, verified with pow(m,e,n)==c.
import sys, base64, socket, subprocess, time
from fractions import Fraction

E = 65537
def ltb(x): return x.to_bytes((x.bit_length()+7)//8, "big") if x else b""
def b2l(b): return int.from_bytes(b, "big")

class Sess:
    HOST, PORT = "archive.cryptohack.org", 53580
    def __init__(self):
        self.sk = socket.create_connection((self.HOST, self.PORT), timeout=60)
        self.buf = b""
        self._read_until(b"[cmd]")
    def _read_until(self, mark):
        while mark not in self.buf:
            d = self.sk.recv(65536)
            if not d: raise EOFError("closed")
            self.buf += d
        i = self.buf.rfind(mark); out = self.buf[:i]; self.buf = self.buf[i+len(mark):]
        return out.decode(errors="replace")
    def cmd(self, line):
        self.sk.sendall((line+"\n").encode())
        return self._read_until(b"[cmd]")
    def yes(self, s, n, c):
        ct = c * pow(s, E, n) % n
        return self.cmd("send " + base64.b64encode(ltb(ct)).decode()).strip().startswith("nice")

class Local:
    def __init__(self):
        import os
        self.p = subprocess.Popen([sys.executable, "-u", os.environ.get("CHALL_LOCAL", "chall_local.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.buf = b""
        self._read_until(b"[cmd]")
    def _read_until(self, mark):
        import os
        while mark not in self.buf:
            d = os.read(self.p.stdout.fileno(), 65536)
            if not d: raise EOFError("closed")
            self.buf += d
        i = self.buf.rfind(mark); out = self.buf[:i]; self.buf = self.buf[i+len(mark):]
        return out.decode(errors="replace")
    def cmd(self, line):
        self.p.stdin.write((line+"\n").encode()); self.p.stdin.flush()
        return self._read_until(b"[cmd]")
    def yes(self, s, n, c):
        ct = c * pow(s, E, n) % n
        return self.cmd("send " + base64.b64encode(ltb(ct)).decode()).strip().startswith("nice")

def run(sess, verbose=True):
    n = b2l(base64.b64decode(sess.cmd("pkey").split()[-1]))
    c = b2l(base64.b64decode(sess.cmd("read").split()[-1]))
    t0 = time.time(); q = 0
    def P(t):
        nonlocal q; q += 1
        return sess.yes(128*t + 1, n, c)
    # sanity: t=0 -> s=1: YES iff m mod 256 == 46
    if not P(0):
        raise RuntimeError("s=1 not YES: message does not end with '.' or mu != 46")
    # doubling to bracket first NOPE
    t_lo, t_hi = 0, None
    j = 0
    while True:
        t = 1 << j
        if not P(t):
            t_hi = t; break
        t_lo = t; j += 1
        if j > 4096: raise RuntimeError("no NOPE by 2^4096")
    if verbose: print(f"[brk] t_hi=2^{j} after {q}q", flush=True)
    # binary search first NOPE in (t_lo, t_hi)
    while t_hi - t_lo > 1:
        mid = (t_lo + t_hi) // 2
        if P(mid): t_lo = mid
        else: t_hi = mid
    if verbose: print(f"[bnd] t*={t_hi} after {q}q {time.time()-t0:.0f}s", flush=True)
    s_no, s_yes = 128*t_hi + 1, 128*t_lo + 1
    lo, hi = Fraction(1, s_no), Fraction(1, s_yes)  # m/n in [lo, hi)
    import math
    cands = range(max(1, math.ceil(n*lo)), min(n-1, math.floor(n*hi))+1)
    nc = 0
    for m in cands:
        nc += 1
        if pow(m, E, n) == c:
            return ltb(m), q, time.time()-t0
        if nc > 5000: break
    raise RuntimeError(f"no candidate matched ({nc} tried, w*n={float((hi-lo)*n):.3e})")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "remote"
    sess = Local() if mode == "local" else Sess()
    flag, q, dt = run(sess)
    print("M:", flag, "queries:", q, f"{dt:.1f}s", flush=True)
    if mode != "local":
        open("flag_calm_down-hkcert_ctf2020.txt", "wb").write(flag)
