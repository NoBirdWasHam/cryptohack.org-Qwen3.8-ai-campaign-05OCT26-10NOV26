# AAR — 128-cryptohack-matrix_reloaded: Matrix Reloaded (CryptoHack)

**Result:** SOLVED — submitted, API-verified (`score_delta +100`, 9475→9575, 184 solved).
**Date:** 2026-10-20 (UTC). Offline (`matrix_reloaded.sage`, `generator.txt`, `output.txt`, `flag.enc`).

## Sources
- CryptoHack DH category, slug `matrix_reloaded` (100 pts). NOT consulted: solutions/writeups.

## The flag
Recorded in `FLAGS/diffie-hellman/challenge-128-cryptohack-matrix_reloaded/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## Problem
- G ∈ GL₃₀(F_P), P 512-bit; H = G^SECRET; random v, w = H·v. KEY = sha256(str(SECRET))[:32]
  (digest()[:128] on 32-byte digest = full 32 bytes → AES-256-CBC).

## How it was solved
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

## Learning points
- **Matrix-DH with non-semisimple G: the Jordan block is an oracle for the exponent.**
  Whenever w = G^s·v, check `nullity(G−λI)` vs multiplicity for every repeated charpoly root.
  A single 2×2 block turns DLP into one division.
- Even when DLP is easy mod ord(G), recovering SECRET itself needs ord(G) > range — Jordan
  blocks bypass that entirely (s appears as a coefficient, not an exponent).
- `digest()[:128]` on a 32-byte sha256 = the whole digest (AES-256, not 128).

## What I did / did not do
- Pure offline; no writeups.

## Limitations
- None; flag verified by submission.

## Configuration
- Windows 11 git-bash; venv python; gp64; dir `...\challenge-128-cryptohack-matrix_reloaded\unzipped`;
  Hermes Agent (qwen3.8-flash-next-unsloth-ud-q4_k_xl @ qwen3-8-flash).
- Artifacts: solve.py (working), eig.gp/eig.txt, rank.gp, mat.gp/mat2.gp.
