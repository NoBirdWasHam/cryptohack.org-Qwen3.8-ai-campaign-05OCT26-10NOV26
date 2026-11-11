import sys, os, json
base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base)
from harness import load_challenge
from Crypto.Util.number import long_to_bytes

for t in range(4):
    ch = load_challenge(os.path.join(base, "13409.py"))
    k = ch.C.share_key
    Lp, Lq, Ld, Lu = [len(long_to_bytes(x)) for x in (k.p, k.q, k.d, k.u)]
    data = 130 + 130 + (2 + Ld) + (2 + Lu)
    print(f"trial {t}: Lp={Lp} Lq={Lq} Ld={Ld} Lu={Lu} data={data} pad_start={data} u_last={data-1} dbits={k.d.bit_length()} ubits={k.u.bit_length()}")
