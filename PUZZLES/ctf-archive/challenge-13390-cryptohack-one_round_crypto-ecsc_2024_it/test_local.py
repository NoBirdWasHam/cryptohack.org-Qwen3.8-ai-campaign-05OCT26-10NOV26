#!/usr/bin/env python3
"""Local end-to-end test: simulate server game against Decryptor."""
import time, random
from local_oracle import Session
from attack_core import build_message, Decryptor

rng = random.Random(42)
T, EXTRA = 96, 256

for trial in range(2):
    sess = Session()   # random key
    t0 = time.time()
    pblocks = build_message(T=T, extra=EXTRA, rng=rng)
    hexin = "".join(b.hex() for b in pblocks)
    outhex = sess.enc(hexin)          # server-side cost
    t_srv = time.time() - t0
    cblocks = [bytes.fromhex(outhex[32*i:32*i+32]) for i in range(len(pblocks))]
    t1 = time.time()
    dec = Decryptor(pblocks, cblocks, T)
    t_build = time.time() - t1
    print("trial", trial, "blocks", len(pblocks), "srv_enc=%.1fs build=%.1fs" % (t_srv, t_build),
          "dims", dec.dims[:4], "... atoms", dec.n_atoms, "kerdims", dec.kernel_dims[:3])
    ok = 0; fail = []
    t2 = time.time()
    for k in range(100):
        m = bytes(rng.getrandbits(8) for _ in range(15))
        blk = m + b'\x01'
        c = sess.enc_block(blk)
        p = dec.decrypt(c)
        if p == blk: ok += 1
        elif len(fail) < 3: fail.append((m.hex(), p.hex() if p else None))
    print("trial", trial, "solved %d/100 in %.2fs" % (ok, time.time()-t2), "fails", fail)
