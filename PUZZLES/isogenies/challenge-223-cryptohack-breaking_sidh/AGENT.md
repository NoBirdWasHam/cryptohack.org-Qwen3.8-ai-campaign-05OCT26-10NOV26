---
record: agent-aar
puzzle: challenge-223-cryptohack-breaking_sidh
category: isogenies
url: https://cryptohack.org/challenges/breaking_sidh/
status: solved
date: 2026-10-22
flag_ref: "FLAGS/isogenies/challenge-223-cryptohack-breaking_sidh/flag.txt"
flag_sha256: 386c4ed59c3ac7f2558894b793e2e6689e129dc94e5bf5da61d22998fd413d0c
skills: []
human_twin: AAR.md
---

# AGENT — breaking_sidh (223, 250 pts, isogenies) — SOLVED 2026-10-22
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
SIDH published, alongside Bob's curve, the images of Alice's torsion basis under Bob's secret isogeny (and vice versa) — i.e. the public key carries the *footprint of the secret walk*. The Castryck–Decru (2022) break: glue Alice's and Bob's curves into one abelian surface (dimension 2), where a deliberately longer auxiliary isogeny walk can be taken; measuring how the glued surface splits as the walk proceeds exposes Bob's secret ternary digits one at a time. Recover the digits, redo the short 3-chain walk, and the shared j-invariant is the AES key. The mathematics is heavy; for this run the *engineering* was the wall (no local Sage on the host).

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Digits 4..69 were re-run with the alt chain; only di∈{3,4,5} were individually audited
  for split-genuineness — the rest rely on the final j-match + decrypt hit (which is a
  complete check of the whole key, so this is fine).
- SageCell is a shared public service; the run took ~25 min wall across ~40 cells.

## artifacts [OBSERVED]
- code: build_attack.py, build_attack2.py, decrypt.py, final2.py, run_attack.py, sagecell_client.py
- data/logs: run_full2.log, skB_state.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Statement + provided instance files. Mathematics: Castryck–Decru key-recovery attack on SIDH (2022 paper); the run ported the jack4818/Castryck–Decru–SageMath implementation of that paper's math as recorded in the AAR (attack-algorithm reference, not a challenge writeup). No CryptoHack solutions pages, solve threads, or third-party challenge writeups consulted; verification = pairing asserts, unique-split audits, single t-match, and the `crypto{` plaintext.
