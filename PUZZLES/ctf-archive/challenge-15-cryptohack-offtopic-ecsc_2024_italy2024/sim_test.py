#!/usr/bin/env python3
# In-process self-test: drive the REAL offtopic.round() 128x with H = infinity
# and check our (m0,m1) recovery.
import json, io, builtins, random
from contextlib import redirect_stdout
import offtopic as O
from Crypto.PublicKey.ECC import EccPoint

K = 10**9
GX, GY = O.Gx, O.Gy
Q = O.q
G = O.G
KS = K*G
O.H = EccPoint(0, 0)   # malicious receiver pubkey = infinity

TABLE = {}
for m0 in range(10):
    for m1 in range(10):
        v = (m0*(1-K) + m1*K) % Q
        if v == 0:
            TABLE[(m0, m1)] = (0, 0)
        else:
            p = v*G
            TABLE[(m0, m1)] = (int(p.x), int(p.y))
assert len({v for v in TABLE.values()}) == 100, "table not injective"
BY_PT = {v: k for k, v in TABLE.items()}

real_input = builtins.input
random.seed(1234)
buf = io.StringIO()

class Feed:
    def input_cb(self, prompt):
        if "choice bit" in prompt:
            return json.dumps({"Rx": GX, "Ry": GY, "Sx": int(KS.x), "Sy": int(KS.y)})
        res = json.loads(buf.getvalue().strip().split("\n")[-1])
        m0, m1 = BY_PT[(res["Sx"], res["Sy"])]
        return json.dumps({"m0": m0, "m1": m1})

feed = Feed()
builtins.input = feed.input_cb
for r in range(128):
    buf.seek(0); buf.truncate()
    with redirect_stdout(buf):
        ok = O.round()
    assert ok, f"round {r} FAILED"
    if r % 16 == 0: print(f"sim round {r} OK", flush=True)
builtins.input = real_input
print("ALL 128 SIM ROUNDS PASSED")
