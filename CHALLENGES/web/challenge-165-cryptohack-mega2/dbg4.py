import sys, os, json, traceback
base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base)
from harness import load_challenge

M = (1 << 1024) + 12345
ch = load_challenge(os.path.join(base, "13409.py"))
mat = json.loads([l for l in ch.before_input.split("\n") if l.startswith("{")][0])
n, e = mat["share_key_pub"]
ske = bytes.fromhex(mat["share_key_enc"])
mke = bytes.fromhex(mat["master_key_enc"])
h = "%x" % pow(M, e, n)
if len(h) % 2: h = "0" + h
SID_enc = bytes.fromhex(h)
for off in (647, 646, 645, 644, 643):
    bad = bytearray(ske); bad[off] ^= 0xFF
    ch.challenge({"action": "wait_login"})
    C_ = ch.C_
    try:
        sid = C_.login_step2(SID_enc, bytes(bad), mke)
        print("off", off, "OK sid len", len(sid))
    except Exception as ex:
        print("off", off, "EXC:", repr(ex)[:200])
        traceback.print_exc(limit=3)
