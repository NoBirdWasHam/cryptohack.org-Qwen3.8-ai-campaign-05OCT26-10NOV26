import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from harness import load_challenge
from solve_mega2_v2 import M
ch = load_challenge(os.path.join(HERE, "13409.py"))
mat = json.loads([l for l in ch.before_input.split("\n") if l.startswith("{")][0])
n, e = mat["share_key_pub"]; ske = bytes.fromhex(mat["share_key_enc"]); mke = mat["master_key_enc"]
# sanity: untampered challenge works?
h = "%x" % pow(M, e, n)
if len(h) % 2: h = "0" + h
ch.challenge({"action": "wait_login"})
r = ch.challenge({"action": "send_challenge", "SID_enc": h, "share_key_enc": ske.hex(), "master_key_enc": mke})
print("clean:", "SID" in r, int.from_bytes(bytes.fromhex(r["SID"]),"big") if "SID" in r else r, flush=True)
for off in (645, 644, 646, 640):
    ch.challenge({"action": "wait_login"})
    bad = bytearray(ske); bad[off] ^= 0xFF
    r = ch.challenge({"action": "send_challenge", "SID_enc": h, "share_key_enc": bytes(bad).hex(), "master_key_enc": mke})
    print("off", off, "->", list(r.keys()), (r["SID"][:40] if "SID" in r else r), flush=True)
    if ch.exit: print("EXITED"); break
