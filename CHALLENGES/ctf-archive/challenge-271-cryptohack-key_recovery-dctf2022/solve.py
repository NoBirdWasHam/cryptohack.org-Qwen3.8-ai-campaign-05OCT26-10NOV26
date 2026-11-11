# Nibble-integral key recovery, DCTF2022 key_recovery cipher.
# Attack: per() is a nibble permutation, so for a 256-set varying one plaintext
# byte, active bytes at each z-layer are nibble-constrained. To test a key byte:
# shift the candidate byte at a layer, map one round inward with per_inv; the
# constant inner partner byte stays constant only for the right key (wrong key =
# nonlinear conjugate image of the nibble set -> spreads). Recover k3,k2,k1 this
# way; k0 then falls out exactly (k0 = x xor S_inv[per_inv[z1]]).
import os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(BASE, "key_recovery.py")).read()
ns = {"__name__": "kr"}
exec(compile(src[:src.rindex("\nmain()")], "kr", "exec"), ns)
S_box, S_inv = ns["S_box"], ns["S_box_inv"]
per, per_inv = ns["per"], ns["per_inv"]
key_schedule, enc = ns["key_schedule"], ns["enc"]
P_box_inv = ns["P_box_inv"]

def dest_bytes(i):
    return sorted({P_box_inv[2*i]//2, P_box_inv[2*i+1]//2})

def layer_bytes(i, rounds):
    cur = {i}
    for _ in range(rounds):
        cur = {d for b in cur for d in dest_bytes(b)}
    return sorted(cur)

def src_bytes(b):
    P_box = ns["P_box"]
    return sorted({P_box[2*b]//2, P_box[2*b+1]//2})

def testable(i, rounds):
    """layer bytes (rounds of per in) testable from set with active byte i:
    b active, exactly one of b's inner source bytes active -> return (b, w)."""
    L = set(layer_bytes(i, rounds))
    Lprev = set(layer_bytes(i, rounds - 1)) if rounds >= 1 else {i}
    out = []
    for b in sorted(L):
        s = src_bytes(b)
        act = [x for x in s if x in Lprev]
        const = [x for x in s if x not in Lprev]
        if len(act) == 1 and len(const) == 1:
            out.append((b, const[0]))
    return out

def choose_sets():
    need = {}
    for rounds in (3, 2, 1):
        for b in range(16):
            need[(rounds, b)] = [i for i in range(16) if b in dict(testable(i, rounds))]
    chosen, uncovered = [], {(r, b) for r in (3, 2, 1) for b in range(16)}
    while uncovered:
        best = max((i for i in range(16) if i not in chosen),
                   key=lambda i: sum(1 for u in uncovered if i in need[u]))
        if not any(best in need[u] for u in uncovered):
            raise RuntimeError("cannot cover all key bytes with 256-sets")
        chosen.append(best)
        uncovered -= {u for u in uncovered if best in need[u]}
    return chosen

def _guess_layer(samples, pairs):
    """samples: list of layer blocks W (value = layer xor true key, exact).
    pairs: [(b,w)]. Returns {b: keybyte} for uniquely-determined b."""
    rec = {}
    for b, w in pairs:
        cands = []
        for g in range(256):
            v0 = per_inv(samples[0][:b] + bytes([samples[0][b] ^ g]) + samples[0][b+1:])[w]
            good = all(len({per_inv(s[:b] + bytes([s[b] ^ g]) + s[b+1:])[w] for s in samples}) == 1
                       and per_inv(s[:b] + bytes([s[b] ^ g]) + s[b+1:])[w] == v0
                       for s in samples[1:])
            if good:
                cands.append(g)
        if len(cands) == 1:
            rec[b] = cands[0]
    return rec

def attack(enc_fn):
    sets = choose_sets()
    data = {}
    for i in sets:
        pts = [bytes([a if j == i else 0 for j in range(16)]) for a in range(256)]
        data[i] = (pts, [enc_fn(p) for p in pts])
    # W3 = S_inv[ct] = z3 xor k3 (exact, key-free up to xor)
    k3 = {}
    for i in sets:
        pts, cts = data[i]
        W3s = [bytes([S_inv[c] for c in ct]) for ct in cts]
        k3.update(_guess_layer(W3s, testable(i, 3)))
    if len(k3) < 16:
        return None, sets, "k3 %d/16" % len(k3)
    W2s = {i: [bytes([S_inv[v] for v in per_inv(bytes([S_inv[c ^ k3[j]] for j, c in enumerate(ct)]))])
               for ct in data[i][1]] for i in sets}
    k2 = {}
    for i in sets:
        k2.update(_guess_layer(W2s[i], testable(i, 2)))
    if len(k2) < 16:
        return None, sets, "k2 %d/16" % len(k2)
    W1s = {i: [bytes([S_inv[v] for v in per_inv(bytes([a ^ k2[j] for j, a in enumerate(W2)]))])
               for W2 in W2s[i]] for i in sets}
    k1 = {}
    for i in sets:
        k1.update(_guess_layer(W1s[i], testable(i, 1)))
    if len(k1) < 16:
        return None, sets, "k1 %d/16" % len(k1)
    i = sets[0]
    pts = data[i][0]
    k0 = None
    for W1, pt in zip(W1s[i], pts):
        z1 = bytes([a ^ k1[j] for j, a in enumerate(W1)])
        u0 = per_inv(z1)
        kk = bytes([pt[j] ^ S_inv[u0[j]] for j in range(16)])
        if k0 is None:
            k0 = kk
        elif kk != k0:
            return None, sets, "k0 inconsistent"
    if bytes(k1.values()) != b"".join(bytes([k1[j]]) for j in range(16)):
        k1b = bytes([k1[j] for j in range(16)])
    else:
        k1b = bytes([k1[j] for j in range(16)])
    k2b = bytes([k2[j] for j in range(16)])
    k3b = bytes([k3[j] for j in range(16)])
    if key_schedule(k0) != [k0, k1b, k2b, k3b]:
        return None, sets, "k0 fails sha512 key-schedule check"
    return k0, sets, "ok"

if __name__ == "__main__":
    ntried = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    sets = choose_sets()
    print("sets:", sets, "blocks:", 256 * len(sets))
    nOK = 0
    for t in range(ntried):
        K = os.urandom(16)
        Krec, _, msg = attack(lambda p: enc(K, p))
        if Krec == K:
            nOK += 1
        else:
            print("trial", t, "FAIL:", msg)
    print(f"{nOK}/{ntried} recovered")
