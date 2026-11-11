#!/usr/bin/env python3
# put_a_ring_on_it (ECSC 2023 Norway) — break ring-signature anonymity.
# Bug: fake ring members' responses (sigc[i]=w, sigr[i]=q) are raw
# random.SystemRandom().getrandbits(256) values, NOT reduced mod the group
# order l (~2^252.3), so they exceed l with prob ~1-2^-4.33. The real signer's
# sigc=(c-sumc)%l and sigr=(q-sigc*sk)%l are always < l. So in each ring the
# unique index with BOTH sigc[i] < l and sigr[i] < l is the signer.
# AES key = first byte of the signer's pubkey in each of 16 levels.
import json
from itertools import product
from Crypto.Cipher import AES

L = 2**252 + 27742317777372353535851937790883648493  # ed25519 group order

d = json.load(open("data.json"))
cands = []
for lev in d["levels"]:
    image, sigc, sigr = lev["signature"]
    idxs = [i for i in range(16) if sigc[i] < L and sigr[i] < L]
    cands.append([lev["public_keys"][i][0:2] for i in idxs])
print("candidate counts per level:", [len(c) for c in cands])

iv = bytes.fromhex(d["iv"])
enc = bytes.fromhex(d["enc"])

def try_key(key):
    # Note: chal.py does NOT PKCS7-pad; flag was exactly 32 bytes.
    pt = AES.new(key, AES.MODE_CBC, iv).decrypt(enc)
    if pt and all(32 <= b < 127 for b in pt):
        return pt
    return None

sols = []
for combo in product(*cands):
    k = bytes.fromhex("".join(combo))
    pt = try_key(k)
    if pt:
        sols.append(pt.decode())
        if len(sols) > 1:
            break

if sols:
    flag = sols[0]
    print("FLAG:", flag)
    open("flag_put_a_ring_on_it-ecsc_2023_no.txt", "w").write(flag)
else:
    print("no plaintext candidate found")
