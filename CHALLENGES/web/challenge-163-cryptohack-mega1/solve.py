# mega1: MEGA malleable-encryption RSA key recovery.
# Flip one ECB block inside u -> CRT decrypt with garbage u' becomes a (M < q?) oracle.
# Binary-search q in ~1023 queries on ONE connection; then decrypt the flag.
import socket, json, hashlib, re, sys, time
from Crypto.Cipher import AES

HOST, PORT = "socket.cryptohack.org", 13408

def readline(f):
    while True:
        line = f.readline()
        if not line:
            raise EOFError("closed")
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except Exception:
            continue  # skip banner text lines

sock = socket.create_connection((HOST, PORT), timeout=60)
f = sock.makefile("rwb")
# banner: raw text lines then a JSON material line
material = None
t0 = time.time()
while material is None:
    line = f.readline()
    if not line: raise EOFError()
    s = line.decode().strip()
    if s.startswith("{"):
        material = json.loads(s)
print("got material", time.time()-t0, flush=True)
n, e = material["share_key_pub"]
ske = bytes.fromhex(material["share_key_enc"])
mke = bytes.fromhex(material["master_key_enc"])
print("n bits", n.bit_length(), "ske blocks", len(ske)//16, flush=True)

# flip block 35 (bytes 560..575, strictly inside u)
ske_bad = bytearray(ske)
B = 35
for j in range(16):
    ske_bad[B*16 + j] ^= 0xFF
ske_bad = bytes(ske_bad)

def query(M):
    SID_enc = pow(M, e, n)
    msg = {"action": "send_challenge",
           "SID_enc": "%x" % SID_enc,
           "share_key_enc": ske_bad.hex(),
           "master_key_enc": mke.hex()}
    sock.sendall((json.dumps(msg) + "\n").encode())
    r = readline(f)
    if "SID" not in r:
        return None
    return bytes.fromhex(r["SID"])

# enter LOGIN state first
sock.sendall((json.dumps({"action": "wait_login"}) + "\n").encode())
r = readline(f)
print("wait_login ->", str(r)[:60], flush=True)

# NOTE: each send_challenge flips state back to PROCESSING; must wait_login before each!
def oracle(M):
    sock.sendall((json.dumps({"action": "wait_login"}) + "\n").encode())
    readline(f)
    sid = query(M)
    if sid is None:
        return None
    exp = ("%x" % M).rstrip()
    eb = bytes.fromhex(exp if len(exp) % 2 == 0 else "0"+exp)
    expected = eb[:-16]
    return sid == expected

lo = 1 << 1023
hi = (1 << 1024) - 1
# sanity: M tiny -> M < q -> True ; M huge (2^1024-1) -> M >= q -> False
assert oracle(12345) is True, "low probe failed"
assert oracle(hi) is False, "high probe failed"
print("probes ok", flush=True)

cnt = 0
while hi - lo > 1:
    mid = (lo + hi) // 2
    r = oracle(mid)
    cnt += 1
    if r is None:
        print("ERROR at query", cnt, flush=True); sys.exit(1)
    if r:
        lo = mid
    else:
        hi = mid
    if cnt % 100 == 0:
        print(cnt, "bits left", (hi-lo).bit_length(), f"{time.time()-t0:.0f}s", flush=True)
q = hi
assert n % q == 0, "q wrong"
p = n // q
print("FACTORED after", cnt, "queries", flush=True)

sock.sendall((json.dumps({"action": "get_encrypted_flag"}) + "\n").encode())
r = readline(f)
enc_flag = bytes.fromhex(r["encrypted_flag"])
secret = hashlib.sha256(p.to_bytes(128,"big") + q.to_bytes(128,"big")).digest()
pt = AES.new(secret, AES.MODE_ECB).decrypt(enc_flag)
print("FLAG:", pt, flush=True)
open("flag_mega1.txt","w").write(pt.decode(errors="replace"))
sock.close()
