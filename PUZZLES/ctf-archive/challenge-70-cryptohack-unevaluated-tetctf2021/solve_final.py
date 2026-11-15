# Step 3: given c1 mod q (from NFS dlog), enumerate c1 candidates, recover k, decrypt
import json, math, sys
from Crypto.Cipher import AES

d = json.load(open("instance.json"))
p = int(d["p"]); q = int(d["q"]); r = int(d["r"]); k0 = int(d["k0"]); enc = bytes.fromhex(d["enc"])
c1q = int(sys.argv[1])  # c1 mod q
c1max = (2**256 - 1 - k0) // p
t = 0
while True:
    c1 = c1q + q*t
    if c1 > c1max: break
    k = k0 + p*c1
    assert k < 2**256
    key = k.to_bytes(32, "big")
    pt = AES.new(key, AES.MODE_ECB).decrypt(enc)
    printable = all(32 <= b < 127 or b == 0 for b in pt)
    ok = pt.endswith(b"\x00"*min(pt[-16:].count(b"\x00"), 16))
    if printable and (b"crypto{" in pt or b"flag" in pt or b"TET{" in pt or ok):
        print("CANDIDATE t =", t)
        print("k =", k)
        print("pt =", pt)
        print("FLAG:", pt.rstrip(b"\x00").decode("latin1"))
    t += 1
print("done, candidates tried:", t)
