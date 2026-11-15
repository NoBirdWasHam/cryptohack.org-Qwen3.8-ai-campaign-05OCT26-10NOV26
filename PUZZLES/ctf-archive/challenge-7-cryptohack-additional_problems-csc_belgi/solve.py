#!/usr/bin/env python3
# additional_problems-csc_belgi solve.
# Idea: per-connection p fixed. Oracle: accumulate k zero-byte encryptions
# (each noise n_i = N*r_i + 0, n_i < 2^126, and sum S = sum n_i == 0 mod N).
# Decrypt prints (c mod p) mod N = (S - b*p) mod N = (-b*p) mod N, b=floor(S/p).
# With k=4: S < 2p always -> b in {0,1}; nonzero output => p mod N = -Y.
# If no wrap (p near 2^128) use k=6 (p>~3.96*2^126 => still b<=1).
# CRT over ~20 primes in [128,256) => p; decrypt printed flag offline.
import socket, sys, time, json
try:
    import gmpy2
    is_prime = gmpy2.is_prime
except ImportError:
    is_prime = None

HOST = sys.argv[1] if len(sys.argv) > 1 else "archive.cryptohack.org"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 21970
L = 24
PRIMES = [131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,239,241,251]

class Conn:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=20)
        self.buf = b""
    def read_until(self, pat, timeout=20):
        self.s.settimeout(timeout)
        while pat not in self.buf:
            chunk = self.s.recv(4096)
            if not chunk: raise EOFError("conn closed; tail=%r" % self.buf[-200:])
            self.buf += chunk
        i = self.buf.index(pat) + len(pat)
        out, self.buf = self.buf[:i], self.buf[i:]
        return out
    def send(self, s):
        self.s.sendall((s + "\n").encode())
    def close(self):
        try: self.s.close()
        except Exception: pass

def get_banner(c):
    data = c.read_until(b"Now you get to encrypt")
    nums = []
    for line in data.split(b"\n"):
        line = line.strip()
        if line.isdigit(): nums.append(int(line))
    return nums

def probe_N(c, N, k, tries):
    """For modulus N, do `tries` accumulations of k zero encryptions each,
    return set of nonzero decrypted byte values."""
    hits = set()
    hexmsg = "00 " * (L - 1) + "00"
    for t in range(tries):
        c.send("1"); c.read_until(b"Choose N: ")
        c.send(str(N)); c.read_until(b"hexadecimal): ")
        c.send(hexmsg); c.read_until(b"> ")
        for _ in range(k - 1):
            c.send("2"); c.read_until(b"hexadecimal): ")
            c.send(hexmsg); c.read_until(b"> ")
        c.send("3")
        out = c.read_until(b"\n")
        # out like b"Decrypted message: 0a 00 1f ...\n"
        body = out.split(b":", 1)[1]
        vals = [int(x, 16) for x in body.split()]
        for v in vals:
            if v != 0: hits.add(v)
        if len(hits) >= 2:
            return hits  # inconsistent -> caller retries
    return hits

def main():
    c = Conn(HOST, PORT)
    flag_ct = get_banner(c)
    print("[*] %d flag ciphertexts" % len(flag_ct), flush=True)
    mods = []
    for N in PRIMES:
        a = None
        for attempt in range(3):
            hits = probe_N(c, N, 4, 4)
            if len(hits) == 1:
                a = (-hits.pop()) % N; break
            if len(hits) == 0:
                # p too close to 2^128 for k=4 wraps; k=6 with b<=1 guaranteed
                hits6 = probe_N(c, N, 6, 4)
                h6 = {v for v in hits6 if v}
                if len(hits6) == 1:
                    a = (-hits6.pop()) % N; break
            # else inconsistent, retry
        if a is None:
            print("[!] failed modulus %d, closing" % N); c.close(); return None
        mods.append((N, a))
        print("[+] p mod %d = %d" % (N, a), flush=True)
    # CRT
    x, M = 0, 1
    for n_i, a_i in mods:
        inv = pow(M, -1, n_i)
        t = ((a_i - x) * inv) % n_i
        x += M * t; M *= n_i
    print("[*] CRT product bits=%d, residue bits=%d" % (M.bit_length(), x.bit_length()), flush=True)
    lo, hi = 2**127, 2**128
    t0 = (lo - x + M - 1) // M
    cands = []
    tt = t0
    while True:
        p = x + tt * M
        if p >= hi: break
        if is_prime(p): cands.append(p)
        tt += 1
    print("[*] %d prime candidates in range" % len(cands), flush=True)
    for p in cands:
        msg = "".join(chr((ci % p) % 128) for ci in flag_ct)
        if all(32 <= ord(ch) < 127 for ch in msg):
            print("[!] FLAG: %s" % msg, flush=True)
            open("flag_local.json", "w").write(json.dumps({"p": str(p), "flag": msg}))
            c.close()
            return msg
    print("[!] no printable decryption", flush=True)
    c.close(); return None

if __name__ == "__main__":
    r = main()
    sys.exit(0 if r else 1)
