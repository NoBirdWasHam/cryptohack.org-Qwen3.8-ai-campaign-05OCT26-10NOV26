---
record: agent-aar
puzzle: challenge-121-cryptohack-node
category: ecc
url: https://cryptohack.org/challenges/node/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/ecc/challenge-10-cryptohack-node/flag.txt"
flag_sha256: 67eb5b679946fa433c3747977438cb5a11fca575c9f65948f373f821107f4f4a
skills: []
human_twin: AAR.md
---

# AGENT — 121-cryptohack-node: Elliptic Nodes (CryptoHack)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability (two layers, both real)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. **Secret parameters aren't secret.** `source.py` hides `a, b` (`from secrets import a, b`), but both `G` and `Q = dG` satisfy `y² = x³ + ax + b (mod p)`. Two points ⇒ two linear equations in `(a, b)` ⇒ solve:
   `a = (gy² − Qy² − gx³ + Qx³)·(gx − Qx)⁻¹ mod p`, `b = gy² − gx³ − a·gx mod p`.
2. **The chosen curve is singular.** With the recovered `a, b`: `4a³ + 27b² ≡ 0 (mod p)`, i.e. Δ = 0. `gcd(x³+ax+b, 3x²+a)` has common root `x₀ = −3b/(2a)` — a node. The "extra layer of security" is a nodal cubic whose nonsingular points form a group isomorphic to **F_p\*** (split node), so the ECDLP collapses to a DLP in F_p\* of order p−1.

## reusable-rules
- Two distinct points on `y² = x³ + ax + b` always determine `(a, b)` — "secret curve parameters" with a published base point + public key provide **zero** security.
- Whenever you recover curve parameters, **check the discriminant first** (`4a³ + 27b² ≠ 0`). A singular curve silently still "works" with naive group-law code (the source's `assert check_point` passes — the node lies on the curve), but the group collapses to (F_p, ×) and DLP becomes easy.
- Split vs non-split node decides the target group: `c = 3x₀` QR ⇒ F_p\* (order p−1); non-QR ⇒ norm-1 subgroup of F_{p²} (order p+1). Here p−1 was smooth-ish by construction.
- PARI `znlog`/`znorder` need `Mod(x, p)` elements, not bare integers (bare ints error into a break loop).

## anti-patterns / limits
- A prior session left this challenge OPEN with a generated stub AAR and no notes; nothing was reused from it beyond the downloaded `source.py`/`output.txt`.
- First `znlog` invocation failed (bare ints → GP break loop → `AttributeError` on the output regex); fixed by wrapping args in `Mod` — no math was wrong.
- The φ homomorphism was validated empirically (k = 2, 3, 5) rather than proved in-script; the final `d·G == Q` check under the source's own group law is the real proof of correctness.
- Did not need SEA point counting or fpylll; no failed mathematical avenues beyond the znlog arg bug.

## artifacts [OBSERVED]
- code: check_singular.py, dl.gp, factor_pm1.gp, recover_ab.py, solve.py, source.py
- data/logs: flag_node.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack — https://cryptohack.org/challenges/ecc/ ("Elliptic Nodes", 150 pts, slug `node`)
- **Statement:** "I've included an extra layer of security by picking my own curve parameters a,b and keeping them secret." Files: `source.py`, `output.txt`.
- **NOT consulted:** `/solutions/`, `/solves/`, third-party writeups (no-cheat rule). No external references used; the singular-cubic group law was derived and verified numerically in-script.
