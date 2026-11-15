# Remote runner for DCTF2022 key_recovery: collects 8x256-block sets via the
# encryption oracle (option 1, batched as one 4096-byte hex line per set),
# runs the solve4 attack, then submits the key (option 3) to get the flag.
import socket, sys, time
import solve4 as s

def connect():
    sock = socket.create_connection(("archive.cryptohack.org", 44134), timeout=30)
    return sock

def recv_until(sock, marker):
    buf = b""
    while marker not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            raise RuntimeError("closed: " + repr(buf[-200:]))
        buf += chunk
    return buf

def encrypt_batch(sock, pts):
    data = b"".join(pts)
    sock.sendall(b"1\n")
    recv_until(sock, b"hex format:")
    sock.sendall(data.hex().encode() + b"\n")
    buf = recv_until(sock, b"Here you go:  ")
    if b"can't encrypt" in buf:
        raise RuntimeError("quota: " + buf.decode(errors="replace"))
    line = buf.split(b"Here you go:  ", 1)[1]
    while b"\n" not in line:
        ch = sock.recv(4096)
        if not ch:
            raise RuntimeError("closed mid-response")
        line += ch
    hexpart = line.split(b"\n")[0].strip()
    ct = bytes.fromhex(hexpart.decode())
    assert len(ct) == len(pts) * 16, (len(ct), len(pts))
    return [ct[16*i:16*i+16] for i in range(len(pts))]

def main():
    sock = connect()
    greet = recv_until(sock, b"> ")
    print(greet.decode(errors="replace")[-120:])
    sets = s.choose_sets()
    print("sets:", sets)
    data = {}
    for idx, i in enumerate(sets):
        pts = [bytes([a if j == i else 0 for j in range(16)]) for a in range(256)]
        cts = encrypt_batch(sock, pts)
        data[i] = (pts, cts)
        print("set", i, "done", flush=True)
    # ---- attack (mirrors solve4.attack but on precollected data) ----
    ISLAND, S_box, S_inv, per_inv = s.ISLAND, s.S_box, s.S_inv, s.per_inv
    def active_bytes(layers):
        return sorted({b for b in range(16) if len({L[b] for L in layers}) > 1} - ISLAND)
    k3 = {}
    for i in sets:
        cts = data[i][1]
        r = s._guess(cts, active_bytes(cts), lambda v, g: S_inv[v ^ g])
        for b, v in r.items():
            if v is not None and b not in k3:
                k3[b] = v
    print("k3:", len(k3), "bytes")
    z3s = {i: [bytes(S_inv[c ^ k3.get(j, 0)] for j, c in enumerate(ct)) for ct in data[i][1]]
           for i in sets}
    u2s = {i: [per_inv(z3) for z3 in z3s[i]] for i in sets}
    k2 = {}
    for i in sets:
        r = s._guess(u2s[i], active_bytes(u2s[i]), lambda v, g: S_inv[v ^ g])
        for b, v in r.items():
            if v is not None and b not in k2:
                k2[b] = v
    print("k2:", len(k2), "bytes")
    u1s = {i: [per_inv(bytes(S_inv[a ^ k2.get(j, 0)] for j, a in enumerate(u2)))
               for u2 in u2s[i]] for i in sets}
    k1 = {}
    for i in sets:
        r = s._guess(u1s[i], active_bytes(u1s[i]), lambda v, g: S_inv[v ^ g])
        for b, v in r.items():
            if v is not None and b not in k1:
                k1[b] = v
    print("k1:", len(k1), "bytes")
    assert len(k1) >= 14 and len(k2) >= 14 and len(k3) >= 14, (len(k1), len(k2), len(k3))
    k0 = {}
    for i in sets:
        for u1, pt in zip(u1s[i], data[i][0]):
            z1 = bytes(S_inv[a ^ k1.get(j, 0)] for j, a in enumerate(u1))
            u0 = per_inv(z1)
            for j in range(16):
                if j in ISLAND:
                    continue
                kk = u0[j] ^ S_box[pt[j]]
                assert k0.get(j, kk) == kk, "k0 inconsistent byte %d" % j
                k0[j] = kk
    print("k0:", len(k0), "bytes")
    # island brute force against observed ct on set 0 (closed island)
    i = sets[0]
    pts, cts = data[i]
    probe = list(zip(pts[:3], cts[:3]))
    import itertools
    good = []
    for v3, v15 in itertools.product(range(256), repeat=2):
        K = bytes([v3 if j == 3 else v15 if j == 15 else k0[j] for j in range(16)])
        ok = True
        for pt, ct in probe:
            c = s.enc(K, pt)
            if c[3] != ct[3] or c[15] != ct[15]:
                ok = False; break
        if ok:
            ks = s.key_schedule(K)
            if all(ks[r + 1][j] == {1: k1, 2: k2, 3: k3}[r + 1][j]
                   for r in (0, 1, 2) for j in range(16) if j not in ISLAND):
                good.append(K)
    print("island candidates:", len(good))
    if len(good) != 1:
        print("AMBIGUOUS:", [g.hex() for g in good])
        sys.exit(1)
    K = good[0]
    print("KEY:", K.hex())
    # full self-check against all collected pairs
    for i in sets:
        for pt, ct in list(zip(*data[i]))[:8]:
            assert s.enc(K, pt) == ct
    print("self-check ok; submitting key...")
    sock.sendall(b"3\n")
    recv_until(sock, b"hex format:")
    sock.sendall(K.hex().encode() + b"\n")
    time.sleep(2)
    resp = b""
    try:
        sock.settimeout(10)
        while True:
            ch = sock.recv(4096)
            if not ch:
                break
            resp += ch
    except Exception:
        pass
    print("RESPONSE:", resp.decode(errors="replace"))

if __name__ == "__main__":
    main()
