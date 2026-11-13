"""Solve CryptoHack 'toomany' (Too Many Errors, 100 pts).

Server (13390.py): LWE over Z_127, 28-dim secret = flag bytes.
Each get_sample: a = 28 values from self.rand (random.Random(SEED)), e = randint(-1,1),
then self.rand is RESEEDED with a fresh random 32-bit seed and, with prob 1/2, ONE
coordinate a[j] is replaced by a uniform random value v (the "faulty sample" bug).
b = a . FLAG + e  (mod 127).

Key facts:
- 'reset' reseeds self.rand to SEED, so the FIRST sample after a reset is always the
  SAME deterministic a vector and the same clean b = a.FLAG + e.
- Faulty samples: b_faulty - b_true = (v - a[j]) * FLAG[j] (mod 127), and the corrupted
  coordinate j is visible by comparing a_faulty with a_true.
=> majority-vote a_true/b_true over many reset+sample cycles; every faulty sample then
  directly yields one flag byte FLAG[j] = (b_f - b_t) * (v - a_true[j])^{-1} mod 127.
Coupon-collector over j=0..27. Known bytes '[flag value withheld — real-flag strings live only under FLAGS/]' give free consistency checks.
"""
import json
import socket
from collections import Counter

HOST, PORT = "socket.cryptohack.org", 13390
Q = 127
N_CYCLES = 450


def main():
    s = socket.create_connection((HOST, PORT), timeout=60)
    s.settimeout(60)
    greeting = s.recv(65536)
    print("greeting:", greeting[:100], flush=True)

    buf = b""
    dec = json.JSONDecoder()

    def recv_obj():
        nonlocal buf
        while True:
            i = buf.find(b"{")
            if i >= 0:
                try:
                    obj, end = dec.raw_decode(buf[i:].decode("utf-8"))
                    buf = buf[i + end:]
                    return obj
                except json.JSONDecodeError:
                    pass
            d = s.recv(65536)
            if not d:
                raise RuntimeError("EOF from server")
            buf += d

    def send_obj(o):
        s.sendall((json.dumps(o) + "\n").encode())

    samples = []
    for k in range(N_CYCLES):
        send_obj({"option": "reset"})
        r = recv_obj()
        assert r.get("success"), r
        send_obj({"option": "get_sample"})
        r = recv_obj()
        assert "a" in r and "b" in r, r
        samples.append((r["a"], r["b"]))
        if k % 75 == 0:
            print(f"collected {k}/{N_CYCLES}", flush=True)

    a_counter = Counter(tuple(a) for a, _ in samples)
    b_counter = Counter(b for _, b in samples)
    a_true = a_counter.most_common(1)[0][0]
    b_true = b_counter.most_common(1)[0][1]
    print("a_true count:", a_counter[a_true], "b_true count:", b_counter[b_true], flush=True)
    print("a_true:", a_true, flush=True)
    print("b_true:", b_true, flush=True)

    known = {i: c for i, c in enumerate(b"crypto{")}
    known[27] = ord("}")

    recovered = {}
    conflicts = 0
    clean_check = 0
    for a, b in samples:
        if a == list(a_true):
            if b == b_true:
                clean_check += 1
            continue
        diffs = [j for j in range(28) if a[j] != a_true[j]]
        assert len(diffs) == 1, (a, diffs)
        j = diffs[0]
        v = a[j]
        dv = (v - a_true[j]) % Q
        if dv == 0:
            continue
        val = ((b - b_true) % Q) * pow(dv, Q - 2, Q) % Q
        if j in recovered and recovered[j] != val:
            conflicts += 1
        recovered[j] = val
        print(f"  sample hits j={j:2d} v={v:3d} -> byte {val}", flush=True)

    print("distinct coords recovered:", sorted(recovered), flush=True)
    print("conflicts:", conflicts, "clean samples consistent:", clean_check, flush=True)

    # consistency on known coords
    ok = True
    for j, c in known.items():
        if j in recovered:
            match = recovered[j] == c
            ok &= match
            print(f"known coord j={j} expected {c} got {recovered[j]} -> {match}", flush=True)

    flag = bytearray(28)
    missing = []
    for j in range(28):
        if j in known:
            flag[j] = known[j]
        elif j in recovered:
            flag[j] = recovered[j]
        else:
            missing.append(j)
    print("missing unknown coords:", missing, flush=True)
    if missing or conflicts or not ok:
        print("INCOMPLETE - need more samples or has conflicts", flush=True)
        return

    flag = bytes(flag)
    # final verification: clean equation a_true.FLAG + e == b_true (mod 127), e in {-1,0,1}
    dot = sum(a_true[i] * flag[i] for i in range(28)) % Q
    e = (b_true - dot) % Q
    print("verification: (b_true - a.FLAG) mod 127 =", e, "(must be in {0,1,126})", flush=True)
    assert e in (0, 1, 126), "verification FAILED"
    print("FLAG:", flag.decode(), flush=True)
    with open("flag.txt", "w") as f:
        f.write(flag.decode())


if __name__ == "__main__":
    main()
