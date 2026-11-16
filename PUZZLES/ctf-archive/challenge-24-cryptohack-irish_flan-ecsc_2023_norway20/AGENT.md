---
record: agent-aar
puzzle: challenge-24-cryptohack-irish_flan-ecsc_2023_norway20
category: ctf-archive
url: https://cryptohack.org/challenges/irish_flan-ecsc_2023_norway20/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-24-cryptohack-irish_flan-ecsc_2023_norway20/flag.txt"
flag_sha256: 6d85158006bbb06edf06f2a7b25e9d9470010a5ca1239156c90980a178b34466
skills: []
human_twin: AAR.md
---

# AGENT — irish_flan-ecsc_2023_norway20 (CryptoHack archive, ECSC 2023 Norway)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability / attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Let φ = inn(χ); on the pure-imaginary part it is a rotation R about axis
A = χ_pure. Nothing factored needed, two structural facts do it:
1. **Axis leak**: γ = χ^ρ ⇒ γ_pure ∥ χ_pure, so the rotation axis A is public
   (γ_pure itself).
2. **Rotations about a fixed axis are commutative / complex-like**: with
   J(x) = A×x (J² = −L²·id on the plane ⊥A), every rotation about A is
   c + s·J with c² + s²L² = 1, and composition is complex multiplication mod n.
Known points on the orbit: v = α_pure, Rv = −N(α)·β_pure (from β = φ(α⁻¹)),
R^m v = ε_pure. Extract (c,s) of λ = R from (v→Rv) and λ^m from (v→ε_pure) by
projection onto the basis {v⊥, J(v⊥)} (only needs L², |v⊥|² invertible — they
were). Then λ^{m+1} = λ·λ^m by complex mult — **no discrete log, no factoring**
— and t = R^{m+1}v. Finally κ = φ^{m+1}(α⁻¹) = (α_a/N(α), −t/N(α)) since
conjugation fixes the real part. Then k, K, AES-decrypt.

Key numbers: n is a 2048-bit product of two 1024-bit primes; r,s < n⁸.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- N(α) must be the full quaternion norm (a²+b²+c²+d²), not pure-part norm —
  caught immediately by the built-in sanity assert (c²+s²L² ≡ 1 mod n).
- output.txt line 2 embeds raw AES bytes between μ and ε; parse quaternions by
  the regex `\((-?\d+) \(mod \d+\)(,…){3}\)` pattern, bytes via literal_eval of
  the segment before the first quaternion.
- The generator's `Q.__pow__` has a bug (`c = c*self` instead of `c*c`), so
  actual exponents are r+popcount(r) etc. Irrelevant to the attack (m stays a
  product-like unknown; the axis/complex trick never needs any exponent).

## artifacts [OBSERVED]
- code: irish_flan.py, solve.py
- data/logs: flag_irish_flan-ecsc_2023_norway20.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
