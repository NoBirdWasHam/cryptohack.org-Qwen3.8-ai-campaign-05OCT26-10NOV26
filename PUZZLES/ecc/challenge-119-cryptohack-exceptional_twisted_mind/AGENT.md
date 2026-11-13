---
record: agent-aar
puzzle: challenge-119-cryptohack-exceptional_twisted_mind
category: ecc
url: https://cryptohack.org/challenges/exceptional_twisted_mind/
status: solved
date: 2026-10-23
flag_ref: "FLAGS/challenge-119-cryptohack-exceptional_twisted_mind/challenge-119-cryptohack-exceptional_twisted_mind/flag.txt"
flag_sha256: cc10ce4b3293c4d725f8e8845e23fff085d2eb6bc79eab1909a6d8c73b7ea16e
skills: []
human_twin: AAR.md
---

# AGENT — 119-cryptohack-exceptional_twisted_mind: An Exceptional Twisted Mind (CryptoHack)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability / attack (p-adic "anomalous-on-the-lift")" [OBSERVED text; evidence tag applies to its source, not each claim]
The response is an x-coordinate mod p², not mod p — so it can be **lifted back to a full point** Q̃ = (r, ±√f(r)) mod p² (f(r) is a QR mod p² since r ≡ x of a genuine point mod p; sqrt via a^((p+1)/4) mod p then one Hensel step). Then Q̃ = ±[k]P̃ in E(Z/p²).

Key structure: 0 → E₁ ≅ Z/p → E(Z/p²) → E(F_p) → 0 splits (non-canonically) as E(F_p) × Z/p. Multiplication by N = #E(F_p) **annihilates the Teichmüller (order-N) component** and leaves only the E₁ component, where the formal group is additive mod p² (no degree-2 term since a1=a3=0; higher terms ≥ p³ ≡ 0). With t = −x/y the formal parameter and u(R̃) := t([N]R̃)/p ∈ Z/p:

    u(Q̃) = ± k · u(P̃) mod p   ⟹   k ≡ ± u(Q̃)/u(P̃) mod p.

k < N < p, so k mod p determines k up to ± — exactly the min(k, N−k) ambiguity the server itself applies. Two get_flag guesses suffice (guesses unlimited).

**Computing u without E₁ arithmetic** (the part that blocked the previous session): [N]R̃ = R̃ + [N−1]R̃ is the degenerate chord (x₁ ≡ x₀, y₁ ≡ −y₀ mod p). [N−1]R̃ computed affinely mod p² never degenerates (intermediate sums [a]R̃+[b]R̃, a+b < N, have x_a ≢ ±x_b mod p). Writing x₀−x₁ = p·d′, ν = y₀−y₁ (a unit), first-order expansion of t = −x/y for the sum gives

    u = d′ · ν⁻¹ mod p.

Derivation check: λ = ν/(p d′), x_S = λ²−x₀−x₁, y_S = λ(x₀−x_S)−y₀; then p³x_S ≡ pν²/d′² and p³y_S ≡ −ν³/d′³ mod p² ⟹ t(S) = −x_S/y_S ≡ p·d′/ν. ✓

## reusable-rules
- x-coordinate mod p² response ⇒ lift to a full point mod p² (sqrt of f(r)); the response is a point, not just a number.
- [N]R̃ ∈ ker(reduction) for any R̃ over Z/p² with R̄ of order | N; E₁ additive mod p²; ratio of u-values = k. Works whenever the server computes over Z/p² (or Z/pᵏ) with prime-order reduction, regardless of twist primeness — "no need for twist" (flag text confirms intent).
- Degenerate final chord handled by the closed form u = d′ν⁻¹; no non-invertible inverse ever taken.
- ± from the sqrt lift == min(k, N−k) server ambiguity; enumerate both candidates.

## anti-patterns / limits
- First live attempt crashed on the privkey-as-string TypeError (cost one connection; fresh key per connection made it harmless).
- u(P̃) = 0 (x0 a Teichmüller lift) would kill the attack; probability 1/p, guarded by assert only.
- If N > p (negative trace) k mod p leaves a 2-way ambiguity; here t > 0 so k < p. Not generalized in code.
- Prior-session ruled-outs (small-subgroup PH, MOV, node degeneration, Infinity oracle, cross-connection PH) remain valid; artifacts probe*.py / *.gp kept.

## artifacts [OBSERVED]
- code: 13417.py, card3.gp, facm.gp, factcub.gp, factw.gp, probe.py, probe2.py, probe_live.py, roots.gp, solve.py
- data/logs: flag_exceptional_twisted_mind.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- CryptoHack socket 13417, provided `13417.py`. NOT consulted: solutions/writeups (no-cheat rule).
