#!/usr/bin/env python3
"""triple_des live probes — minimal, read-only, documented requests."""
import json, urllib.request

BASE = "https://aes.cryptohack.org/triple_des"

def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "practice-run/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

# non-degenerate 3DES key: K1 != K2 != K3, K1 != K3
K1 = "0001020304050607"
K2 = "08090a0b0c0d0e0f"
K3 = "1011121314151617"
K  = K1 + K2 + K3

# 1) flag ciphertext under K
cf = get("/encrypt_flag/%s/" % K)
print("FLAG ct len:", len(cf["ciphertext"])//2, "bytes")
print("FLAG ct:", cf["ciphertext"])
ct = bytes.fromhex(cf["ciphertext"])
for i in range(0, len(ct), 8):
    print("  block %d: %s  ascii=%r" % (i//8, ct[i:i+8].hex(), bytes(b if 32<=b<127 else 0x2e for b in ct[i:i+8])))

# 2) structural checks: encrypt known plaintexts under K
print("\n-- structural probes --")
for name, plain in [
    ("zeros", "00"*8),
    ("08x8 ", "08"*8),
    ("crypto{0", "63727970746f7b30"),
]:
    r = get("/encrypt/%s/%s/" % (K, plain))
    print("%s -> %s" % (name, r.get("ciphertext", r)))

# 3) complementation property check: encrypt_flag under comp(K) should be comp(ct)
def comp(b): return bytes(x ^ 0xFF for x in b)
Kc = comp(bytes.fromhex(K)).hex()
cfc = get("/encrypt_flag/%s/" % Kc)
print("\ncomplement check: comp(FLAG_ct) == FLAG_ct under comp(K)? ",
      comp(ct).hex() == cfc["ciphertext"])
