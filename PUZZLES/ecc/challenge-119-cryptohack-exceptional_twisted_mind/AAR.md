# AAR — 119-cryptohack-exceptional_twisted_mind: An Exceptional Twisted Mind (CryptoHack)

**Result:** SOLVED — flag `[flag value withheld — real-flag strings live only under FLAGS/]` (+125, score 14650→14775, solved 221→222, verified via submit_flag.py JSON ok:true).
**Date:** 2026-10-23. (Prior-session OPEN analysis preserved in `AAR_open_20261020.md`.)

## Source
- CryptoHack socket 13417, provided `13417.py`. NOT consulted: solutions/writeups (no-cheat rule).

## Setup facts (verified prior session, reused here)
- modulus = p² exactly, p = 2^256 − 189 prime (p ≡ 3 mod 4). a=−3, b=152961.
- N = #E(F_p) prime; #E'(F_p) = 2p+2−N prime; cubic x³−3x+152961 irreducible mod p.
- privkey = min(k mod N, N−k mod N), k = fresh 256-bit random per connection.
- Server returns r = x([k]P̃) mod p² via an x-only Weierstrass ladder (verified == true group law on the lift P̃ ∈ E(Z/p²); twist-invariant rational function, so non-QR x0 works too).

## The vulnerability / attack (p-adic "anomalous-on-the-lift")
The response is an x-coordinate mod p², not mod p — so it can be **lifted back to a full point** Q̃ = (r, ±√f(r)) mod p² (f(r) is a QR mod p² since r ≡ x of a genuine point mod p; sqrt via a^((p+1)/4) mod p then one Hensel step). Then Q̃ = ±[k]P̃ in E(Z/p²).

Key structure: 0 → E₁ ≅ Z/p → E(Z/p²) → E(F_p) → 0 splits (non-canonically) as E(F_p) × Z/p. Multiplication by N = #E(F_p) **annihilates the Teichmüller (order-N) component** and leaves only the E₁ component, where the formal group is additive mod p² (no degree-2 term since a1=a3=0; higher terms ≥ p³ ≡ 0). With t = −x/y the formal parameter and u(R̃) := t([N]R̃)/p ∈ Z/p:

    u(Q̃) = ± k · u(P̃) mod p   ⟹   k ≡ ± u(Q̃)/u(P̃) mod p.

k < N < p, so k mod p determines k up to ± — exactly the min(k, N−k) ambiguity the server itself applies. Two get_flag guesses suffice (guesses unlimited).

**Computing u without E₁ arithmetic** (the part that blocked the previous session): [N]R̃ = R̃ + [N−1]R̃ is the degenerate chord (x₁ ≡ x₀, y₁ ≡ −y₀ mod p). [N−1]R̃ computed affinely mod p² never degenerates (intermediate sums [a]R̃+[b]R̃, a+b < N, have x_a ≢ ±x_b mod p). Writing x₀−x₁ = p·d′, ν = y₀−y₁ (a unit), first-order expansion of t = −x/y for the sum gives

    u = d′ · ν⁻¹ mod p.

Derivation check: λ = ν/(p d′), x_S = λ²−x₀−x₁, y_S = λ(x₀−x_S)−y₀; then p³x_S ≡ pν²/d′² and p³y_S ≡ −ν³/d′³ mod p² ⟹ t(S) = −x_S/y_S ≡ p·d′/ν. ✓

## Execution
- `solve.py sim`: exact clone of the server ladder, random k, full attack loop → **10/10 recovered** before touching the network.
- Live: x0 = 2 (first QR x), one get_pubkey, attack (~1 s), two get_flag guesses → second accepted.
- Pitfall hit: `get_flag` needs privkey as a JSON **integer** — a string makes the server do `str % int` → `TypeError('not all arguments converted during string formatting')` (listener catches it; session survives).

## Why the previous session stalled
It analyzed the p-adic readout in Teichmüller coordinates and correctly noted δ_T([k]P̄) is uncomputable at the unknown point — but missed that multiplying the **lifted response** by N kills δ_T automatically ([N]∘Teichmüller = O). Its empirical fits (δ(k)/k etc.) tested the wrong invariant. Same family as Smart/Anomalous (where N = p does it in one step); here N ≠ p but [N] still projects onto E₁.

## Learning points
- x-coordinate mod p² response ⇒ lift to a full point mod p² (sqrt of f(r)); the response is a point, not just a number.
- [N]R̃ ∈ ker(reduction) for any R̃ over Z/p² with R̄ of order | N; E₁ additive mod p²; ratio of u-values = k. Works whenever the server computes over Z/p² (or Z/pᵏ) with prime-order reduction, regardless of twist primeness — "no need for twist" (flag text confirms intent).
- Degenerate final chord handled by the closed form u = d′ν⁻¹; no non-invertible inverse ever taken.
- ± from the sqrt lift == min(k, N−k) server ambiguity; enumerate both candidates.

