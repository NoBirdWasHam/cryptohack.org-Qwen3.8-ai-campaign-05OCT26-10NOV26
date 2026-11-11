#!/usr/bin/env python3
"""oh_snap — RC4 key = nonce || FLAG; oracle echoes keystream (ct=0 => cmd==keystream).
RC4 KSA reads K[i % n] for i in 0..255. If n = len(nonce)+len(FLAG) >= 256, the KSA reads
only K[0..255] = nonce || FLAG[0 : 256-len(nonce)]. So choosing len(nonce)=255-i makes the
KSA depend on FLAG[0..i] only. Recover FLAG byte-by-byte from the front, 256 local candidates
per byte, matched against one oracle keystream query per byte.
Stop when recovered byte == '}' (flag is crypto{...})."""
import urllib.request, json, sys
from Crypto.Cipher import ARC4

def keystream(nonce: bytes, m: int = 32) -> bytes:
    ct = "00" * m
    r = urllib.request.Request(
        "https://aes.cryptohack.org/oh_snap/send_cmd/%s/%s/" % (ct, nonce.hex()),
        headers={"User-Agent": "practice-run/1.0"})
    d = json.loads(urllib.request.urlopen(r, timeout=30).read().decode())
    if "error" in d and d["error"].startswith("Unknown command:"):
        return bytes.fromhex(d["error"].split(":")[1].strip())
    raise RuntimeError("no keystream: %r" % d)

def local_ks(key: bytes, m: int = 32) -> bytes:
    return ARC4.new(key).encrypt(b"\x00" * m)

known = b""
i = 0
while True:
    L = 255 - i
    if L < 1:
        print("exceeded", file=sys.stderr); break
    nonce = b"\x00" * L
    ks = keystream(nonce, 32)
    hit = None
    for c in range(256):
        key = nonce + known + bytes([c])          # exactly 256 bytes (255-i + i + 1)
        if local_ks(key, 32) == ks:
            hit = c
            break
    if hit is None:
        print("NO CANDIDATE at i=%d (L=%d)" % (i, L), file=sys.stderr)
        open("partial.txt", "wb").write(known)
        break
    known += bytes([hit])
    ch = chr(hit)
    print("i=%-2d L=%-3d byte=0x%02x %r  -> %s" % (i, L, hit, ch, known.decode(errors="replace")),
          file=sys.stderr, flush=True)
    if hit == ord("}") and known.startswith(b"crypto{"):
        break
    i += 1
    if i > 120:
        print("safety stop", file=sys.stderr); break

flag = known.decode(errors="replace")
print("\nFLAG:", flag)
open("flag.txt", "w").write(flag)

# ---- end-to-end self-check: random short nonce, compare local vs oracle ----
import os
check_nonce = os.urandom(16)
ks_o = keystream(check_nonce, 48)
ks_l = local_ks(check_nonce + flag.encode(), 48)
print("SELF-CHECK (16-byte random nonce, 48B):", "MATCH" if ks_o == ks_l else "MISMATCH")
if ks_o != ks_l:
    print("  oracle:", ks_o.hex(), file=sys.stderr)
    print("  local :", ks_l.hex(), file=sys.stderr)
