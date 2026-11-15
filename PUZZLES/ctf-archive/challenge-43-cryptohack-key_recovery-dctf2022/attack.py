# Local validation of nibble-integral key recovery on the DCTF2022 cipher.
import os, random
BASE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(BASE, "key_recovery.py")).read()
# strip trailing main() invocation so import-safe
cut = src.rindex("\nmain()")
ns = {"__name__": "kr"}
exec(compile(src[:cut], "key_recovery.py", "exec"), ns)

S_box = ns["S_box"]; S_inv = ns["S_box_inv"]
per = ns["per"]; key_schedule = ns["key_schedule"]; enc = ns["enc"]

# --- nibble-flow structure of per ---
# per: out_nib[i] = P_nib[ in_nib[ P_box[i] ] ]  => input nibble n -> out pos P_box_inv[n]
P_box = ns["P_box"]; P_box_inv = ns["P_box_inv"]
dest_byte = [P_box_inv[n] // 2 for n in range(32)]
split = [ (n, n+1) for n in range(0, 32, 2) ]
print("byte i's two nibbles land in dest bytes:",
      [ (b, tuple(dest_byte[x] for x in pair)) for b, pair in enumerate(split) ])

def nibble_active(byte_set):
    """given set of active BYTES, return set of active bytes after per (byte-level approx: any nibble active)."""
    act = set()
    for b in byte_set:
        act.add(dest_byte[2*b]); act.add(dest_byte[2*b+1])
    return act

# propagation counts: 1 active byte -> per -> sub -> per -> ...
a = {0}
print("z1 active:", sorted(nibble_active(a)))
print("z2 active:", sorted(nibble_active(nibble_active(a))))
print("z3 active:", sorted(nibble_active(nibble_active(nibble_active(a)))))

# --- empirical structure check with random key ---
K = os.urandom(16)
ks = key_schedule(K)
k0, k1, k2, k3 = ks
act_byte = 0
pts = [bytes([a_ if i == act_byte else 0 for i in range(16)]) for a_ in range(256)]
cts = [enc(K, p) for p in pts]

def z_layer(cts):
    z3 = [bytes(S_inv[c] ^ k for c, k in zip(ct, k3)) for ct in cts]
    return z3
z3s = [bytes(S_inv[c] ^ k for c, k in zip(ct, k3)) for ct in cts]
z3_bytes_active = sorted({b for b in range(16) if len({z[b] for z in z3s}) > 1})
print("z3 active bytes:", z3_bytes_active)
def shares_nib(vals):
    hi = {v >> 4 for v in vals}; lo = {v & 15 for v in vals}
    return len(hi) == 1 or len(lo) == 1
ok = 0
for b in z3_bytes_active:
    vals = {z[b] for z in z3s}
    if shares_nib(vals): ok += 1
print(f"z3 active bytes sharing a nibble: {ok}/{len(z3_bytes_active)}")

# false positive check: guess k3 byte, test share-nibble
def guess_k3_bytes(z3_bytes_active):
    rec = {}
    for b in z3_bytes_active:
        cands = []
        for g in range(256):
            vals = {S_inv[ct[b] ^ g] for ct in cts}
            if len(vals) == 16 and shares_nib(vals):
                cands.append(g)
        rec[b] = cands
    return rec
r = guess_k3_bytes(z3_bytes_active)
print("k3 candidates unique?", all(len(v) == 1 and v[0] == k3[b] for b, v in r.items()))
