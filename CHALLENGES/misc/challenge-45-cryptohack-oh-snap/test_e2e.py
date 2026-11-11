#!/usr/bin/env python3
"""Local end-to-end test of the two-round pipeline against a synthetic flag."""
import sys, json, random, time
from collections import Counter
from Crypto.Cipher import ARC4
import solve_oh_snap as S

FLAG = sys.argv[3].encode() if len(sys.argv) > 3 else b"crypto{sn4p_snap_rc4_bites_h4rd}"
N1 = int(sys.argv[1]) if len(sys.argv) > 1 else 60000
N2 = int(sys.argv[2]) if len(sys.argv) > 2 else 60000
RLEN = 4
M = 96
rng = random.Random(123)

def synth(prefix, count, fname):
    with open(fname, "w") as fh:
        for _ in range(count):
            R = bytes(rng.randrange(256) for _ in range(RLEN))
            N = R + prefix
            ks = ARC4.new(N + FLAG).decrypt(b"\x00" * M)
            fh.write(json.dumps({"n": N.hex(), "k": ks.hex()}) + "\n")

t0 = time.time()
synth(b"crypto{", N1, "r1.jsonl")
print(f"round1 synth {N1} in {time.time()-t0:.1f}s")
samples = S.load_samples("r1.jsonl")
held = samples[-20:]
table = S.build_table(samples[:-20], b"crypto{")
rows = S.argmax_bytes(table, 7)
good = 0
for t, b, margin, v in rows:
    ok = b == FLAG[t]
    good += ok
    print(f"byte {t}: {chr(b)!r} want {chr(FLAG[t])!r} {'OK' if ok else 'X'} margin={margin} votes={v}")
    if not ok:
        break
p2 = 7 + good
known = FLAG[:p2]
print(f"confident prefix: {known!r} (p2={p2})")
if p2 < len(FLAG):
    synth(known, N2, "r2.jsonl")
    samples2 = S.load_samples("r2.jsonl")
    held2 = samples2[-20:]
    table2 = S.build_table(samples2[:-20], known)
    rows2 = S.argmax_bytes(table2, p2)
    for t, b, margin, v in rows2:
        ok = b == FLAG[t]
        print(f"byte {t}: {chr(b)!r} want {chr(FLAG[t])!r} {'OK' if ok else 'X'} margin={margin} votes={v}")
    # DP over table2 from p2
    closed = S.dp_search(table2, p2, 50, M=16)
    print(f"closed candidates: {len(closed)}")
    for score, bs in closed[:50]:
        cand = known + bs
        if S.verify(cand, held2):
            print(f"VERIFIED: {cand!r}")
            if cand == FLAG:
                print("EXACT MATCH")
            break
    else:
        print("no verified candidate")
