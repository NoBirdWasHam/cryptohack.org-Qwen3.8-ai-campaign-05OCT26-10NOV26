import sys, os, json, math
base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base)
from harness import load_challenge

ch = load_challenge(os.path.join(base, "13409.py"))
mat = json.loads([l for l in ch.before_input.split("\n") if l.startswith("{")][0])
n, e = mat["share_key_pub"]
ske = bytes.fromhex(mat["share_key_enc"])
mke = mat["master_key_enc"]
print("remaining_logins", ch.remaining_logins)

# baseline: uncorrupted -> should return SID == M truncated
M = (1 << 1024) + 12345
h = "%x" % pow(M, e, n)
if len(h) % 2: h = "0" + h
ch.challenge({"action": "wait_login"})
r = ch.challenge({"action": "send_challenge", "SID_enc": h, "share_key_enc": ske.hex(), "master_key_enc": mke})
print("baseline:", str(r)[:80])

for off in (647, 646, 645, 644, 560, 520):
    bad = bytearray(ske); bad[off] ^= 0xFF
    ch.challenge({"action": "wait_login"})
    r = ch.challenge({"action": "send_challenge", "SID_enc": h, "share_key_enc": bytes(bad).hex(), "master_key_enc": mke})
    print("off", off, "->", str(r)[:100])
    if ch.remaining_logins == 0: break
