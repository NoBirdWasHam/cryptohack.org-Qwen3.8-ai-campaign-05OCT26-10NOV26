#!/usr/bin/env python3
"""triple_des (60 pts) — WEAK KEY attack.

Structure: C = W ^ E_K(P ^ W)  (W = 8-byte server IV, K = my chosen DES3 key).

DES has period-1 WEAK keys: for them ALL 16 round keys are identical, so the
encryption and decryption key schedules coincide  =>  E_K(X) == D_K(X), i.e.
E_K(E_K(X)) == X.  (AES has no such keys: "a strange weakness of DES which a
secure block cipher should not have".)

With a 16-byte DES3 key K1||K2 (K3=K1) where K1,K2 are weak:
    T(X) = E_{K1}(D_{K2}(E_{K1}(X))) = E_{K1}(E_{K2}(E_{K1}(X)))
and T(T(X)) == X  (each E is an involution).

Attack (2 queries):
    ct = enc_flag(K)      => ct = W ^ T(F ^ W)        (F = pad(FLAG))
    pt = enc(K, ct)       => pt = W ^ T(ct ^ W)
                          = W ^ T(T(F ^ W))
                          = W ^ (F ^ W)
                          = F = pad(FLAG)
Strip PKCS7 -> FLAG.
"""
import json
import urllib.request
from Crypto.Cipher import DES3

BASE = "https://aes.cryptohack.org/triple_des"

# 16-byte DES3 key: K1 = 8x00 (period-1 weak), K2 = 8xFF (period-1 weak), K3 = K1
WEAK = bytes(8) + bytes([0xFF] * 8)


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "practice-run/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def verify_weak_local():
    """E_K == D_K for each weak subkey, and T(T(X)) == X for the 3DES T."""
    ok_sub = []
    from Crypto.Cipher import DES
    for k in (bytes(8), bytes([0xFF] * 8)):  # the two weak DES subkeys used
        de = DES.new(k, DES.MODE_ECB)
        x = bytes(range(8))
        ok_sub.append(de.encrypt(x) == de.decrypt(x))
    # T(T(X)) == X with the real 16-byte DES3 key
    T = lambda X: DES3.new(WEAK, DES3.MODE_ECB).encrypt(X)
    x = bytes(range(8)) * 3
    tt = T(T(x))
    print("subkeys are involutions (E==D):", ok_sub)
    print("T(T(x)) == x:", tt == x)
    assert all(ok_sub) and tt == x


def main():
    verify_weak_local()
    khex = WEAK.hex()
    print("weak key:", khex)
    cf = bytes.fromhex(get("/encrypt_flag/%s/" % khex)["ciphertext"])
    print("flag ct len:", len(cf), "blocks:", len(cf) // 8)
    pt = bytes.fromhex(get("/encrypt/%s/%s/" % (khex, cf.hex()))["ciphertext"])
    print("recovered pad(FLAG):", pt)
    k = pt[-1]
    if 1 <= k <= 8 and pt[-k:] == bytes([k]) * k:
        flag = pt[:-k]
    else:
        flag = pt
    s = flag.decode(errors="replace")
    print("FLAG:", s)
    import re
    print("format crypto{...}:", bool(re.fullmatch(r"crypto\{[0-9a-zA-Z_\-]+\}", s)))
    with open("flag_recovered.txt", "w") as f:
        f.write(s)


if __name__ == "__main__":
    main()
