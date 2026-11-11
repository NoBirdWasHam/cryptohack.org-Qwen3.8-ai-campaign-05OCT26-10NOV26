import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "challenge-165-cryptohack-mega2"))
from harness import load_challenge
from Crypto.Util.number import long_to_bytes, bytes_to_long
from solve_mega3 import M, J
ch = load_challenge(os.path.join(HERE, "13410.py"))
mats = [json.loads(l) for l in ch.before_input.split("\n") if l.strip().startswith("{")]
mat, filemat, rec = mats
n, e = mat["share_key_pub"]; ske = bytes.fromhex(mat["share_key_enc"]); mke = mat["master_key_enc"]
X = bytes_to_long(filemat["node_key_enc"] and bytes.fromhex(filemat["node_key_enc"]))
p = rec["share_key"][2]; q = n // p
d = pow(e, -1, (p-1)*(q-1)); u = pow(q, -1, p)
print("p==C.p?", p == ch.C.share_key.p, "d==C.d?", d == ch.C.share_key.d, "u==C.u?", u == ch.C.share_key.u, flush=True)
data = b""
for num in (p, q, d, u):
    b = long_to_bytes(num); data += long_to_bytes(len(b), 2) + b
npad = 16 - len(data) % 16; data += bytes([npad])*npad
print("blob len", len(data), "ske len", len(ske), flush=True)
orig = bytes_to_long(data[J*16:(J+1)*16])
shift = 8*(648-(J+1)*16)
ug = (u + (X - orig)*(1 << shift)) % q
mp = M % p; mq = M % q; t = (mq - mp) % q
h = (t * ug) % q
m = h*p + mp
exp_top = m >> 128
bad = bytearray(ske); bad[J*16:(J+1)*16] = bytes.fromhex(filemat["node_key_enc"])
he = "%x" % pow(M, e, n)
if len(he) % 2: he = "0" + he
ch.challenge({"action": "wait_login"})
r = ch.challenge({"action": "send_challenge", "SID_enc": he, "share_key_enc": bytes(bad).hex(), "master_key_enc": mke})
print("resp keys", list(r.keys()), flush=True)
if "SID" in r:
    got = int.from_bytes(bytes.fromhex(r["SID"]), "big")
    print("SID match:", got == exp_top, "got bits", got.bit_length(), "exp bits", exp_top.bit_length(), flush=True)
