# twist_and_shout-ecsc_2023_nor
- Listener: archive.cryptohack.org 11718
- Files: /static/challenges/twist_and_shout_1477ac70b0ba9fc5bf5e5366ee6d3efa.py, Dockerfile_dfbcd10952c8d81d74f21fb783a01d23, twist_and_shout_dcc501ec132189fbdfc40fddd844f95e.xinetd
- Card source: cat_ctfarch.html (workspace root)

## Key numbers
- q = 2^128-159; E: y^2=x^3+x+1494
- #E = 340282366920938463465004184633952524077 (PRIME — unusable for PH)
- #twist = 340282366920938463461745030229583898519 = 3 · 79 · 644899 · 1283505703 · 19385376821 · 89480282251 (squarefree)

## Attack
Invalid-curve (x-coordinate oracle). For x with f=x^3+x+1494 a non-residue mod q,
the x-only ladder computes [d]P on the quadratic twist; twist has smooth order.
For each prime factor l: take generator Q=[#twist/l]P (model twist as E over
F_{q^2}), get x([d]Q) from oracle, BSGS in <Q> → e = ±d mod l (x can't see sign).
CRT over 2^6 sign choices → d; decode to bytes. Works since d (#twist ≈ 2^128)
covers flag bodies ≤16 bytes.
