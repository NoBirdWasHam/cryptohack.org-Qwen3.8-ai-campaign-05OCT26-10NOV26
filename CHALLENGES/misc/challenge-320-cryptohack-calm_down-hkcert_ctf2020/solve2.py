# Calm Down HKCERT2020: pipelined last-byte RSA decryption oracle.
# YES(s) on ct=c*s^e mod n  <=>  (s*m mod n) mod 256 == 46
# Block scan: query s in [s0, s0+255]; YES reveals q_true(s) mod 256 ->
# narrows phi=m/n to union of bins [q/s,(q+1)/s]. ~8 bits / 256 queries.
import sys, base64, socket, subprocess, time
from fractions import Fraction
from math import ceil, floor

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
    def query_block(self, svals, n, c):
        # pipeline all, then count response lines 'nice'/'nope'
        payload = []
        for sv in svals:
            ct = c * pow(sv, E, n) % n
            payload.append("send " + base64.b64encode(ltb(ct)).decode() + "\n")
        self.sk.sendall("".join(payload).encode())
        want = len(svals); res = []
        while len(res) < want:
            while b"\n" not in self.buf:
                d = self.sk.recv(65536)
                if not d: raise EOFError("closed")
                self.buf += d
            line, self.buf = self.buf.split(b"\n", 1)
            l = line.decode(errors="replace").strip()
            if l == "nice" or l.endswith("[cmd] nice"): res.append(True)
            elif l == "nope" or l.endswith("[cmd] nope"): res.append(False)
        return res

class Local:
    def __init__(self):
        self.p = subprocess.Popen([sys.executable, "-u", "chall_local.py"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.buf = b""
        self._read_until(b"[cmd]")
        self.sk = None
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
    def query_block(self, svals, n, c):
        # local subprocess: stdin pipe buffers, same pipelining trick
        payload = []
        for sv in svals:
            ct = c * pow(sv, E, n) % n
            payload.append("send " + base64.b64encode(ltb(ct)).decode() + "\n")
        self.p.stdin.write("".join(payload).encode()); self.p.stdin.flush()
        import os
        want = len(svals); res = []
        while len(res) < want:
            while b"\n" not in self.buf:
                d = os.read(self.p.stdout.fileno(), 65536)
                if not d: raise EOFError("closed")
                self.buf += d
            line, self.buf = self.buf.split(b"\n", 1)
            l = line.decode(errors="replace").strip()
            if l == "nice" or l.endswith("[cmd] nice"): res.append(True)
            elif l == "nope" or l.endswith("[cmd] nope"): res.append(False)
        return res

def run(sess, block=256, verbose=True):
    n = b2l(base64.b64decode(sess.cmd("pkey").split()[-1]))
    c = b2l(base64.b64decode(sess.cmd("read").split()[-1]))
    ninv = pow(n, -1, 256)
    t0 = time.time(); q = 0
    # Phase 1: determine mu = m mod 256 from small-s YESes with q_true=0
    # (small flag => s*m < n for tiny s): YES(s) <=> mu*s ≡ 46 (mod 256)
    cands = set(range(256))
    for sv in range(1, 3072):
        ct = c * pow(sv, E, n) % n
        r = sess.cmd("send " + base64.b64encode(ltb(ct)).decode())
        q += 1
        if r.strip().startswith("nice"):
            cands &= {x for x in range(256) if x*sv % 256 == 46}
            if len(cands) == 1: break
        if len(cands) == 0: raise RuntimeError("phase1 contradiction")
    if len(cands) != 1: raise RuntimeError(f"phase1 ambiguous: {sorted(cands)}")
    mu = cands.pop()
    print(f"[mu] mu={mu} char={chr(mu)!r} after {q}q", flush=True)
    intervals = [(Fraction(0), Fraction(1))]
    while True:
        lo, hi = max(intervals, key=lambda iv: iv[1]-iv[0])
        w = hi - lo
        if w * n < 64:  # few candidate integers -> verify directly
            for (ilo, ihi) in intervals:
                for m in range(max(1, ceil(n*ilo)), min(n-1, floor(n*ihi))+1):
                    if pow(m, E, n) == c:
                        return ltb(m), q, time.time()-t0
        s0 = max(1, int(256 / w))
        svals = [s0 + r for r in range(block)]
        res = sess.query_block(svals, n, c)
        q += block
        yes_any = False
        # YES(sv) <=> q_true(sv)=floor(sv*m/n) ≡ (mu*sv-46)*ninv (mod 256)
        for sv, ok in zip(svals, res):
            if not ok: continue
            yes_any = True
            R = (mu*sv - 46) * ninv % 256
            newlist = []
            for (ilo, ihi) in intervals:
                ql, qh = ceil(sv*ilo), floor(sv*ihi)
                first = ql + ((R - ql) % 256)
                for qq in range(first, qh+1, 256):
                    a, b = max(ilo, Fraction(qq, sv)), min(ihi, Fraction(qq+1, sv))
                    if a < b: newlist.append((a, b))
            if newlist: intervals = newlist
        if verbose and q % 2048 < block:
            print(f"[{q}q {time.time()-t0:.0f}s] ivs={len(intervals)} w~{float(max(iv[1]-iv[0] for iv in intervals)):.2e} yes={sum(res)}", flush=True)
        if not yes_any and q > 200000: raise RuntimeError("no YES for 200k queries")
        if q > 400000: raise RuntimeError("query budget")
    lo, hi = intervals[0]
    for m in range(ceil(n*lo), floor(n*hi)+1):
        if pow(m, E, n) == c:
            return ltb(m), q, time.time()-t0
    raise RuntimeError("no m matched in final interval")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "remote"
    sess = Local() if mode == "local" else Sess()
    flag, q, dt = run(sess)
    print("M:", flag, "queries:", q, f"{dt:.1f}s")
    if mode != "local":
        open("flag_calm_down-hkcert_ctf2020.txt", "wb").write(flag)
