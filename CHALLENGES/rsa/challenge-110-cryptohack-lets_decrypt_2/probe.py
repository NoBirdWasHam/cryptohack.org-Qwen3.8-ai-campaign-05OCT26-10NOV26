#!/usr/bin/env python3
import socket, json, hashlib

HOST, PORT = "socket.cryptohack.org", 13394

def conn():
    s = socket.create_connection((HOST, PORT), timeout=30)
    f = s.makefile("rwb")
    line = f.readline()
    return s, f, line

def send(f, obj):
    f.write((json.dumps(obj) + "\n").encode())
    f.flush()
    return json.loads(f.readline().decode())

s, f, pre = conn()
print("PRE:", pre.decode(errors="replace")[:120])
r = send(f, {"option": "get_signature"})
N = int(r["N"], 16); E = int(r["E"], 16); SIG = int(r["signature"], 16)
print("N bits", N.bit_length(), "E", E, "SIG bits", SIG.bit_length(), "SIG odd?", SIG & 1)

MSG = b'We are MAINT-ACCOUNT and Jack and we own CryptoHack.org'
DI = bytes.fromhex("3031300d060960864801650304020105000420")
def em(msg, em_len=96, di=DI, hashf=hashlib.sha256):
    t = di + hashf(msg).digest()
    ps = em_len - len(t) - 3
    return b"\x00\x01" + b"\xff"*ps + b"\x00" + t

cands = {
    "sha256+DI": int.from_bytes(em(MSG), "big"),
    "sha256 noDI": int.from_bytes(em(MSG, di=b""), "big"),
    "sha1+DI": int.from_bytes(em(MSG, di=bytes.fromhex("3021300906052b0e03021a05000414"), hashf=hashlib.sha1), "big"),
}
V = pow(SIG, E, N)
for k, v in cands.items():
    print(k, "MATCH" if v == V else "no")
print("V hex head:", hex(V)[:40])
print("V == sha256-DI em?", cands["sha256+DI"] == V)
s.close()
