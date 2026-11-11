import sys, os, json, math
base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base)
from harness import load_challenge

M = (1 << 1024) + 12345
for off in (None, 647, 646, 645, 644, 560, 520, 519, 518):
    ch = load_challenge(os.path.join(base, "13409.py"))   # fresh: resets logins
    mat = json.loads([l for l in ch.before_input.split("\n") if l.startswith("{")][0])
    n, e = mat["share_key_pub"]
    ske = bytes.fromhex(mat["share_key_enc"])
    mke = mat["master_key_enc"]
    h = "%x" % pow(M, e, n)
    if len(h) % 2: h = "0" + h
    bad = bytearray(ske)
    if off is not None: bad[off] ^= 0xFF
    ch.challenge({"action": "wait_login"})
    r = ch.challenge({"action": "send_challenge", "SID_enc": h, "share_key_enc": bytes(bad).hex(), "master_key_enc": mke})
    if "SID" in r:
        sid = bytes.fromhex(r["SID"])
        print("off", off, "-> SID", len(sid), "bytes, top:", r["SID"][:32])
    else:
        print("off", off, "->", r)
