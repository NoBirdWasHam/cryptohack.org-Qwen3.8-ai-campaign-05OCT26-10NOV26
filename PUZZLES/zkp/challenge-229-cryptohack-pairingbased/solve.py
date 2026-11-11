#!/usr/bin/env python
# pairingbased (229, zkp, static): flag bit b -> zG = e(yG, bias*xG)
# bias=1 iff bit=1, else random in [0,255].  So zG==e(yG,xG) iff bit=1
# (false positive 1/256). Compute E=e(yG,xG) from public points per bit.
import time, re
from py_ecc.optimized_bn128 import FQ, FQ2, FQ12, G1, G2, pairing
t0=time.time()
bits=[]; n=0
for line in open(r"~\Practice_runs\cryptohack_org\challenge-229-cryptohack-pairingbased\output.txt"):
    line=line.strip()
    if not line: continue
    xG,yG,zG=eval(line)
    xG=[FQ(c) for c in xG]
    yG=[FQ2(c) for c in yG]
    z12=FQ12(zG)
    E=pairing(yG,xG)
    bits.append(1 if E==z12 else 0)
    n+=1
    if n%10==0: print(f"{n} bits ({time.time()-t0:.0f}s)",flush=True)
val=0
for b in bits: val=(val<<1)|b
raw=val.to_bytes((val.bit_length()+7)//8,"big")
print("n bits:",n)
print("raw:",raw)
m=re.search(rb"crypto\{[^}]*\}",raw)
print("FLAG:",m.group(0).decode() if m else "(none)")
