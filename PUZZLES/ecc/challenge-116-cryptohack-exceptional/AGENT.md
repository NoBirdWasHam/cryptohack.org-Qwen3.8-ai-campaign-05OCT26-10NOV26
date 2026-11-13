---
record: agent-aar
puzzle: challenge-116-cryptohack-exceptional
category: ecc
url: https://cryptohack.org/challenges/exceptional/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/ecc/challenge-116-cryptohack-exceptional/flag.txt"
flag_sha256: c2b7e91892a3788683436ffc6904e2bdd838bad38895c087773a8889c70ef100
skills: []
human_twin: AAR.md
---

# AGENT — 116-cryptohack-exceptional: Exceptional Curves (CryptoHack)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
1. `is_prime(order)` passes for ANY prime order — including the **anomalous** case.
   gp64 `ellcard` (SEA, ~1 min at 512 bits, 2 GB stack): **#E == p** → Smart's attack.
2. Smart/formal-group lift: E~ over Z/p², lift P~=(x, y+tp) with
   t = ((x³+ax+b − y²)/p)·(2y)⁻¹ mod p; λ(P) = t([p]P~)/p mod p where t = −x/y;
   n = λ(A)·λ(G)⁻¹ mod p. Pure-python Jacobian coords over Z/p² (no inversions).
3. Validated the whole λ pipeline **20/20 on a small anomalous curve first**
   (p=1039, a=2, b=5 — found by gp scan; classic p=751 example is NOT anomalous).
4. nA recovered, verified nA·G == A, S = nA·B, AES-CBC → flag.

## reusable-rules
- **`assert is_prime(order)` ≠ safe.** Prime order kills Pohlig–Hellman but not:
  anomalous (#E=p → Smart), supersingular (MOV), or trace-2 (#E=(p+1)²-ish) cases.
  ALWAYS compute #E and compare to p, p+1, and factor it — "prime" is one check of many.
- Smart's attack is O(1) group laws over Z/p² — trivially cheap even at 512 bits.
- Validate exotic attacks on a tiny instance found by brute-force scan before pointing
  them at 512-bit targets (the p=751 "textbook" anomalous example is wrong — scan your own).

## anti-patterns / limits
- Pure offline; no writeups consulted.

## artifacts [OBSERVED]
- code: anom.gp, card.gp, smart_test.py, solve.py
- data/logs: flag_exceptional.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack — "Exceptional Curves" (slug `exceptional`, 100 pts)
- **NOT consulted:** solutions page / writeups (no-cheat rule)
