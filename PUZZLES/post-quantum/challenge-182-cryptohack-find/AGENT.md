---
record: agent-aar
puzzle: challenge-182-cryptohack-find
category: post-quantum
url: https://cryptohack.org/challenges/find/
status: solved
date: 2026-10-14
flag_ref: "FLAGS/post-quantum/challenge-182-cryptohack-find/flag.txt"
flag_sha256: 32e7a37fe97212d77e156407812bfb8b4d048d0cd2be596503d9e279d4394f6a
skills: []
human_twin: AAR.md
---

# AGENT — Find the Lattice (challenge-182-cryptohack-find)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (the "hidden 2D lattice")" [OBSERVED text; evidence tag applies to its source, not each claim]
The key relation h·f = g + s'·q means the vector **(g, f) lies in the 2D lattice**

    L = ⟨ (h, 1), (q, 0) ⟂  ⊂ Z²,   since (g, f) = f·(h, 1) − s'·(q, 0).

det(L) = q ≈ 2^511.6, so a *random* 2D lattice of this determinant has shortest
vector ≈ 2^255.8 — and (g, f) sits right at that scale (‖(g,f)‖ ≈ 2^255). 2D
Gaussian reduction is provably optimal, so it finds (g, f) exactly.

Solve script: `solve.py` (pure Python, 2D Gauss, no fpylll needed).

Result:

    g = 43997957885147078115851147456370880089696256470389782348293341937915504254589
    f = 47251817614431369468151088301948722761694622606220578981561236563325808178756

Verified against all structural constraints (each checked in code):
- (h·f) mod q == g ✓
- 2 ≤ f < isqrt(q//2) ✓
- isqrt(q//4) ≤ g < isqrt(q//2) ✓
- gcd(f, g) == 1 ✓

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: find_source.py, solve.py
- data/logs: find_output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- q = 512-bit prime; f ∈ [2, √(q/2)), g ∈ [√(q/4), √(q/2)), gcd(f,g)=1
- public key h ≡ g·f⁻¹ (mod q)  ⇒  **h·f = g + s'·q** (s' = ⌊h·f/q⌋ < 2^255)
- ciphertext e ≡ r·h + m (mod q), r < √(q/2), m = flag (27 bytes = 216 bits)
- decrypt: a = (f·e) mod q;  m = a·f⁻¹ (mod g)

Only (q, h, e) are known. All secrets (f, g, r) are ≈ 2^254.8.
