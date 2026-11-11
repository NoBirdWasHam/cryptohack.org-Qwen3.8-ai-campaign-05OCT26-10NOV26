import sys, os, json, math
base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base)
from harness import load_challenge

ch = load_challenge(os.path.join(base, "13409.py"))
mat = json.loads([l for l in ch.before_input.split("\n") if l.startswith("{")][0])
n, e = mat["share_key_pub"]
ske = bytes.fromhex(mat["share_key_enc"])
mke = mat["master_key_enc"]
p_true, q_true = ch.C.share_key.p, ch.C.share_key.q
M = (1 << 1024) + 12345
bad = bytearray(ske)
for j in range(16): bad[160 + j] ^= 0xFF
h = "%x" % pow(M, e, n)
if len(h) % 2: h = "0" + h
ch.challenge({"action": "wait_login"})
r = ch.challenge({"action": "send_challenge", "SID_enc": h, "share_key_enc": bytes(bad).hex(), "master_key_enc": mke})
sid = bytes.fromhex(r["SID"])
m_top = int.from_bytes(sid, "big")
Y = m_top * (1 << 128) - M
print("p bits", p_true.bit_length(), "q bits", q_true.bit_length(), "p<q", p_true < q_true)
print("m_top bits", m_top.bit_length())
print("Y bits", Y.bit_length(), "Y>0", Y > 0)
# recover true m range: m = m_top*2^128 + r, r<2^128 ; m - M should be divisible by p
print("(Y mod p_true):", Y % p_true, " (should be ~ -r mod p, i.e. small-ish residue)")
print("Y + k*p small? try: (-Y) mod p =", (-Y) % p_true)
rlo = (-Y) % p_true
print("residue bits:", rlo.bit_length())
# what did enumeration see:
print("-(Y+2^127) bits:", (-(Y + (1<<127))).bit_length() if Y + (1<<127) < 0 else "pos")
print("isqrt(-(Y+2^127)) == p or q?", end=" ")
if Y + (1<<127) < 0:
    c = math.isqrt(-(Y + (1<<127)))
    print(c == p_true, c == q_true, " n%c ==", n % c)
