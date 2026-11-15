#!/usr/bin/env python
# dh_static2: Bob validates A!=1, p prime, p large — but not A vs g.
# Send A = g^t (t=3). Then shared = A^b = (g^b)^t = B^t mod p -> decrypt phase-1 flag.
import socket, json, hashlib
from Crypto.Cipher import AES

P0 = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff

def session(payload):
    s = socket.create_connection(("socket.cryptohack.org", 13378), timeout=15)
    s.settimeout(12)
    buf = b""
    def readline():
        nonlocal buf
        try:
            while b"\n" not in buf:
                d = s.recv(65536)
                if not d: return None
                buf += d
        except Exception:
            if buf.strip():
                out = buf.split(b"\n", 1)[0]
                buf = buf.split(b"\n", 1)[1] if b"\n" in buf else b""
                return out.decode().strip()
            return None
        line, buf = buf.split(b"\n", 1)
        return line.decode().strip()
    got = []
    for _ in range(4):
        l = readline()
        if l is None: break
        got.append(l)
    resp = None
    if payload:
        s.sendall((json.dumps(payload) + "\n").encode())
        resp = readline()
    s.close()
    return got, resp

got, _ = session(None)
alice = enc = None
for l in got:
    i = l.find("{")
    if i < 0: continue
    try: o = json.loads(l[i:])
    except Exception: continue
    if "A" in o: alice = o
    if "iv" in o: enc = o
p = int(alice["p"], 16)
A_al = int(alice["A"], 16)

# Path 1: g = A_alice -> Bob's B2 = A_alice^b = phase-1 shared secret.
got2, resp = session({"p": hex(p), "g": hex(A_al), "A": "0x2"})
print("path1 resp:", str(resp)[:140])
if resp and '"B"' in resp:
    o = json.loads(resp[resp.find("{"):])
    s = int(o["B"], 16)
    key = hashlib.sha1(str(s).encode()).digest()[:16]
    pt = AES.new(key, AES.MODE_CBC, bytes.fromhex(enc["iv"])).decrypt(bytes.fromhex(enc["encrypted"]))
    print("PT:", pt)
    if b"crypto" in pt:
        open("flag.txt", "w").write(pt.decode(errors="replace"))
