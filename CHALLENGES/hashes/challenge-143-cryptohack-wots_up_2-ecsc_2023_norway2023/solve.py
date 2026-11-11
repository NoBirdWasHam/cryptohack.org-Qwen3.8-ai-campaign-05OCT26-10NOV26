#!/usr/bin/env python
"""wots_up_2 (90 pts) — WOTS-256 signature forgery from 20 past transaction signatures.

The "fix" (independent priv_key elements) removed the seed-chain weakness, but the
safe now holds 20 past signatures of the SAME key. For chain position i (one of the
32 bytes of the SHA-256 hash of the message), each signature gives a point
sig_j[i] = H^(255 - b_j[i])(priv[i]) on the 256-link chain priv[i] -> ... -> pub[i],
where b_j[i] is byte i of SHA256(message_j). The closest known point to the private
key is at exponent e_i = 255 - B_i with B_i = max_j b_j[i]. Any needed point at
exponent >= e_i (i.e. b2[i] <= B_i) is reached by plain forward hashing.

With the provided data, b2[i] <= B_i for all 32 positions, so the whole signature2
(for "pub[0] sent 999999 WOTScoins to me") is forged by forward hashing only.
AES-CBC key = first byte of each signature2 element (per chal.py).
"""
import hashlib
import json
import os
import re
from Crypto.Cipher import AES

HERE = os.path.dirname(os.path.abspath(__file__))
H = lambda b: hashlib.sha256(b).digest()

data = json.load(open(os.path.join(HERE, "data_provided.json"), encoding="utf-8"))
pub = [bytes.fromhex(x) for x in data["public_key"]]
sigs = [[bytes.fromhex(x) for x in s["signature"]] for s in data["signatures"]]
msgs = [s["message"].encode() for s in data["signatures"]]
target = f"{data['public_key'][0]} sent 999999 WOTScoins to me".encode()

bs = [hashlib.sha256(m).digest() for m in msgs]
b2 = hashlib.sha256(target).digest()

sig2 = []
for i in range(32):
    B = max(bs[j][i] for j in range(len(bs)))
    assert b2[i] <= B, f"pos {i}: b2={b2[i]} > B={B} (would need a preimage)"
    # closest known point at exponent 255 - B (the one that hashed the most)
    jbest = max(range(len(bs)), key=lambda j: bs[j][i])
    steps = B - b2[i]
    x = sigs[jbest][i]
    for _ in range(steps):
        x = H(x)
    sig2.append(x)
    print(f"  sig2[{i:2d}] = H^{steps:3d}(sig_tx[{jbest:2d}][{i}])  (B={B}, b2={b2[i]})")

# verify against public key
ok = True
for i in range(32):
    v = sig2[i]
    for _ in range(b2[i] + 1):
        v = H(v)
    if v != pub[i]:
        ok = False
        print(f"  VERIFY FAIL at {i}")
print("forged signature verifies:", ok)
assert ok

key = bytes([s[0] for s in sig2])
iv = bytes.fromhex(data["iv"])
ct = bytes.fromhex(data["enc"])
raw = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
m = re.search(rb"(?:crypto|ECSC)\{[^}]*\}", raw)
flag = m.group(0) if m else raw
print("FLAG:", flag.decode())
open(os.path.join(HERE, "flag.txt"), "w").write(flag.decode() + "\n")
