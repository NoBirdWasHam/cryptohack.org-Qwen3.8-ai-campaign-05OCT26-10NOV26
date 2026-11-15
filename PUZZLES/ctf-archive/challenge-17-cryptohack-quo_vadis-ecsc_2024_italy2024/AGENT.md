---
record: agent-aar
puzzle: challenge-283-cryptohack-quo_vadis-ecsc_2024_italy2024
category: ctf-archive
url: https://cryptohack.org/challenges/quo_vadis-ecsc_2024_italy2024/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-17-cryptohack-quo_vadis-ecsc_2024_italy2024/flag.txt"
flag_sha256: c3b52d904b1afe91979d8c6da8fc6ef4db5c48ffafa32b848112ddc1f46eb1a4
skills: []
human_twin: AAR.md
---

# AGENT — quo_vadis (ECSC 2024 Italy, CryptoHack archive, slug quo_vadis-ecsc_2024_italy2024)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
Per challenge, the server builds two rings over Z/2^k:
- R1 = tower Z/2^k[b0]/(m0) ... successive quotients by lifted irreducibles (degrees ds),
- R2 = Z/2^k[b]/(g) in ONE step, deg g = prod(ds) = D,
Both are the Galois ring GR(2^k, D), hence CANONICALLY ISOMORPHIC over Z/2^k.
The oracle: server prints f(pt1) for a SECRET random {0,±1}-coeff poly f (1024 coeffs)
and returns f(pt2) for our chosen pt2 — but only after we "prove" we can compute in the
rings. Since f has integer coefficients, f commutes with the isomorphism psi: R1 -> R2:
send pt2 = psi(pt1); the reply is f(psi(pt1)) = psi(f(pt1)); pull back to get f(pt1).
Five challenges give all bytes of K = sha256 key -> AES-CBC flag decrypt.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Tower.ensure_tab original design = 2^D x 2^D table: OOM-huge for D=30/60; replaced by
  structure constants + byte XOR tables (this was the prior session's stall; the earlier
  "Q(sqrt(D)) order/ideal/lattice" direction was NOT needed and was abandoned).
- parse_poly_str originally mis-assigned flat constant-coefficient terms (duplicate-deg
  AssertionError); fixed with zero-term grouping rule.
- No Sage on this host; protocol replica is my own Python server (same math, sage-style
  output strings), so parse-format coverage of the REAL sage prints is verified only
  against the sample lines captured from the live build (e.g. "b1^3 + (b0bar + 1)*b1 + 1").

## artifacts [OBSERVED]
- code: _gp_test.gp, harness.py, quo_core.py, sim_server.py, solve.py
- data/logs: flag_quo_vadis-ecsc_2024_italy2024.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
