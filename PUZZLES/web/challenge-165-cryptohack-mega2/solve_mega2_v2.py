# mega2 solver v2 — CRT fault on u (scramble interior block 39) + Coppersmith.
# ONE login: send_challenge with share_key_enc = legit blob with a byte in
# ciphertext block 39 (bytes 624..639, interior to u, padding block untouched)
# XOR 0xFF -> AES-ECB-decrypt scrambles plaintext block 39 -> u' = u + delta.
# With SID_enc = M^e mod n (M = 2^1024+12345) the legit decrypt is exactly M, and
# the faulted CRT output is m' = M + v*p exactly (v = h'-h, |v| < q).
# Server returns m_top = m' >> 128, so Yc = m_top*2^128 - M + m_low = v*p with
# m_low < 2^128:  Yc = j*p - r (mod n), r < 2^128 -> Coppersmith factors n.
import sys, os, json, math, socket, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cop3 import coppersmith_factor

HOST, PORT = "socket.cryptohack.org", 13409
M = (1 << 1024) + 12345

class S:
    def __init__(self, host=HOST, port=PORT):
        self.sock = socket.create_connection((host, port), timeout=60)
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

    def fault(self, off):
        h = "%x" % pow(M, self.e, self.n)
        if len(h) % 2: h = "0" + h
        bad = bytearray(self.ske); bad[off] ^= 0xFF
        self.act({"action": "wait_login"}); self.logins += 1
        return self.act({"action": "send_challenge", "SID_enc": h,
                         "share_key_enc": bytes(bad).hex(), "master_key_enc": self.mke})

def crack(n, Yc):
    facs, _ = coppersmith_factor(n, Yc % n, 1 << 130, m=6)
    return facs[0] if facs else None

def attack(host=HOST, port=PORT, verbose=True):
    s = S(host, port)
    for off in (639, 630, 624):
        if s.logins >= 4: break
        r = s.fault(off)
        if "SID" not in r:
            if verbose: print("off", off, "errored:", r, flush=True)
            continue
        m_top = int.from_bytes(bytes.fromhex(r["SID"]), "big")
        Yc = m_top * (1 << 128) - M
        if verbose: print("off", off, "got SID, m_top bits", m_top.bit_length(), flush=True)
        p_ = crack(s.n, Yc)
        if p_:
            q_ = s.n // p_
            if verbose: print("FACTORED p bits", p_.bit_length(), "logins", s.logins, flush=True)
            return s, p_, q_
        return None, None, None
    return None, None, None

def finish(s, p_, q_):
    import hashlib
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    r2 = s.act({"action": "get_encrypted_flag"})
    enc = bytes.fromhex(r2["encrypted_flag"])
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
    for attempt in range(5):
        try:
            s, p_, q_ = attack()
            if p_:
                flag = finish(s, p_, q_)
                if flag:
                    print("FLAG:", flag, flush=True)
                    open(os.path.join(HERE, "flag_mega2.txt"), "w").write(flag)
                    sys.exit(0)
                print("factored but decrypt failed", flush=True)
            else:
                print("attempt", attempt, "no factor", flush=True)
        except Exception as ex:
            print("attempt", attempt, "fatal:", str(ex)[:160], flush=True)
        time.sleep(5)
    sys.exit(1)
