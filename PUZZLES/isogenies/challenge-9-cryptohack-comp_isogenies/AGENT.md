---
record: agent-aar
puzzle: challenge-211-cryptohack-comp_isogenies
category: isogenies
url: https://cryptohack.org/challenges/comp_isogenies/
status: solved
date: 2026-10-15
flag_ref: "FLAGS/isogenies/challenge-9-cryptohack-comp_isogenies/flag.txt"
flag_sha256: 64759845ad9cf223c97af5def6e901fa697d8ab4e5496326c1403d4e0d3518d7
skills: []
human_twin: AAR.md
---

# AGENT — comp_isogenies (CryptoHack Isogenies, 60 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
13-step Vélu isogeny chain over F_{p²} = F_p[i] (p = 417942208511 = 2^18·3^13 − 1), pure Python, no PARI/Sage/fpylll:
1. Verify K ∈ E(F_{p²}), 3^13·K = O (K order 3^13).
2. Q_0 = [3^12]K (order 3); φ_0 = Vélu 3-isogeny with kernel {O, Q_0, −Q_0}.
3. Iterate: K_{k+1} = φ_k(K_k), Q_{k+1} = [3^{11−k}]K_{k+1} (order 3), φ_{k+1} = Vélu 3-isogeny. 13 steps total.
4. j(E_13) from final (a, b) coefficients = 292990704480 + 249510360818·i.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- EC doubling used the addition formula (off-curve 2P; caught by on-curve
  assertion).
- The x^((q+1)/4) square root is invalid for q = p² (q ≡ 1 mod 4) → infinite
  loop; replaced by Tonelli–Shanks in F_{p²}.
- Tonelli–Shanks non-residue search over F_p can never terminate (every element
  of F_p is a square in F_{p²}); must search elements of genuinely non-residue
  norm.
- 6 of 7 flag submissions failed on serialization only — the value never changed.

## artifacts [OBSERVED]
- code: comp_iso.py, verify_comp.py
- data/logs: verify.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Standard Vélu / cyclic-kernel factorization math; PARI not usable for the
  F_{p²} checks, hence the three-way internal verification.
- No third-party writeups or solution pages consulted (run log).
