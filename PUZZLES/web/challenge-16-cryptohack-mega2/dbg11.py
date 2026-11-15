import sys, os, json, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from harness import load_challenge
from Crypto.Util.Padding import unpad
from Crypto.Util.number import bytes_to_long
ch = load_challenge(os.path.join(HERE, "13409.py"))
C = ch.C
ske = C.share_key_enc
mk = C.master_key
from Crypto.Cipher import AES
pt = AES.new(mk, AES.MODE_ECB).decrypt(ske)
print("pt len", len(pt), "tail", pt[-24:].hex(), flush=True)
# parse layout
idx = 0
for name in ("p","q","d","u"):
    ln = bytes_to_long(pt[idx:idx+2]); print(name, "len", ln, "at", idx+2, "..", idx+2+ln, flush=True); idx += 2+ln
print("pad bytes", pt[idx:].hex(), flush=True)
bad = bytearray(ske); bad[645] ^= 0xFF
ptb = AES.new(mk, AES.MODE_ECB).decrypt(bytes(bad))
print("tampered pt diff at", [i for i in range(len(pt)) if pt[i]!=ptb[i]], flush=True)
try:
    sh = unpad(ptb, 16)
    p, q, d, u = C_ = None, None, None, None
    idx = 0; els = []
    while idx < len(sh):
        ln = bytes_to_long(sh[idx:idx+2]); idx += 2
        els.append(bytes_to_long(sh[idx:idx+ln])); idx += ln
    print("parsed ok, els", [e.bit_length() for e in els], flush=True)
except Exception:
    traceback.print_exc()
