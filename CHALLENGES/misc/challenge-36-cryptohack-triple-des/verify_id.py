#!/usr/bin/env python3
"""triple_des — verify the transform-level complementation identity (the 'strange weakness').

Server:  T_K(P) = W ^ E_K(P ^ W)   (W = fixed 8-byte IV, K = my choice, DES3 ECB)

DES/3DES complementation property:  E_{K^1}(X^1) = E_K(X) ^ 1   (1 = 0xFF..FF)

=>  T_{K^1}(P^1) = W ^ E_{K^1}((P^1)^W)
                 = W ^ E_{K^1}((P^W)^1)
                 = W ^ (E_K(P^W) ^ 1)          [complementation]
                 = (W ^ E_K(P^W)) ^ 1
                 = T_K(P) ^ 1

So the identity T_{K^1}(P^1) = T_K(P)^1 must hold for ANY P, ANY K.
This is a verifiable property that a secure block cipher (AES) would NOT have.
"""
import json, urllib.request

BASE = "https://aes.cryptohack.org/triple_des"
def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "practice-run/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def comp(b): return bytes(x^0xFF for x in b)

K1=bytes(range(1,9)); K2=bytes(range(8,16)); K3=bytes(range(16,24))
K=K1+K2+K3; Kc=comp(K)

def T(key, plain):
    return bytes.fromhex(get("/encrypt/%s/%s/" % (key.hex(), plain.hex()))["ciphertext"])

print("Verifying  T_{K^1}(P^1) == T_K(P)^1  for random P (live oracle):")
import os
ok = True
for i in range(6):
    P = os.urandom(8)
    lhs = T(Kc, comp(P))        # T_{K^1}(P^1)
    rhs = comp(T(K, P))          # T_K(P)^1
    good = (lhs == rhs)
    ok = ok and good
    print("  P=%s  %s" % (P.hex(), "OK" if good else "FAIL"))
print("IDENTITY HOLDS:", ok)

# Also confirm flag last block is a full 0x08 padding block (flag length multiple of 8)?
cf  = bytes.fromhex(get("/encrypt_flag/%s/" % K.hex())["ciphertext"])
zpad= bytes.fromhex(get("/encrypt/%s/%s/" % (K.hex(), "08"*8))["ciphertext"])
print("\nflag last block     :", cf[-8:].hex())
print("E(08*8) full block  :", zpad.hex())
print("flag len is multiple of 8 (last block == pad block)?", cf[-8:]==zpad)
print("flag ct total bytes:", len(cf), "(blocks:", len(cf)//8, ")")
