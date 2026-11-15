# Offline test: model vs CPython getstate, and full attack on simulated server.
import os, struct, sys, hashlib
sys.path.insert(0, ".")
from random import Random
from solve import seed_model, unseed, untwist, untemper, temper, my_twist, attack

# 1) model vs CPython getstate (via the real bytes->int->words path)
ok = True
for t in range(20):
    sec = os.urandom(32)
    X = int.from_bytes(sec + hashlib.sha512(sec).digest(), 'big')
    key = [(X >> (32*w)) & 0xffffffff for w in range(24)]
    r = Random(); r.seed(sec)
    real = list(r.getstate()[1][:624])
    if real != seed_model(key):
        ok = False; print("MODEL MISMATCH", t); break
print("seed_model matches CPython:", ok)

# 2) full attack pipeline on simulated server output
def sim_attack(trials=5):
    for t in range(trials):
        sec = os.urandom(32)
        r = Random(); r.seed(sec)
        outs = []
        for _ in range(79):
            outs += list(struct.unpack('<8I', r.randbytes(32)))
        rec = attack(outs)
        assert rec == sec, f"trial {t}: {rec.hex()} != {sec.hex()}"
        # predict 79th block from recovered state
        N = [untemper(w) for w in outs[:624]]
        S0 = untwist(N)
        tw = my_twist(S0); tw2 = my_twist(tw)
        pred = [temper(tw2[i]) for i in range(8)]
        assert pred == outs[624:632], f"trial {t}: next-block prediction failed"
    print(f"all {trials} simulated attacks recovered the secret + next block")

sim_attack()
