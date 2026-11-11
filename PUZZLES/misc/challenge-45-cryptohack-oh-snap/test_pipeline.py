#!/usr/bin/env python3
"""Local pipeline test: iterative rounds with confidence gating + final DP."""
import sys, json, random, time
from Crypto.Cipher import ARC4
import solve_oh_snap as S

FLAG = sys.argv[1].encode() if len(sys.argv) > 1 else b"crypto{sn4p_snap_rc4_bites_h4rd}"
PER = int(sys.argv[2]) if len(sys.argv) > 2 else 120000
RLEN, M = 4, 96
rng = random.Random(2026)

def synth(prefix, count):
    out = []
    for _ in range(count):
        R = bytes(rng.randrange(256) for _ in range(RLEN))
        N = R + prefix
        ks = ARC4.new(N + FLAG).decrypt(b"\x00" * M)
        out.append((N.hex(), ks.hex()))
    return out

known = b"crypto{"
t0 = time.time()
for rnd in range(1, 6):
    samples = synth(known, PER)
    held = samples[-20:]
    table = S.build_table(samples[:-20], known)
    ext, rows = S.confident_extend(known, table)
    print(f"round {rnd}: {known!r} -> {ext!r} ({time.time()-t0:.0f}s)")
    for t, b, margin, v1, v2 in rows:
        mark = "OK" if b == FLAG[t] else "X!"
        print(f"   byte {t} {chr(b)!r} [{mark}] margin={margin} v1={v1} v2={v2}")
    known = ext
    if known.endswith(b"}"):
        ok = S.verify(known, held)
        print(f"FLAG: {known!r} verified={ok} exact={known==FLAG}")
        break
    cand, score, nc = S.final_dp(known, table, held)
    if cand:
        print(f"DP early finish: {cand!r} exact={cand==FLAG}")
        break
else:
    print("round budget exhausted")
