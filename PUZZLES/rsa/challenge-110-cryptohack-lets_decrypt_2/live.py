#!/usr/bin/env python3
import socket, json, hashlib
from solve import solve, pick_modulus

HOST, PORT = "socket.cryptohack.org", 13394
s = socket.create_connection((HOST, PORT), timeout=60)
f = s.makefile("rwb")
print("PRE:", f.readline().decode(errors="replace").strip()[:100])

def send(obj):
    f.write((json.dumps(obj) + "\n").encode()); f.flush()
    return json.loads(f.readline().decode())

r = send({"option": "get_signature"})
SIG = int(r["signature"], 16)
p, k, N_MOD = pick_modulus(SIG)
print(f"SIG mod 3 = {SIG%3}; using p={p} k={k}")

r = send({"option": "set_pubkey", "pubkey": hex(N_MOD)})
print("set_pubkey:", r.get("status"), r.get("error", ""))
suffix = r["suffix"]
print("suffix:", suffix)

shares = []
for i, e, msg in solve(SIG, suffix):
    c = send({"option": "claim", "msg": msg, "e": hex(e), "index": i})
    print(f"claim gate {i}:", c.get("msg"), c.get("error", ""))
    if "secret" in c:
        shares.append(bytes.fromhex(c["secret"]))
    else:
        raise SystemExit(f"gate {i} failed: {c}")
    if len(shares) == 3:
        break

flag = bytes(x ^ y ^ z for x, y, z in zip(*shares))
print("FLAG:", flag.decode(errors="replace"))
with open("flag_lets_decrypt_2.txt", "wb") as fh:
    fh.write(flag)
s.close()
