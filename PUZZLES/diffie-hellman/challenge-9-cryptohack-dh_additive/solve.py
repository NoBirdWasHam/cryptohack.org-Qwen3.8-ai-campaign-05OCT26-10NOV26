#!/usr/bin/env python
"""dh_additive (70 pts) — DH in the ADDITIVE group Z_p.

Additive DLP is trivial: A = a*g (mod p)  =>  a = A * g^{-1} (mod p).
Shared secret (additive DH) = a*B = a*b*g (mod p)  ==  b*A (mod p).
Key = SHA1(str(secret))[:16], AES-128-CBC — the "Deriving Symmetric Keys"
script from dh-starter-5 (decrypt_provided.py).
"""
import socket, json, hashlib
from Crypto.Cipher import AES

p = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff
g = 2

s = socket.create_connection(("socket.cryptohack.org", 13380), timeout=30)
s.settimeout(25)
buf = b""
alice = bob = enc = None
while True:
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
        print("S:", t[:100])
        if "Intercepted from Alice:" in t and '"A"' in t:
            alice = json.loads(t.split("Intercepted from Alice:", 1)[1])
        elif "Intercepted from Bob:" in t:
            bob = json.loads(t.split("Intercepted from Bob:", 1)[1])
        elif "Intercepted from Alice:" in t and '"iv"' in t:
            enc = json.loads(t.split("Intercepted from Alice:", 1)[1])
    if alice and bob and enc:
        break
s.close()

A = int(alice["A"], 16)
B = int(bob["B"], 16)
g = int(alice["g"], 16)

# Additive DLP: a = A/g mod p  (multiply by inverse of g)
ginv = pow(g, -1, p)
a = A * ginv % p
b = B * ginv % p
secret = a * B % p
assert secret == (b * A % p), "additive DH consistency check failed"
print("a =", a)
print("b =", b)
print("secret =", secret)

# "Deriving Symmetric Keys" script (dh-starter-5 decrypt_provided.py)
sha1 = hashlib.sha1()
sha1.update(str(secret).encode("ascii"))
key = sha1.digest()[:16]
iv = bytes.fromhex(enc["iv"])
ct = bytes.fromhex(enc["encrypted"])
pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
n = pt[-1]
if 1 <= n <= 16 and pt[-n:] == bytes([n]) * n:
    pt = pt[:-n]  # strip valid PKCS7 padding
flag = pt.decode("ascii", "replace")
print("PLAINTEXT:", flag)
