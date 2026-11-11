import os
BASE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(BASE, "key_recovery.py")).read()
ns = {"__name__": "kr"}
exec(compile(src[:src.rindex("\nmain()")], "kr", "exec"), ns)
S_box, S_inv = ns["S_box"], ns["S_box_inv"]
per, key_schedule, enc = ns["per"], ns["key_schedule"], ns["enc"]
xor = ns["xor"]
K = os.urandom(16)
k0,k1,k2,k3 = key_schedule(K)
pts = [bytes([a if i==0 else 0 for i in range(16)]) for a in range(256)]
# compute layers by hand with true keys
u0s=[]; z1s=[]; u1s=[]; z2s=[]; u2s=[]; z3s=[]
for p in pts:
    u0 = bytes([S_box[a^k] for a,k in zip(p,k0)]); z1 = per(u0)
    u1 = bytes([S_box[a^k] for a,k in zip(z1,k1)]); z2 = per(u1)
    u2 = bytes([S_box[a^k] for a,k in zip(z2,k2)]); z3 = per(u2)
    u0s.append(u0); z1s.append(z1); u1s.append(u1); z2s.append(z2); u2s.append(u2); z3s.append(z3)
for name, layer in [("z1",z1s),("u1",u1s),("z2",z2s),("u2",u2s),("z3",z3s)]:
    for b in range(16):
        vs = {L[b] for L in layer}
        if len(vs) > 1:
            hi = {v>>4 for v in vs}; lo = {v&15 for v in vs}
            print(name, "byte", b, "distinct", len(vs), "hi-set", len(hi), "lo-set", len(lo))
