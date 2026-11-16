---
record: agent-aar
puzzle: challenge-13-cryptohack-matrix_reloaded
category: diffie-hellman
url: https://cryptohack.org/challenges/matrix_reloaded/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/diffie-hellman/challenge-13-cryptohack-matrix_reloaded/flag.txt"
flag_sha256: 4ab60d7b5702d43a92e91f6b17caa359a046878da41b7e9a5400f44d81466ddf
skills: []
human_twin: AAR.md
---

# AGENT — 128-cryptohack-matrix_reloaded: Matrix Reloaded (CryptoHack)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
1. gp: charpoly of G splits into LINEAR factors over F_P — 29 distinct eigenvalues, ONE with
   multiplicity 2. P−1 = 2·5·71·(503-bit composite) ⇒ generic DLP in F_P* is hopeless, so the
   eigenvalue route (PH over ord(λ)) is a dead end — and even full PH would only give s mod
   ord(G), not SECRET.
2. The real hook: nullity(G − λ₀I) = 1 at the double root ⇒ **2×2 Jordan block ⇒ G not
   diagonalizable ⇒ s leaks LINEARLY, no DLP at all**:
   Jordan basis (eigenvectors of the 28 simple λᵢ + chain u₁,u₂ with (G−λ₀)u₂=u₁), dual
   functionals φ₁,φ₂ = rows of T⁻¹:
     β₂ = φ₂(w) = λ₀^s·a₂  ⇒  ls = β₂/a₂
     β₁ = φ₁(w) = λ₀^s·a₁ + s·λ₀^{s−1}·a₂  ⇒  **s = (β₁ − ls·a₁)·λ₀/(ls·a₂) mod P**
   SECRET < P ⇒ unique. Verified G^s·v == w exactly, then sha256 → AES → flag.
3. Linear algebra hand-rolled (rref/solve/inverse mod P, 30×30 — instant); eigenvalues via
   gp `factor(charpoly)` + `lift()` (Mod objects print wrapped — lift to ints).

## reusable-rules
- **Matrix-DH with non-semisimple G: the Jordan block is an oracle for the exponent.**
  Whenever w = G^s·v, check `nullity(G−λI)` vs multiplicity for every repeated charpoly root.
  A single 2×2 block turns DLP into one division.
- Even when DLP is easy mod ord(G), recovering SECRET itself needs ord(G) > range — Jordan
  blocks bypass that entirely (s appears as a coefficient, not an exponent).
- `digest()[:128]` on a 32-byte sha256 = the whole digest (AES-256, not 128).

## anti-patterns / limits
- Pure offline; no writeups.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: flag_matrix_reloaded.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- CryptoHack DH category, slug `matrix_reloaded` (100 pts). NOT consulted: solutions/writeups.
