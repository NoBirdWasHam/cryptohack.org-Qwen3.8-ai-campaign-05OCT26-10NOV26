# Nibble-integral key recovery, DCTF2022 key_recovery cipher.
# per() permutes nibbles, so a 256-set varying one plaintext byte yields
# nibble-constrained active bytes at each layer. To test a key byte: shift that
# layer byte by the guess, map one round inward with per_inv; a constant inner
# partner byte stays constant only for the right key (wrong guess = nonlinear
# conjugate of a nibble set -> spreads over the samples).
# Bytes 3 and 15 form a closed 2-byte island of per (dest(3)=dest(15)={3,15}),
# so their round-key bytes are invisible to any integral test; the island also
# means island garbage never leaks outward. Recover k1/k2 (14 bytes each) + k0
# (14 bytes) this way, then brute force K[3],K[15] (2^16) against observed
# ciphertext; the sha512 key schedule confirms.
import os, sys, itertools
BASE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(BASE, "key_recovery.py")).read()
ns = {"__name__": "kr"}
exec(compile(src[:src.rindex("\nmain()")], "kr", "exec"), ns)
S_box, S_inv = ns["S_box"], ns["S_box_inv"]
per, per_inv = ns["per"], ns["per_inv"]
key_schedule, enc = ns["key_schedule"], ns["enc"]
P_box, P_box_inv = ns["P_box"], ns["P_box_inv"]
ISLAND = {3, 15}

def dest_bytes(i):
    return sorted({P_box_inv[2*i]//2, P_box_inv[2*i+1]//2})

def layer_bytes(i, rounds):
    cur = {i}
    for _ in range(rounds):
        cur = {d for b in cur for d in dest_bytes(b)}
    return sorted(cur)

def src_bytes(b):
    return sorted({P_box[2*b]//2, P_box[2*b+1]//2})

def testable(i, rounds):
    """(b, w): b active at layer `rounds` in for set with active byte i, with
    exactly one active inner source and one constant partner byte w."""
    L = set(layer_bytes(i, rounds))
    Lprev = set(layer_bytes(i, rounds - 1)) if rounds >= 1 else {i}
    out = []
    for b in sorted(L):
        if b in ISLAND:
            continue
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
            if b in ISLAND:
                continue
            need[(rounds, b)] = [i for i in range(16) if b in dict(testable(i, rounds))]
    chosen, uncovered = [], set(need)
    while uncovered:
        cand = [i for i in range(16) if i not in chosen
                and any(i in need[u] for u in uncovered)]
        if not cand:
            raise RuntimeError("cannot cover all non-island key bytes")
        best = max(cand, key=lambda i: sum(1 for u in uncovered if i in need[u]))
        chosen.append(best)
        uncovered -= {u for u in uncovered if best in need[u]}
    return chosen

def _guess_layer(samples, pairs):
    """samples: layer blocks W (= layer xor true key byte, exact values).
    For each (b, w): unique g keeping inner byte w constant over all samples."""
    rec = {}
    for b, w in pairs:
        cands = []
        for g in range(256):
            v = None
            good = True
            for s in samples:
                t = per_inv(s[:b] + bytes([s[b] ^ g]) + s[b+1:])[w]
                if v is None:
                    v = t
                elif t != v:
                    good = False
                    break
            if good:
                cands.append(g)
        if len(cands) == 1:
            rec[b] = cands[0]
    return rec

def attack(enc_fn, nverify=4):
    sets = choose_sets()
    data = {}
    for i in sets:
        pts = [bytes([a if j == i else 0 for j in range(16)]) for a in range(256)]
        data[i] = (pts, [enc_fn(p) for p in pts])
    k3 = {}
    for i in sets:
        W3s = [bytes([S_inv[c] for c in ct]) for ct in data[i][1]]
        k3.update(_guess_layer(W3s, testable(i, 3)))
    # z3 (garbage on island bytes -> u2/W2 valid off-island only)
    W2s = {i: [bytes([S_inv[v] for v in per_inv(bytes(
                    [S_inv[c ^ k3[j]] if j in k3 else 0 for j, c in enumerate(ct)]))])
               for ct in data[i][1]] for i in sets}
    k2 = {}
    for i in sets:
        k2.update(_guess_layer(W2s[i], testable(i, 2)))
    W1s = {i: [bytes([S_inv[v] if j not in ISLAND else 0 for j, v in enumerate(
                    per_inv(bytes([a ^ k2[j] if j in k2 else 0
                                   for j, a in enumerate(W2)])))])
            for W2 in W2s[i]] for i in sets}
    k1 = {}
    for i in sets:
        k1.update(_guess_layer(W1s[i], testable(i, 1)))
    if len(k1) < 14:
        return None, sets, "k1 %d/14 incomplete" % len(k1)
    i = sets[0]
    pts = data[i][0]
    k0 = {}
    for W1, pt in zip(W1s[i], pts):
        z1 = bytes([a ^ k1[j] if j in k1 else 0 for j, a in enumerate(W1)])
        u0 = per_inv(z1)
        for j in range(16):
            if j in ISLAND:
                continue
            kk = pt[j] ^ S_inv[u0[j]]
            if j not in k0:
                k0[j] = kk
            elif k0[j] != kk:
                return None, sets, "k0 byte %d inconsistent" % j
    if len(k0) < 14:
        return None, sets, "k0 %d/14 incomplete" % len(k0)
    ref_ct = data[i][1]
    probe = list(zip(pts[:nverify], ref_ct[:nverify]))
    K_cands = []
    for v3, v15 in itertools.product(range(256), repeat=2):
        K = bytes([v3 if j == 3 else v15 if j == 15 else k0[j] for j in range(16)])
        ok = True
        for pt, ct in probe:
            c = enc(K, pt)
            if c[3] != ct[3] or c[15] != ct[15]:
                ok = False
                break
        if ok:
            K_cands.append(K)
    if len(K_cands) != 1:
        return (K_cands[0] if len(K_cands) > 1 else None), sets, \
               "island brute force: %d candidates" % len(K_cands)
    return K_cands[0], sets, "ok"

if __name__ == "__main__":
    ntried = int(sys.argv[1]) if len(sys.argv) > 1 else 5
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
