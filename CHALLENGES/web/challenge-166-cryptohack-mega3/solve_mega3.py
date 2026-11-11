# mega3 solver — leak node_key through the CRT SID oracle.
# We know (n, e, p) -> q, d, u. All blob blocks are known plaintext EXCEPT
# X = D_master(node_key_enc). Submit share_key_enc = legit ske with block 39
# (interior to u, keeps lengths+padding valid) REPLACED by node_key_enc.
# Server parses p,q,d real, u_g = u + (X - orig)*2^64, and returns
# SID = (h*p + mp) >> 128 with h = t*u_g mod q, t = (M%q - M%p) mod q known.
# => u_g = ((SID*2^128 + low - mp)/p) * t^-1 mod q  (low unknown but h = (m-mp)/p
# is exact; recover h from SID top bits by trying low in [0,2^128) via
# h_top = (SID<<128 ... ) — actually m = h*p+mp, m_top = m>>128 known:
# h*p + mp - m_top*2^128 = m_low in [0,2^128) -> h = ((m_top*2^128 + m_low - mp)/p);
# enumerate? No: h = t*u_g mod q < q, and u_g = u + delta*2^64 with |delta|<2^128.
# Simpler: h = (m - mp)/p exact; m unknown low 128 bits -> h*p = m - mp, so
# h = (m_top*2^128 - mp + m_low)/p: try the ~1 candidate h near (m_top*2^128-mp)/p
# by checking h*t^-1... we solve: for h in candidates around (m_top*2^128-mp)//p
# within 2^128/p (< 1 candidate!): h = round((m_top*2^128 + 2^127 - mp)/p), verify
# u_g = h*t^-1 mod q satisfies (u_g - u) % 2^64 == 0 and |u_g-u| < 2^192.
import sys, os, json, socket, time
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util.number import long_to_bytes, bytes_to_long

HOST, PORT = "socket.cryptohack.org", 13410
M = (1 << 1024) + 12345
J = 39  # block index inside u

def parse_material(ch_before):
    blocks = {}
    for line in ch_before.split("\n"):
        line = line.strip()
        if line.startswith("{"):
            try: blocks[len(blocks)] = json.loads(line)
            except Exception: pass
    return blocks

class S:
    def __init__(self, host=HOST, port=PORT):
        self.sock = socket.create_connection((host, port), timeout=60)
        self.f = self.sock.makefile("rwb")
        buf = ""
        mats = []
        while len(mats) < 3:
            line = self.f.readline()
            if not line: raise EOFError()
            s = line.decode().strip()
            if s.startswith("{"):
                try: mats.append(json.loads(s))
                except Exception: pass
        self.mat, self.filemat, self.rec = mats
        self.n, self.e = self.mat["share_key_pub"]
        self.ske = bytes.fromhex(self.mat["share_key_enc"])
        self.mke = self.mat["master_key_enc"]
        self.node_key_enc = bytes.fromhex(self.filemat["node_key_enc"])
        self.file_enc = bytes.fromhex(self.filemat["file_enc"])
        self.p_given = self.rec["share_key"][2]

    def act(self, msg):
        self.sock.sendall((json.dumps(msg) + "\n").encode())
        while True:
            line = self.f.readline()
            if not line: raise EOFError()
            s = line.decode().strip()
            if not s: continue
            try: return json.loads(s)
            except Exception: continue

def attack(s, verbose=True):
    p = s.p_given
    assert s.n % p == 0
    q = s.n // p
    from math import gcd, lcm
    d = pow(s.e, -1, lcm(p - 1, q - 1))
    u = pow(p, -1, q)
    blob = bytearray(656)  # we don't need the full blob, only orig block 39
    # rebuild legit plaintext to get orig chunk of u at block 39
    def fmt(num):
        b = long_to_bytes(num)
        return bytes_to_long(long_to_bytes(len(b), 2)) * 0 + len(b), b
    data = b""
    for num in (p, q, d, u):
        b = long_to_bytes(num)
        data += long_to_bytes(len(b), 2) + b
    npad = 16 - len(data) % 16
    data += bytes([npad]) * npad
    assert len(data) == len(s.ske), (len(data), len(s.ske))
    orig = bytes_to_long(data[J * 16:(J + 1) * 16])
    shift = 8 * (len(data) - (J + 1) * 16)  # bit position of block J in u? NO:
    # block 39 replaces u-bytes; u_g = u + (X-orig)*2^shift where shift counts
    # from END of u (u ends at byte 648, block ends at 640): shift = 8*(648-640)=64
    shift = 8 * (2 + 128 - (J + 1) * 16)  # u field ends at 648; generic:
    # u field: starts at 2+128+2+128+2+256 = 520, ends 648 (for 128-byte u)
    u_end = 2 + 128 + 2 + 128 + 2 + 256 + 2 + 128
    shift = 8 * (u_end - (J + 1) * 16)
    bad = bytearray(s.ske)
    bad[J * 16:(J + 1) * 16] = s.node_key_enc
    h_enc = "%x" % pow(M, s.e, s.n)
    if len(h_enc) % 2: h_enc = "0" + h_enc
    s.act({"action": "wait_login"})
    r = s.act({"action": "send_challenge", "SID_enc": h_enc,
               "share_key_enc": bytes(bad).hex(), "master_key_enc": s.mke})
    if "SID" not in r:
        if verbose: print("SID error:", r, flush=True)
        return None
    m_top = int.from_bytes(bytes.fromhex(r["SID"]), "big")
    mp = M % p
    mq = M % q
    t = (mq - mp) % q
    # h*p = m_top*2^128 + m_low - mp, m_low in [0, 2^128): interval length 2^128 < p
    lo_num = m_top * (1 << 128) - mp
    h0 = lo_num // p  # floor; true h in {h0, h0+1} (interval < p wide)
    for h in (h0, h0 + 1, h0 - 1):
        if h <= 0: continue
        ug = (h * pow(t, -1, q)) % q
        for k in (-1, 0, 1):
            ug2 = ug + k * q
            diff = ug2 - u
            if diff % (1 << shift): continue
            delta = diff >> shift
            if not (-1 << 128) < delta < (1 << 128): continue
            X = (orig + delta) % (1 << 128)
            # verify: recompute h with u_g = u + (X-orig)*2^shift
            ug3 = (u + (X - orig) * (1 << shift)) % q
            if (t * ug3) % q == h % q:
                node_key = long_to_bytes(X, 16)
                if verbose: print("node_key", node_key.hex(), flush=True)
                return node_key
    return None

def finish(s, node_key):
    pt = unpad(AES.new(node_key, AES.MODE_ECB).decrypt(s.file_enc), 16)
    return pt.decode(errors="replace")

if __name__ == "__main__":
    for attempt in range(5):
        try:
            s = S()
            nk = attack(s)
            if nk:
                txt = finish(s, nk)
                print("FILE:", txt, flush=True)
                import re
                m = re.search(r"crypto\{[^}]+\}", txt)
                if m:
                    flag = m.group(0)
                    print("FLAG:", flag, flush=True)
                    open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "flag_mega3.txt"), "w").write(flag)
                    sys.exit(0)
            print("attempt", attempt, "no key", flush=True)
        except Exception as ex:
            print("attempt", attempt, "fatal:", str(ex)[:160], flush=True)
        time.sleep(5)
    sys.exit(1)
