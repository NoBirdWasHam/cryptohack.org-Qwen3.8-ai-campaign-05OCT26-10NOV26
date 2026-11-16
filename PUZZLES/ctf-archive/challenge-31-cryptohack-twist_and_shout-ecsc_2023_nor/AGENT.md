---
record: agent-aar
puzzle: challenge-31-cryptohack-twist_and_shout-ecsc_2023_nor
category: CTF Archive
url: https://cryptohack.org/challenges/twist_and_shout-ecsc_2023_nor/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-31-cryptohack-twist_and_shout-ecsc_2023_nor/flag.txt"
flag_sha256: ccdfb32edf13dc5f9f7dc34ca05201b498c97b40641d26a5e7fe9305b605576f
skills: []
human_twin: AAR.md
---

# AGENT — twist_and_shout-ecsc_2023_nor (CryptoHack archive, ECSC 2023 Norway)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
Service oracle: `shout(x, d) = x([d]P)` computed by an x-only Montgomery ladder
(EFD ladd-2002-it) with **no check that x is a valid curve x-coordinate**.
E: y²=x³+x+1494 over q=2^128-159, #E prime (= claimed "secure"), but the
**quadratic twist** order
#E' = 340282366920938463461745030229583898519
   = 3 · 79 · 644899 · 1283505703 · 19385376821 · 89480282251 (squarefree).
For any x with x³+x+1494 a quadratic non-residue, the ladder faithfully computes
x([d]P) in the twist group (verified: ladder output == full E(F_{q²}) arithmetic
for the same x). Classic invalid-curve attack.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Recovers d only up to #E' ≈ 2^128: flag bodies > 16 bytes would need extra
  info not available here (design limit of the challenge; real flag fits).
- The two 35–37-bit factors need BSGS (~2×3e5 group ops); if they were any
  larger, a Pollard-rho/p-airing upgrade would be required.

## artifacts [OBSERVED]
- code: diag_live.py, live2.py, solve.py, twist_and_shout.py
- data/logs: flag_twist_and_shout-ecsc_2023_nor.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Sources: challenge-provided materials only; self-derived per run logs.
