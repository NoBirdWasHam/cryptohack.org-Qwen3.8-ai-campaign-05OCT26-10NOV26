#!/usr/bin/env python
"""dh_static (100 pts) — Bob uses a STATIC secret key b.

Phase 1 (passive): server prints intercepted Alice {p,g,A}, Bob {B}, {iv,encrypted}.
Phase 2: "Bob connects to you, send him some parameters" — I provide {p, g, A}
and Bob (using the SAME b, and my p/g) computes shared = A^b and returns
{B, iv, encrypted_flag} under key SHA1(str(shared))[:16].

Attack: send A = 1. Then shared = 1^b = 1 for ANY b. Key known -> decrypt.
"""
import socket, json, hashlib
from Crypto.Cipher import AES

P = "0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff"

s = socket.create_connection(("socket.cryptohack.org", 13373), timeout=30)
s.settimeout(25)
buf = b""

def recv_until(objs_wanted=3):
    global buf
    have = 0
    while have < objs_wanted:
        try:
            d = s.recv(65536)
        except socket.timeout:
            break
        if not d:
            break
        buf += d
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            t = line.decode().strip()
            if not t:
                continue
            print("S:", t[:120])
            have += 1
    return have

recv_until(3)  # intercepted Alice / Bob / Alice(iv)
t = recv_until(1)  # "Bob connects to you, send him some parameters:"

# Phase 2: send Bob our chosen parameters. A = 1  =>  shared = 1^b = 1.
send = {"p": P, "g": "0x02", "A": "0x01"}
s.sendall((json.dumps(send) + "\n").encode())
print("C:", json.dumps(send))

# Read Bob's reply (may span packets)
resp = b""
while b"encrypted" not in resp and b"error" not in resp and b"iv" not in resp:
    try:
        d = s.recv(65536)
    except socket.timeout:
        break
    if not d:
        break
    resp += d
print("S:", resp.decode().strip()[:400])
s.close()

objs = []
for line in resp.decode().strip().splitlines():
    b = line.find("{")
    if b >= 0:
        try:
            objs.append(json.loads(line[b:]))
        except Exception:
            pass
m = objs[-1] if objs else {}
print("reply keys:", list(m.keys()))

iv = m.get("iv", "")
ct = m.get("encrypted", m.get("encrypted_flag", ""))
shared = 1  # 1^b = 1
key = hashlib.sha1(str(shared).encode()).digest()[:16]
pt = AES.new(key, AES.MODE_CBC, bytes.fromhex(iv)).decrypt(bytes.fromhex(ct))
n = pt[-1]
if 1 <= n <= 16 and pt[-n:] == bytes([n]) * n:
    pt = pt[:-n]
flag = pt.decode("ascii", "replace")
print("PLAINTEXT:", flag)
