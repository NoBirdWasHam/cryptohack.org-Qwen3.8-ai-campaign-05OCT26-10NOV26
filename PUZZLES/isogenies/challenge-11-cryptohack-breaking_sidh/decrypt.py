"""Decrypt breaking_sidh flag from candidate shared-secret strings."""
import sys, hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

IV = bytes.fromhex('f45273daf12b8234bd41607d8b517913')
CT = bytes.fromhex('65917ae4d3de3ba753d50bab78992b2239cb189493807fcc3da8d058da1eda7d993c041d0ecb09089808d759a982f087')

def try_str(s):
    key = hashlib.sha256(s.encode()).digest()
    try:
        pt = unpad(AES.new(key, AES.MODE_CBC, IV).decrypt(CT), 16)
        if pt.startswith(b"crypto{"):
            return pt.decode()
    except Exception:
        pass
    return None

if __name__ == "__main__":
    for s in sys.argv[1:]:
        r = try_str(s)
        print(("HIT " + r) if r else f"miss: {s[:60]}")
