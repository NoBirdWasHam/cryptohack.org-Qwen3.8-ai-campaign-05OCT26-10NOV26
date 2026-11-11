import sys, os, json
base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base)
from harness import load_challenge
from Crypto.Cipher import AES

ch = load_challenge(os.path.join(base, "13409.py"))
mat = json.loads([l for l in ch.before_input.split("\n") if l.startswith("{")][0])
ske = bytes.fromhex(mat["share_key_enc"])
mk = ch.C.master_key
pt = AES.new(mk, AES.MODE_ECB).decrypt(ske)
print("len pt", len(pt))
print("tail:", pt[-24:].hex())
print("lens:", int.from_bytes(pt[0:2],'big'), int.from_bytes(pt[130:132],'big'),
      int.from_bytes(pt[260:262],'big'), int.from_bytes(pt[518:520],'big'))
print("byte647:", pt[647], "byte646:", pt[646], "byte644:", pt[644])
# compare with expected format
k = ch.C.share_key
from Crypto.Util.number import long_to_bytes
exp = b""
for x in (k.p, k.q, k.d, k.u):
    nb = long_to_bytes(x); exp += long_to_bytes(len(nb), 2) + nb
from Crypto.Util.Padding import pad
exp = pad(exp, 16)
print("matches expected:", exp == pt, "len exp", len(exp))
