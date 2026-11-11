# mega2 solver: ONE login. XOR 0xFF into u's last plaintext byte (probe 647/646/645
# via the padding-error channel). Then u' = u + d, |d| < 256, and
#   m = M + f*p^2*d - w*n   exactly, with f = floor(M/p) in {1,2,3}, |w| <= 1100.
# SID gives m up to its low 128 bits; p = isqrt((Y + w*n + r)/(f*d)) is insensitive
# to r, so enumerate (f, d, w) and test n % cand == 0. Then decrypt the flag.
import sys, os, json, math, socket, time
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

HOST, PORT = "socket.cryptohack.org", 13409

class S:
    def __init__(self):
        self.sock = socket.create_connection((HOST, PORT), timeout=60)
        self.f = self.sock.makefile("rwb")
        while True:
            line = self.f.readline()
            if not line: raise EOFError()
            s = line.decode().strip()
            if s.startswith("{"):
                self.mat = json.loads(s); break
        self.n, self.e = self.mat["share_key_pub"]
        self.ske = bytes.fromhex(self.mat["share_key_enc"])
        self.mke = self.mat["master_key_enc"]
        self.logins = 0

    def act(self, msg):
        self.sock.sendall((json.dumps(msg) + "\n").encode())
        while True:
            line = self.f.readline()
            if not line: raise EOFError()
            s = line.decode().strip()
            if not s: continue
            try: return json.loads(s)
            except Exception: continue

    def oracle(self, M, ske_bad):
        h = "%x" % pow(M, self.e, self.n)
        if len(h) % 2: h = "0" + h
        self.act({"action": "wait_login"}); self.logins += 1
        return self.act({"action": "send_challenge", "SID_enc": h,
                         "share_key_enc": ske_bad.hex(), "master_key_enc": self.mke})

def solve(s):
    M = (1 << 1024) + 12345
    for off in (647, 646, 645):
        bad = bytearray(s.ske); bad[off] ^= 0xFF
        r = s.oracle(M, bytes(bad))
        if "SID" in r:
            break
    else:
        return None, f"all probes errored (logins={s.logins})"
    m_top = int.from_bytes(bytes.fromhex(r["SID"]), "big")
    Y = m_top * (1 << 128) - M
    n = s.n
    for f in (1, 2, 3):
        for d in range(-255, 256, 2):
            if d == 0: continue
            for w in range(-1600, 1601):
                num = Y + w * n + (1 << 127)
                den = f * d
                if den < 0: num, den = -num, -den
                if num <= 0: continue
                p_ = math.isqrt(num // den)
                for cand in (p_ - 1, p_, p_ + 1):
                    if cand > 1 and n % cand == 0:
                        return cand, f"off={off} f={f} d={d} w={w}"
    return None, "enumeration found no factor"

def finish(s, p_):
    r2 = s.act({"action": "get_encrypted_flag"})
    enc = bytes.fromhex(r2["encrypted_flag"])
    q_ = s.n // p_
    for (a, b) in ((p_, q_), (q_, p_)):
        secret = hashlib.sha256(a.to_bytes((a.bit_length()+7)//8, "big") +
                                b.to_bytes((b.bit_length()+7)//8, "big")).digest()
        try:
            pt = unpad(AES.new(secret, AES.MODE_ECB).decrypt(enc), 16)
        except Exception:
            continue
        if pt.startswith(b"crypto"):
            return pt.decode()
    return None

if __name__ == "__main__":
    for attempt in range(3):
        try:
            s = S()
            p_, info = solve(s)
            if p_:
                flag = finish(s, p_)
                if flag:
                    print("INFO:", info, "| logins:", s.logins)
                    print("FLAG:", flag)
                    open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "flag_mega2.txt"), "w").write(flag)
                    sys.exit(0)
            print("attempt", attempt, "no flag:", info, flush=True)
        except Exception as ex:
            print("attempt", attempt, "fatal:", str(ex)[:160], flush=True)
        time.sleep(3)
    sys.exit(1)
