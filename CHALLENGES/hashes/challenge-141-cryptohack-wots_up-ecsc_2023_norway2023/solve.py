#!/usr/bin/env python
"""wots_up (75 pts) — WOTS-256 signature forgery via the seeded priv-key chain.

Weakness: in __init__, priv_key elements are successive hashes of one seed:
    priv[0] = H(seed), priv[1] = H^2(seed), ..., priv[31] = H^32(seed)
So every sig1[i] = H^(255-b1[i])(priv[i]) sits at chain position p1[i] = 256 + i - b1[i]
on ONE chain from the seed. Any chain element at position >= min(p1) is reachable by
forward hashing from the known sig1 elements. The target signature for "Sign for flag"
needs position p2[i] = 256 + i - b2[i]; with the provided data all p2[i] >= min(p1),
so the whole signature2 is forged by forward hashing only.

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
sig1 = [bytes.fromhex(x) for x in data["signature"]]
m1 = data["message"].encode()
assert m1 == b"WOTS Up???"
m2 = b"Sign for flag"

b1 = hashlib.sha256(m1).digest()
b2 = hashlib.sha256(m2).digest()

# chain position of each known sig1 element (position k = H^k(seed), seed at 0)
p1 = [256 + i - b1[i] for i in range(32)]
pmin = min(p1)
print("Pmin =", pmin)

# forge signature2
sig2 = []
for i in range(32):
    target = 256 + i - b2[i]
    assert target >= pmin, f"pos {i}: target {target} < Pmin {pmin}"
    # closest known element at or below target position
    best = max(j for j in range(32) if p1[j] <= target)
    steps = target - p1[best]
    x = sig1[best]
    for _ in range(steps):
        x = H(x)
    sig2.append(x)
    print(f"  sig2[{i:2d}] = H^{steps:3d}(sig1[{best:2d}])  (target pos {target})")

# verify the forged signature against the public key (WOTS verify)
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

# decrypt the flag
key = bytes([s[0] for s in sig2])
iv = bytes.fromhex(data["iv"])
ct = bytes.fromhex(data["enc"])
raw = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
# flag is block-aligned (exactly 32 bytes) with NO PKCS7 padding in this challenge
m = re.search(rb"(?:crypto|ECSC)\{[^}]*\}", raw)
flag = m.group(0) if m else raw
print("FLAG:", flag.decode())
open(os.path.join(HERE, "flag.txt"), "w").write(flag.decode() + "\n")
