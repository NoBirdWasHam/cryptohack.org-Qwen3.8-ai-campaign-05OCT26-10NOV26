---
record: agent-aar
puzzle: challenge-20-cryptohack-abelian_sidh
category: isogenies
url: https://cryptohack.org/challenges/abelian_sidh/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/isogenies/challenge-20-cryptohack-abelian_sidh/flag.txt"
flag_sha256: 76c1fd35fbe35e29d3b65e97d20e355d40d7eb6a5b5ff1207bcf9002b9bc9161
skills: []
human_twin: AAR.md
---

# AGENT — challenge-218: Abelian SIDH (cryptohack.org, 90 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
The scheme composes each party's isogeny with its own dual — "G_X = phi_hat(phi(G))
is safer". But the fundamental dual-isogeny identity phi_hat ∘ phi = [deg phi]
makes every such composition just scalar multiplication on the base curve. The
abelian (both-ways-dual) framing collapses the whole key exchange to one scalar
multiplication: no isogeny computation, no key recovery, no ECDLP.

## reusable-rules
**φ̂ ∘ φ = [deg φ]** always. So G_B = [3^137]G and
ss = φ̂_A(φ_A(G_B)) = [2^216]([3^137]G) = **[2^216·3^137]G** — a plain scalar
multiplication on E(F_{p²}). The "Abelian SIDH" framing (duals both ways) is what
collapses it; no key recovery, no ECDLP, no walk.

Implementation: hand-rolled F_{p²} (tuples, i²=−1) + double-and-add; parse G from
output.txt; ss = mul(G, 2^216·3^137).

## anti-patterns / limits
- First doubling draft omitted the +a4 term in the tangent slope (visible only in
  scalar mult, not in on-curve spot checks) — fixed.
- Nothing else failed (run log); the solve did zero isogeny arithmetic.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Dual-isogeny identity phi_hat ∘ phi = [deg]: standard textbook theory
  (knowledge retrieval, stated plainly).
- Sage serialization conventions inferred from decrypt success.
- No third-party writeups or solution pages consulted (run log).
