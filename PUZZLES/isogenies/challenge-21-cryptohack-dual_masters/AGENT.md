---
record: agent-aar
puzzle: challenge-21-cryptohack-dual_masters
category: isogenies
url: https://cryptohack.org/challenges/dual_masters/
status: solved
date: 2026-10-23
flag_ref: "FLAGS/isogenies/challenge-21-cryptohack-dual_masters/flag.txt"
flag_sha256: ff1a40ff1fd4abe32647972c263f81b826f135caae99fb63631cb53c82b89e1d
skills: []
human_twin: AAR.md
---

# AGENT — dual_masters (CryptoHack, 90 pts, isogenies)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability / attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Key observation: φ(P_a) = φ(R − n·Q_a) = −n·φ(Q_a), so

    φ(E[2²¹⁶]) = ⟨φ(P_a), φ(Q_a)⟩ = ⟨Q'⟩,  Q' := φ(Q_a).

But ker(φ̂) = φ(E[deg φ]) for the dual isogeny φ̂: E_A → E. Hence

    ker φ̂ = ⟨Q'⟩ — computable from public data alone!

1. Build φ̂ as a chain of 216 Vélu 2-isogenies from E_A with kernel ⟨Q'⟩
   (step k kills the order-2 subgroup ⟨2²¹⁵⁻ᵏ⁺¹·T⟩ of the running image T of Q').
2. Dualize the chain step-by-step: the dual of each Vélu 2-step is the Vélu
   2-map on the codomain with kernel = image of another 2-torsion point of the
   source. Composing duals in reverse gives ψ = φ̂̂ = φ (up to identifications).
3. φ(P_a) = H lies in ⟨Q'⟩; solve H = k·Q' by 2-adic bit lifting (216 doublings
   per bit), n ≡ −k (mod 2²¹⁶). The flag is exactly 27 bytes = 216 bits, so
   n mod 2²¹⁶ is the whole secret.

## reusable-rules
- In SIDH, publishing the codomain curve already leaks the dual kernel
  φ(E[l_a^e_a]); with the *full* l_a-torsion image that's the standard dual
  isogeny attack, but here even ONE image point generates φ(E[2²¹⁶]) because
  the secret kernel is the graph of multiplication by n — the second point is
  redundant. "One point instead of two" buys nothing when the kernel is a
  graph: ⟨φ(Q)⟩ alone determines ker φ̂.
- j = 0 makes the final twist identification cheap (a = 0 forced, 6 candidates).

## anti-patterns / limits
- First pure-Python attempt used a wrong Vélu y-sign and a wrong μ₃×μ₂
  parametrization of the twist (u³ = ±1 instead of u³² = b₂₁₆) — both caught
  only by numerical validation, not by reasoning.
- Early non-residue searches looped forever (searched F_p and the diagonal,
  where no non-residue exists in F_{p²}); fixed by scanning (x,1)-type elements.
- p = 1009 toy probes were meaningless (1009 ≡ 1 mod 4 ⇒ F_p[i]/(i²+1) is not
  a field); had to redo probes with p ≡ 3 mod 4.
- The 3-way μ₃ ambiguity in the dual-step scaling when a_old = 0 is resolved
  by the [2]-test; a purely algebraic choice was not attempted.

## artifacts [OBSERVED]
- code: debug_small.py, isog_lib.py, solve.py, test_small.py
- data/logs: flag_dual_masters.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Vélu 2-isogeny formulas and the dual-isogeny identity
  ker(phi_hat) = phi(E[deg phi]) — textbook-level knowledge (retrieval stated
  plainly; no paper named in run log).
- No third-party writeups or solution pages consulted (run log).