## Limitations (honest)
- First live attempt crashed on the privkey-as-string TypeError (cost one connection; fresh key per connection made it harmless).
- u(P̃) = 0 (x0 a Teichmüller lift) would kill the attack; probability 1/p, guarded by assert only.
- If N > p (negative trace) k mod p leaves a 2-way ambiguity; here t > 0 so k < p. Not generalized in code.
- Prior-session ruled-outs (small-subgroup PH, MOV, node degeneration, Infinity oracle, cross-connection PH) remain valid; artifacts probe*.py / *.gp kept.

## Artifacts
- `solve.py` (attack + ladder clone + sim + live), `flag_exceptional_twisted_mind.txt`, `AAR_open_20261020.md` (prior analysis).

## Configuration
- Windows 11 git-bash; venv `~\tools\crypto-ctf\venv\Scripts\python.exe`; submit via `python3 submit_flag.py exceptional_twisted_mind "<flag>"` from workspace root.

## Vulnerability (plain words)
The server does its EC ladder over Z/p² (the socket's modulus is exactly p², p = 2^256−189) and returns r = x([k]P̃) mod p² — a value living one level *above* F_p. That lets you lift r back to a genuine point Q̃ = (r, ±√f(r)) in E(Z/p²). The group E(Z/p²) fits into 0 → E₁ ≅ Z/p → E(Z/p²) → E(F_p) → 0 which (non-canonically) splits; multiplying by N = #E(F_p) annihilates the hard "Teichmüller" (order-N) part and leaves only E₁, where the group law is essentially additive mod p². On that additive part, discrete log is one division — a Smart/anomalous-style attack on the lift, no twist needed.

## How the answer follows
1. Verified setup facts (reused from prior-session analysis): p² exact modulus, p ≡ 3 mod 4; a=−3, b=152961; N = #E(F_p) prime; #E′(F_p) = 2p+2−N prime; cubic irreducible mod p; ladder == true group law on the lift, x-only twist-invariant readout (non-QR x0 fine).
2. Lift the response: f(r) is a QR mod p² (r reduces to a real x mod p); sqrt via a^((p+1)/4) mod p + one Hensel step ⇒ Q̃ = ±[k]P̃ in E(Z/p²).
3. With t = −x/y the formal parameter at O and u(R̃) := t([N]R̃)/p ∈ Z/p, additivity of the formal group mod p² gives u(Q̃) = ±k·u(P̃) mod p ⇒ k ≡ ±u(Q̃)/u(P̃) mod p.
4. u without E₁ arithmetic: [N]R̃ = R̃ + [N−1]R̃ is the degenerate chord (x₁ ≡ x₀, y₁ ≡ −y₀ mod p) while [N−1]R̃ computed affinely mod p² never degenerates; writing x₀−x₁ = p·d′ and ν = y₀−y₁ (a unit), first-order expansion gives the closed form u = d′·ν⁻¹ mod p (derivation check in "Setup/attack" section above).
5. k < N < p ⇒ k mod p determines k up to sign — exactly the server's own min(k, N−k) ambiguity ⇒ enumerate both, ≤2 get_flag guesses.
Execution: solve.py sim (exact ladder clone) 10/10 recoveries before network; live: x0=2, one get_pubkey, attack ~1 s, second guess accepted → flag `[flag value withheld — real-flag strings live only under FLAGS/]` (+125).

## Limitations / attempts that failed
Carried from "Why the previous session stalled" and "Limitations (honest)" above: first live attempt crashed on privkey-as-string TypeError (harmless — fresh key per connection); u(P̃)=0 (Teichmüller x0) would kill the attack, probability 1/p, assert-guarded; if N > p the k mod p readout leaves a 2-way ambiguity not handled in code (here t > 0 so k < p). Prior-session ruled-outs that failed: small-subgroup Pohlig–Hellman, MOV, node degeneration, Infinity oracle, cross-connection PH, and empirical δ(k)/k fits against the wrong invariant (δ_T at an unknown point is uncomputable; [N]∘Teichmüller = O is what actually kills it).

## Sources
Provided socket-server source `13417.py`; own prior-session analysis `AAR_open_20261020.md`; probe*.py / *.gp artifacts from the prior session. Formal-group / p-adic-lift theory used self-derived per logs (no textbook cited in the original AAR; same family as Smart/anomalous, noted as context). No solutions/writeups consulted.
