---
record: agent-aar
puzzle: challenge-115-cryptohack-degenerate
category: ecc
url: https://cryptohack.org/challenges/degenerate/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ecc/challenge-21-cryptohack-degenerate/flag.txt"
flag_sha256: ec2d6dd876df1a5a362348541924dec6ee3340eee7464d80c3a2639c502386b3
skills: []
human_twin: AAR.md
---

# AGENT — 115-cryptohack-degenerate: Edwards Goes Degenerate (CryptoHack)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
1. `recover_x(1, 11)` FAILS (xsqr non-residue) → returns 0 → base point is **(0, 11),
   NOT on the curve**. Public keys also decompress to x=0.
2. The Edwards addition law is closed on {(0,y)}:
   **(0,y₁)+(0,y₂) = (0, y₁y₂ mod p)** — the "curve" degenerates to the MULTIPLICATIVE
   GROUP F_p^* with generator y₀ = 11. (Same family as twisted_mind: the law evaluates
   wherever the formulas are defined.)
3. So y_a = 11^{n_a}, y_b = 11^{n_b} in F_p^*. **p−1 is smooth** (2 · ten ~2^25 primes —
   gp64 `factor` in seconds) → Pohlig–Hellman + BSGS per factor → n_a mod (p−1),
   verified 11^{n_a} == y_a.
4. shared_secret = y_b^{n_a} mod p; key = sha1(str(secret))[:16]; AES-CBC → flag.

## reusable-rules
- **Check that the base point is actually ON the curve.** A complete-looking addition law
  on off-curve points can hide a much weaker group (here: F_p^*, and p−1 was smooth).
- Edwards/Montgomery laws are rational functions — off-curve input evaluates a *different*
  group law (twist family / degenerate conic), never "fails loudly".
- A prime `order` handed to keygen means nothing if the real group is different.

## anti-patterns / limits
- Pure offline computation; no live service contact; no writeups consulted.

## artifacts [OBSERVED]
- code: card2.gp, fac.gp, facp1.gp, fo.gp, ordcheck.py, solve.py, source.py
- data/logs: flag_degenerate.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack — "Edwards Goes Degenerate" (slug `degenerate`, 100 pts)
- **NOT consulted:** solutions page / writeups (no-cheat rule)
