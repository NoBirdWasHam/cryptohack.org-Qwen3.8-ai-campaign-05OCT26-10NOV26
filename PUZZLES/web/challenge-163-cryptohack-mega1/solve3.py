# mega1 v3: even-length hex fix for SID_enc (odd hex -> server bytes.fromhex ValueError).
import socket, json, hashlib, time
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

HOST, PORT = "socket.cryptohack.org", 13408

class S:
    def __init__(self):
        self.sock = socket.create_connection((HOST, PORT), timeout=60)
        self.f = self.sock.makefile("rwb")
        while True:
            line = self.f.readline()
            if not line: raise EOFError()
            s = line.decode().strip()
            if s.startswith("{"):
                mat = json.loads(s); break
        self.n, self.e = mat["share_key_pub"]
        self.ske = bytes.fromhex(mat["share_key_enc"])
        self.mke = bytes.fromhex(mat["master_key_enc"])
        bad = bytearray(self.ske)
        for j in range(16): bad[35*16+j] ^= 0xFF   # corrupt u-field block only
        self.ske_bad = bytes(bad)
        self.queries = 0

    def rjson(self):
        while True:
            line = self.f.readline()
            if not line: raise EOFError()
            s = line.decode().strip()
            if not s: continue
            try: return json.loads(s)
            except Exception: continue

    def act(self, msg):
        self.sock.sendall((json.dumps(msg) + "\n").encode())
        return self.rjson()

    def oracle(self, M):
        h = "%x" % pow(M, self.e, self.n)
        if len(h) % 2: h = "0" + h          # <-- the fix
        self.act({"action": "wait_login"})
        r2 = self.act({"action": "send_challenge",
                       "SID_enc": h,
                       "share_key_enc": self.ske_bad.hex(),
                       "master_key_enc": self.mke.hex()})
        self.queries += 1
        if "SID" not in r2:
            raise RuntimeError(f"oracle err q{self.queries}: {str(r2)[:100]}")
        sid = bytes.fromhex(r2["SID"])
        hm = "%x" % M
        if len(hm) % 2: hm = "0" + hm
        return sid == bytes.fromhex(hm)[:-16]

def finish(s, qmin):
    assert s.n % qmin == 0, "qmin invalid"
    a, b = qmin, s.n // qmin
    r = s.act({"action": "get_encrypted_flag"})
    enc = bytes.fromhex(r["encrypted_flag"])
    for (p_, q_) in ((a, b), (b, a)):
        secret = hashlib.sha256(p_.to_bytes((p_.bit_length()+7)//8, "big") +
                                q_.to_bytes((q_.bit_length()+7)//8, "big")).digest()
        try:
            pt = unpad(AES.new(secret, AES.MODE_ECB).decrypt(enc), 16)
        except Exception:
            continue
        if pt.startswith(b"crypto"):
            print("FLAG:", pt.decode(), flush=True)
            open("flag_mega1.txt", "w").write(pt.decode())
            return True
    print("neither order decrypted; p,q =", a, b, flush=True)
    return False

for attempt in range(4):
    try:
        s = S()
        print("connected; n bits", s.n.bit_length(), flush=True)
        assert s.oracle(12345) is True, "probe1"
        assert s.oracle((1 << 1024) - 1) is False, "probe2"
        lo, hi = 1 << 1023, (1 << 1024) - 1
        t0 = time.time()
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if s.oracle(mid): lo = mid
            else: hi = mid
            if s.queries % 256 == 0:
                print(s.queries, "bits", (hi - lo).bit_length(), f"{time.time()-t0:.0f}s", flush=True)
        print("search done", s.queries, "queries", f"{time.time()-t0:.0f}s", flush=True)
        if finish(s, hi): break
        else: break
    except Exception as ex:
        print("attempt", attempt, "fatal:", str(ex)[:160], flush=True)
        time.sleep(3)
