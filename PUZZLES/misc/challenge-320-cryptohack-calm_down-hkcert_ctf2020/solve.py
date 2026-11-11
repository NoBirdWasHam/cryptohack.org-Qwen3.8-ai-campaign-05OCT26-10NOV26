# Calm Down (HKCERT 2020): RSA raw-decrypt oracle, YES iff plaintext last byte == '.'
# YES(s) <=> (m*s mod n) mod 256 == 46
#        <=> exists q=floor(s*m/n): mu*s - q*n == 46 (mod 256),  mu = m mod 256
# Phase 1: small odd s -> q=0 -> YES gives mu = 46*s^{-1} mod 256
# Phase 2: interval [lo,hi] for phi=m/n; per round pick s ~ 256/(hi-lo), scan s
#          so each candidate bin q tested; YES <=> phi in [q/s,(q+1)/s).
import socket, base64, json, sys, time
from fractions import Fraction
from math import ceil, floor

HOST, PORT = "archive.cryptohack.org", 53580
E = 65537

class Sess:
    def __init__(self, host=HOST, port=PORT):
        self.sk = socket.create_connection((host, port), timeout=30)
        self.buf = b""
        self._read_until()
    def _read_until(self):
        while b"[cmd]" not in self.buf:
            d = self.sk.recv(4096)
            if not d: raise EOFError("closed")
            self.buf += d
        i = self.buf.rfind(b"[cmd]"); out = self.buf[:i]; self.buf = self.buf[i+6:]
        return out.decode(errors="replace")
    def cmd(self, line):
        self.sk.sendall((line + "\n").encode())
        return self._read_until()

def ltb(x):
    return x.to_bytes((x.bit_length()+7)//8, "big") if x else b""

def b2l(b): return int.from_bytes(b, "big")

def run(session=None, verbose=True):
    s = session or Sess()
    out = s.cmd("pkey"); n = int.from_bytes(base64.b64decode(out.split()[-1]), "big")
    out = s.cmd("read"); c = b2l(base64.b64decode(out.split()[-1]))
    ninv = pow(n, -1, 256)
    qcount = 0
    def Q(sv):
        nonlocal qcount
        qcount += 1
        ct = c * pow(sv % n, E, n) % n
        r = s.cmd("send " + base64.b64encode(ltb(ct)).decode())
        return r.strip().startswith("nice")
    # Phase 1: mu
    mu = None
    for sv in range(1, 2048, 2):
        if Q(sv):
            mu = 46 * pow(sv, -1, 256) % 256
            if verbose: print(f"[mu] YES at s={sv} -> mu={mu} (char {chr(mu)!r})", flush=True)
            break
    if mu is None: raise RuntimeError("no YES for mu (last byte even or session issue)")
    # Phase 2
    lo, hi = Fraction(0), Fraction(1)
    t0 = time.time()
    PRINT = set(range(32, 127))
    muinv = pow(mu, -1, 256) if mu % 2 else None
    while True:
        mlo, mhi = ceil(n*lo), floor(n*hi)
        if mlo == mhi and mlo > 0:
            return ltb(mlo), mu, qcount, time.time()-t0
        if hi - lo < Fraction(1, n):
            return ltb(mhi if mhi != mlo else mlo), mu, qcount, time.time()-t0
        width = hi - lo
        s0 = max(2, int(256/width))
        ql, qh = int(ceil(s0*lo)), int(floor(s0*hi))
        if qh <= ql: qh = ql + 1
        bins = [q for q in range(ql, qh+1)]
        def topbyte(q):
            f = Fraction(q, s0) * n
            return int(f // 1) & 0xff
        pred = (mlo >> (mlo.bit_length()-8)) & 0xff if mlo else None
        bins.sort(key=lambda q: (0 if topbyte(q)==pred else 1, 0 if topbyte(q) in PRINT else 1))
        found = False
        for q in bins:
            if muinv is not None:
                v = ((46 + q*(n % 256)) * muinv) % 256
            else:
                continue
            sv = s0 + ((v - s0) % 256)
            # ensure unique candidate bin for this s
            a = int(ceil(sv*lo)); b = int(floor(sv*hi))
            cands = [x for x in range(a, b+1) if Fraction(x,1) < sv*hi and x % 256 == ((mu*(sv%256)-46)*ninv)%256]
            if len(cands) != 1 or cands[0] != q:
                sv += 256
                a = int(ceil(sv*lo)); b = int(floor(sv*hi))
                cands = [x for x in range(a, b+1) if Fraction(x,1) < sv*hi and x % 256 == ((mu*(sv%256)-46)*ninv)%256]
                if len(cands) != 1: continue
            if Q(sv):
                lo, hi = max(lo, Fraction(q, sv)), min(hi, Fraction(q+1, sv))
                found = True
                break
        if not found:
            raise RuntimeError(f"scan miss at width={float(width):.3e} q={qcount}")
        if qcount > 30000: raise RuntimeError("query budget")
        if qcount % 1000 < 20 and verbose:
            print(f"[{qcount}q {time.time()-t0:.0f}s] width~{float(width):.2e}", flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        # local clone test: spawn python chall.py locally
        import subprocess, threading
        proc = subprocess.Popen([sys.executable, "chall_local.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        class L:
            def __init__(self, p):
                self.p = p
                self._read()
            def _read(self):
                out = b""
                while True:
                    ch = self.p.stdout.read(1)
                    if not ch: raise EOFError
                    out += ch
                    if out.endswith(b"[cmd] "): return out[:-6].decode()
            def cmd(self, line):
                self.p.stdin.write((line+"\n").encode()); self.p.stdin.flush()
                return self._read()
        ls = L(proc)
        # pkey/read handled inside cmd loop; first prompt consumed lazily below
        flag, mu, q, dt = run(ls)
        print("FLAG:", flag, "queries:", q, f"{dt:.1f}s")
    else:
        flag, mu, q, dt = run()
        print("FLAG:", flag)
        print(f"queries={q} time={dt:.1f}s")
        open("flag_calm_down-hkcert_ctf2020.txt", "wb").write(flag)
