# Live solve: broken_oracle-hacktm_ctf2023 @ archive.cryptohack.org:56048
import socket, sys, random, re
sys.path.insert(0, ".")
import server, gmpy2
from math import gcd
from Crypto.Util.number import long_to_bytes

HOST, PORT = "archive.cryptohack.org", 56048

class Conn:
    def __init__(self):
        self.s = socket.create_connection((HOST, PORT), timeout=30)
        self.f = self.s.makefile("rwb")
    def line(self):
        b = self.f.readline()
        if not b: raise EOFError("closed")
        return b.decode().strip()
    def query(self, r, s, t):
        self.f.write(f"{r},{s},{t}\n".encode()); self.f.flush()
        rp = sp = tp = None
        while True:
            ln = self.line()
            if "Something wrong" in ln: return None
            m = re.match(r"(?:.*?r = (-?\d+))", ln)
            if m: rp = int(m.group(1)); break
        sp = int(re.search(r"s = (-?\d+)", self.line()).group(1))
        tp = int(re.search(r"t = (-?\d+)", self.line()).group(1))
        return rp, sp, tp

c = Conn()
assert "encrypted flag" in c.line()
ef = {}
for k in ("r", "s", "t"):
    ef[k] = int(re.search(rf"{k} = (-?\d+)", c.line()).group(1))
n = None
print("flag enc r bits:", ef["r"].bit_length(), "s,t:", ef["s"], ef["t"], flush=True)

p = None
random.seed()
tries = 0
while p is None and tries < 300:
    tries += 1
    r = random.randrange(2**1023 + 1, 2**1024)  # < n (n is 2048-bit) — below n since n>2^2047? n=p*q ~2^2048; keep r < n via retry on wrong
    res = None
    while True:
        res = c.query(r % (2**2047), 1, 1)
        break
    if res is None: continue
    rp, sp, tp = res
    if rp is None: continue
    g = gcd(abs(rp - (r % (2**2047))), 0)  # placeholder, n unknown yet
    # We don't know n yet! Use gcd(g_diff, ...) trick: need n. Derive n from... we only know r' values.
    print("diff bits:", abs(rp - (r % (2**2047))).bit_length(), flush=True)
    break
