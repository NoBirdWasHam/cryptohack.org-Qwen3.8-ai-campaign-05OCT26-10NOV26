#!/usr/bin/env python3
"""triple_des — deeper structural probing (read-only, documented endpoints only)."""
import json, urllib.request

BASE = "https://aes.cryptohack.org/triple_des"
def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "practice-run/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

K1="0001020304050607"; K2="08090a0b0c0d0e0f"; K3="1011121314151617"
K  = K1+K2+K3
def comp_hex(h): return bytes(x^0xFF for x in bytes.fromhex(h)).hex()

cf  = get("/encrypt_flag/%s/" % K)["ciphertext"]
Kc  = comp_hex(K)
cfc = get("/encrypt_flag/%s/" % Kc)["ciphertext"]
ct  = bytes.fromhex(cf); ctc = bytes.fromhex(cfc)
print("flag under K  :", cf)
print("flag under K^1:", cfc)
# per-block XOR of the two
print("\nper-block C_i ^ C_i' (K vs K^1):")
for i in range(5):
    b = bytes(a^b_ for a,b_ in zip(ct[i*8:(i+1)*8], ctc[i*8:(i+1)*8]))
    print("  blk%d: %s" % (i, b.hex()))

# zero probe + padding probe under K
z = get("/encrypt/%s/%s/" % (K, "00"*8))["ciphertext"]
p8 = get("/encrypt/%s/%s/" % (K, "08"*8))["ciphertext"]
print("\nE_K(IV)^IV  (zero probe)   :", z)
print("E_K(08..^IV)^IV (pad probe):", p8)
print("flag block4 (last)         :", ct[32:40].hex())
print("flag block4 == pad probe?   ", ct[32:40].hex()==p8)
print("flag block0 (first)        :", ct[0:8].hex())

# Does the last block look like all-padding? If flag is 32 bytes, block4 == pad probe.
# Also test: does complementing the PLAINTEXT (not key) give the clean property?
# encrypt under K of plaintext (08..^1 = 77..) and compare to comp of pad probe
p77 = get("/encrypt/%s/%s/" % (K, "77"*8))["ciphertext"]
print("\ncomplement property (single block): comp(E_K(08..)) == E_K(77..)?",
      bytes(x^0xFF for x in bytes.fromhex(p8)).hex()==p77)
