#!/usr/bin/env python3
"""triple_des — RECOVERY via DES complementation property.

Structure (from provided server source):
    C = E_K( P XOR IV ) XOR IV          (fixed 8-byte IV; K = my choice; DES3 ECB)
Flag: C_f = E_K( FLAG XOR IV ) XOR IV

DES (and DES3) complementation property:
    E_{K^1}( X^1 ) = E_K(X) ^ 1
where ^1 = bitwise complement (XOR 0xFF...FF).

Therefore:
    E_{K^1}( (FLAG XOR IV) ^ 1 ) = E_K( FLAG XOR IV ) ^ 1
So:
    enc_flag(K)   = E_K( F' )      XOR IV
    enc_flag(K^1) = E_K(F') ^ 1    XOR IV          [F' = FLAG XOR IV]
    => enc_flag(K) XOR enc_flag(K^1) = E_K(F') ^ 1
    => E_K(F') = (enc_flag(K) XOR enc_flag(K^1)) ^ 1
    => F' = DES3_K^-1( that )  = FLAG XOR IV
    => FLAG = F'  (the last byte is PKCS7 padding 0x08 since FLAG is a multiple of 8
       after pad() — strip one 0x08 byte of padding).
"""
import json, urllib.request
from Crypto.Cipher import DES3

BASE = "https://aes.cryptohack.org/triple_des"
def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "practice-run/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def comp(b): return bytes(x^0xFF for x in b)

# ---- 0) sanity: confirm complementation property holds for DES3 locally ----
K1=bytes(range(1,9)); K2=bytes(range(0x08,0x10)); K3=bytes(range(0x10,0x18))
K = K1+K2+K3; Kc = comp(K)
X = bytes(range(8))
E  = DES3.new(K,  DES3.MODE_ECB).encrypt(X)
Ec = DES3.new(Kc, DES3.MODE_ECB).encrypt(comp(X))
print("complementation holds for DES3:", comp(E)==Ec)

# ---- 1) get the two flag ciphertexts ----
Khex  = K.hex(); Khexc = Kc.hex()
cf  = bytes.fromhex(get("/encrypt_flag/%s/" % Khex)  ["ciphertext"])
cfc = bytes.fromhex(get("/encrypt_flag/%s/" % Khexc) ["ciphertext"])
print("len flag ct:", len(cf))

# ---- 2) recover E_K(F') per block = (cf ^ cfc) ^ 1 ----
Fp = b""
for i in range(0, len(cf), 8):
    e = comp(bytes(a^b for a,b in zip(cf[i:i+8], cfc[i:i+8])))
    Fp += DES3.new(K, DES3.MODE_ECB).decrypt(e)

# ---- 3) strip PKCS7 (last byte is 0x08; FLAG is exactly a multiple of 8 before padding) ----
if Fp[-1] == 0x08:
    FLAG = Fp[:-1]
else:
    FLAG = Fp
print("\nRecovered FLAG bytes:", FLAG)
print("FLAG (str):", FLAG.decode(errors="replace"))
# validate format
import re
m = re.fullmatch(r"crypto\{[0-9a-zA-Z_\-]+\}", FLAG.decode(errors="replace"))
print("format crypto{...}:", bool(m))
