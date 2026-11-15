# mega1 v2: same attack, but log raw errors + reconnect/resync on failure.
import socket, json, hashlib, sys, time
from Crypto.Cipher import AES

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
        for j in range(16): bad[35*16+j] ^= 0xFF
        self.ske_bad = bytes(bad)
        self.mat = mat
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
        r1 = self.act({"action": "wait_login"})
        r2 = self.act({"action": "send_challenge",
                       "SID_enc": "%x" % pow(M, self.e, self.n),
                       "share_key_enc": self.ske_bad.hex(),
                       "master_key_enc": self.mke.hex()})
        self.queries += 1
        if "SID" not in r2:
            raise RuntimeError(f"oracle err after {self.queries}q: login={str(r1)[:60]} chal={str(r2)[:120]}")
        sid = bytes.fromhex(r2["SID"])
        h = "%x" % M
        if len(h) % 2: h = "0" + h
        return sid == bytes.fromhex(h)[:-16]

def search():
    s = S()
    print("connected; n bits", s.n.bit_length(), "blocks", len(s.ske)//16, flush=True)
    assert s.oracle(12345) is True
    assert s.oracle((1<<1024)-1) is False
    lo, hi = 1 << 1023, (1 << 1024) - 1
    t0 = time.time()
    while hi - lo > 1:
        mid = (lo + hi) // 2
        try:
            r = s.oracle(mid)
        except (RuntimeError, EOFError) as ex:
            print("reconnect:", str(ex)[:140], flush=True)
            time.sleep(2)
            return None  # fresh key needed; caller restarts
        if r: lo = mid
        else: hi = mid
        if s.queries % 128 == 0:
            print(s.queries, "bits", (hi-lo).bit_length(), f"{time.time()-t0:.0f}s", flush=True)
    q = hi
    assert s.n % q == 0, "q invalid"
    p = s.n // q
    r = s.act({"action": "get_encrypted_flag"})
    enc_flag = bytes.fromhex(r["encrypted_flag"])
    secret = hashlib.sha256(p.to_bytes(128,"big") + q.to_bytes(128,"big")).digest()
    pt = AES.new(secret, AES.MODE_ECB).decrypt(enc_flag)
    print("FLAG:", pt, flush=True)
    open("flag_mega1.txt","w").write(pt.decode(errors="replace"))
    return True

for attempt in range(5):
    try:
        if search(): break
    except Exception as ex:
        print("attempt", attempt, "fatal:", str(ex)[:200], flush=True)
        time.sleep(3)
