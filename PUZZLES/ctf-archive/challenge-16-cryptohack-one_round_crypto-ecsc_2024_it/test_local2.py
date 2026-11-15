#!/usr/bin/env python3
"""Local end-to-end: coset attack vs corrected local_oracle."""
import time, random, sys
from local_oracle import Session
from attack2 import build_message2, Decryptor2

MCOS, DIM, EXTRA = int(sys.argv[1]) if len(sys.argv) > 1 else 12, 7, 1536
t0 = time.time()
rng = random.Random(12345)
sess = Session()
pblocks, probes = build_message2(MCOS, DIM, EXTRA, rng)
print("blocks=%d probes=%d build=%.1fs" % (len(pblocks), len(probes), time.time()-t0), flush=True)
hexin = "".join(b.hex() for b in pblocks)
tout = sess.enc(hexin)
cblocks = [bytes.fromhex(tout[32*i:32*i+32]) for i in range(len(pblocks))]
print("encrypted %.1fs" % (time.time()-t0), flush=True)
dec = Decryptor2(pblocks, cblocks, probes)
print("decryptor: %.1fs hits=%d hitdims=%s atoms=%d ker=%s" %
      (time.time()-t0, dec.n_hits, dec.hitdims, dec.n_atoms,
       sorted(set(dec.kernel_dims))), flush=True)
ok = fail = none = 0
for k in range(100):
    m = bytes(rng.getrandbits(8) for _ in range(15)) + b"\x01"
    c = bytes.fromhex(sess.enc(m[:15].hex()))
    g = dec.decrypt(c)
    if g is None:
        none += 1
    elif g[:15] == m[:15]:
        ok += 1
    else:
        fail += 1
        if fail < 4:
            print("MISS k=%d want=%s got=%s" % (k, m.hex(), g.hex()), flush=True)
print("solved %d/%d fail=%d none=%d total %.1fs" % (ok, 100, fail, none, time.time()-t0), flush=True)
