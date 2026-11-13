---
record: agent-aar
puzzle: challenge-168-cryptohack-lwe-intro
category: post-quantum
url: https://cryptohack.org/challenges/lwe-intro/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/post-quantum/challenge-168-cryptohack-lwe-intro/flag.txt"
flag_sha256: 95a640c9f92afc7765451dcb767079870059179377cdb37327306cd5def261b3
skills: []
human_twin: AAR.md
---

# AGENT — LWE Intro (challenge-168-cryptohack-lwe-intro)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
None — this is a teaching/knowledge question in the LWE intro track, not a broken system. The lesson it teaches: all of LWE's hardness lives in the error term. Strip the error away and an LWE sample (A, b) is just a system of linear equations over Z_q; the secret stops being hidden and falls out of ordinary linear algebra.

## reusable-rules
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).

## anti-patterns / limits
- Knowledge retrieval, not a derivation — no computation was performed or needed; no solve script exists for this item.
- Exact statement wording not archived (see above); beyond the recorded wrapped-vs-bare answer-format quirk (earlier attempts), nothing else failed, and no other attempts are recorded in run logs.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/post-quantum/lwe-intro/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).
