# Key recovery, DCTF2022 "key_recovery" (v4, CORRECT round order).
# Cipher: u_r = S(z_{r-1}) ^ k_r ; z_r = per(u_r) ; ct = S(z3) ^ k3.
# key_schedule: k0=K, k1|k2|k3 = sha512(K)[0:48].
# per is a nibble permutation: a 256-set (vary plaintext byte i) makes every
# active byte at z1,z2,z3 nibble-CONFINED (one fixed nibble, <=16 values,
# multiplicity 16). Since the key XOR sits AFTER the S-box, guessing a round
# key byte b applies XOR on the S-box OUTPUT side while the confined structure
# lives on the INPUT side -> conjugation invariance does NOT apply:
#   predicate: confined(candidate_layer_byte) is an 8-bit-sensitive test.
# Layers are peeled exactly: z3 = S[ct^k3], u2=per_inv(z3), z2=Sinv[u2^k2], ...
# Bytes {3,15} form a closed island of per (dest(3)=dest(15)={3,15}) -> their
# key bytes untestable; island never contaminates other bytes, so recover 14
# bytes of K directly and brute force K[3],K[15] (2^16) vs observed ct;
# sha512 key schedule verifies.
import os, sys, itertools
BASE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(BASE, "key_recovery.py")).read()
ns = {"__name__": "kr"}
exec(compile(src[:src.rindex("\nmain()")], "kr", "exec"), ns)
S_box, S_inv = ns["S_box"], ns["S_box_inv"]
per, per_inv = ns["per"], ns["per_inv"]
key_schedule, enc = ns["key_schedule"], ns["enc"]
ISLAND = {3, 15}

def confined(vals):
    return len({v >> 4 for v in vals}) == 1 or len({v & 15 for v in vals}) == 1

def _guess(samples, active, gfun):
    """samples: per-set list of 256 exact layer blocks. active: bytes to test.
    gfun(bytevalue, g) -> candidate layer byte value."""
    rec = {}
    for b in active:
        cands = []
        for g in range(256):
            vals = set()
            good = True
            for sx in samples:
                vals.add(gfun(sx[b], g))
                if len(vals) >= 3 and not confined(vals):
                    good = False
                    break
            if good and 3 <= len(vals) <= 20:
                cands.append(g)
        if len(cands) == 1:
            rec[b] = cands[0]
        elif cands:
            rec[b] = None
    return rec

def choose_sets():
    targets = set(range(16)) - ISLAND
    P_box_inv = ns["P_box_inv"]
    def dest(i):
        return {P_box_inv[2*i]//2, P_box_inv[2*i+1]//2} - ISLAND
    chosen, cov = set(), set()
    while cov != targets:
        best = max((i for i in range(16) if i not in chosen and i not in ISLAND),
                   key=lambda i: len(dest(i) - cov))
        if not dest(best) - cov:
            raise RuntimeError("coverage stuck")
        chosen.add(best); cov |= dest(best)
    return sorted(chosen)

def attack(enc_fn):
    sets = choose_sets()
    data = {}
    for i in sets:
        pts = [bytes([a if j == i else 0 for j in range(16)]) for a in range(256)]
        data[i] = (pts, [enc_fn(p) for p in pts])
    def active_bytes(layers):
        return sorted({b for b in range(16) if len({L[b] for L in layers}) > 1} - ISLAND)
    # stage k3: candidate z3 byte = S_box[ct_b ^ g]
    k3 = {}
    z3s = {}
    for i in sets:
        cts = data[i][1]
        act = active_bytes(cts)
        r = _guess(cts, act, lambda v, g: S_inv[v ^ g])
        for b, v in r.items():
            if v is not None:
                k3.setdefault(b, v)
            if b not in k3:
                k3[b] = None
        k3 = {b: v for b, v in k3.items() if v is not None}
    if len(k3) < 14:
        return None, sets, "k3 %d/14" % len(k3)
    for i in sets:
        cts = data[i][1]
        z3s[i] = [bytes(S_inv[c ^ k3.get(j, 0)] for j, c in enumerate(ct)) for ct in cts]
    # stage k2: u2 = per_inv(z3); candidate z2 byte = S_inv[u2_b ^ g]
    k2 = {}
    u2s = {i: [per_inv(z3) for z3 in z3s[i]] for i in sets}
    for i in sets:
        r = _guess(u2s[i], active_bytes(u2s[i]), lambda v, g: S_inv[v ^ g])
        for b, v in r.items():
            if v is not None and b not in k2:
                k2[b] = v
    if len(k2) < 14:
        return None, sets, "k2 %d/14" % len(k2)
    # z2 = S_inv[u2 ^ k2] elementwise, then u1 = per_inv(z2)
    u1s = {}
    for i in sets:
        u1s[i] = [per_inv(bytes(S_inv[a ^ k2.get(j, 0)] for j, a in enumerate(u2)))
                  for u2 in u2s[i]]
    k1 = {}
    for i in sets:
        r = _guess(u1s[i], active_bytes(u1s[i]), lambda v, g: S_inv[v ^ g])
        for b, v in r.items():
            if v is not None and b not in k1:
                k1[b] = v
    if len(k1) < 14:
        return None, sets, "k1 %d/14" % len(k1)
    # z1 = S_inv[u1 ^ k1]; u0 = per_inv(z1); k0 = u0 ^ S[x]
    k0 = {}
    for i in sets:
        for u1, pt in zip(u1s[i], data[i][0]):
            z1 = bytes(S_inv[a ^ k1.get(j, 0)] for j, a in enumerate(u1))
            u0 = per_inv(z1)
            for j in range(16):
                if j in ISLAND:
                    continue
                kk = u0[j] ^ S_box[pt[j]]
                if j in k0 and k0[j] != kk:
                    return None, sets, "k0 byte %d inconsistent" % j
                k0[j] = kk
    if len(k0) < 14:
        return None, sets, "k0 %d/14" % len(k0)
    # island brute force vs ct (bytes 3,15) on one set
    i = sets[0]
    pts, cts = data[i]
    probe = list(zip(pts[:3], cts[:3]))
    Kc = []
    for v3, v15 in itertools.product(range(256), repeat=2):
        K = bytes([v3 if j == 3 else v15 if j == 15 else k0[j] for j in range(16)])
        if all((c := enc_fn(pt))[3] == ct[3] and c[15] == ct[15] for pt, ct in probe):
            Kc.append(K)
    # verify sha512 schedule on non-island bytes
    good = []
    for K in Kc:
        ks = key_schedule(K)
        if all(ks[r+1][j] == {1: k1, 2: k2, 3: k3}[r+1][j]
               for r in (0, 1, 2) for j in range(16) if j not in ISLAND):
            good.append(K)
    if len(good) != 1:
        return (good[0] if good else None), sets, "island: %d good" % len(good)
    return good[0], sets, "ok"

if __name__ == "__main__":
    ntried = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    sets = choose_sets()
    print("sets:", sets, "blocks:", 256*len(sets))
    nOK = 0
    for t in range(ntried):
        K = os.urandom(16)
        Krec, _, msg = attack(lambda p: enc(K, p))
        if Krec == K:
            nOK += 1
        else:
            print("trial", t, "FAIL:", msg)
    print(f"{nOK}/{ntried} recovered")
