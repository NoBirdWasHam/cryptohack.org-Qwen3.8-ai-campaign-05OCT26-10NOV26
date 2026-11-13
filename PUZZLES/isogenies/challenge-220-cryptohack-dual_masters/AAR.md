# AAR — dual_masters (CryptoHack, 90 pts, isogenies)

**Flag:** `[flag — recorded in FLAGS/isogenies/challenge-220-cryptohack-dual_masters/flag.txt]` — submitted, `ok:true`, score_delta +90.

## The setup
SIDH-flavoured keygen on the supersingular curve E: y² = x³ + 1 over F_{p²},
p = 2²¹⁶·3¹³⁷ − 1 (so #E(F_{p²}) = (2²¹⁶·3¹³⁷)²). Secret n = bytes_to_long(flag[7:-1]).
Public: E, P_a, Q_a (generators of E[2²¹⁶]), and the "safer" public key
E_A = codomain(φ), φ_a(Q_b) = φ(Q_a) — **only one** image point, where
φ: E → E_A is the cyclic 2²¹⁶-isogeny with ker φ = ⟨P_a + n·Q_a⟩.
The predecessor challenge ("What's my Kernel") leaked both φ(P) and φ(Q);
this one leaks only φ(Q_a) and claims to be secure. It isn't.

## The vulnerability / attack
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

## Implementation gotchas (each cost real debugging time)
- **Vélu y-formula**: for kernel {(e,0)}, t = 3e²+a: x' = x + t/(x−e),
  **y' = y·(1 − t/(x−e)²)** (not −y(1+t/(x−e)²)). Codomain a' = a−5t, b' = b−7et.
  Verified numerically (homomorphism + codomain fit) before trusting.
- **Dual step lands on a twist**: the Vélu quotient of E' by ker φ̂-step is
  isomorphic to the old curve but not coefficient-equal. Each dual step needs
  an (x,y) ↦ (u²x, u³y) rescaling; u² = (b·ad)/(bd·a) from the twist relation,
  and the sign of u³ (and, when a = 0, the μ₃ choice of u²) is pinned by
  testing φ̂̂∘φ̂-step = [2] on a tracked generic point.
- **E_216 ≅ E is only a 6-way twist**: final curve is y² = x³ + b₂₁₆; the
  isomorphism to y² = x³ + 1 needs u2³ = b₂₁₆ (cube root via AMM lifting,
  since 3 | p²−1 so no exponent works) and u3² = b₂₁₆. Resolved by testing
  which of the 6 scalings maps Q_a to a point whose dual image equals the
  given Q' — exactly one matched.
- **F_{p²} root searches**: every element of F_p is both a square and a cube
  in F_{p²} (p+1 even, 3 ∤ p−1), and so is every diagonal a+ai. Tonelli-Shanks
  non-residue / AMM non-cube searches must scan elements with genuinely
  non-residue norm (e.g. (x,1) with x²+1 non-residue in F_p).
- No Sage on this host: everything implemented in pure Python + gmpy2
  (`isog_lib.py`), validated end-to-end on tiny analogous instances
  (e_a=8/10) before the 216-step real run.

## Key numbers
- p = 2²¹⁶·3¹³⁷ − 1 (432-bit prime, p ≡ 3 mod 4, p ≡ 2 mod 3)
- deg φ = 2²¹⁶; ord(Q') = 2²¹⁶; n = 40503603885770094348265111722076962450835331292559523493818154785
- runtime: ~2 min pure Python for the full chain + DLP.

## Learning points
- In SIDH, publishing the codomain curve already leaks the dual kernel
  φ(E[l_a^e_a]); with the *full* l_a-torsion image that's the standard dual
  isogeny attack, but here even ONE image point generates φ(E[2²¹⁶]) because
  the secret kernel is the graph of multiplication by n — the second point is
  redundant. "One point instead of two" buys nothing when the kernel is a
  graph: ⟨φ(Q)⟩ alone determines ker φ̂.
- j = 0 makes the final twist identification cheap (a = 0 forced, 6 candidates).

## Limitations / what failed
- First pure-Python attempt used a wrong Vélu y-sign and a wrong μ₃×μ₂
  parametrization of the twist (u³ = ±1 instead of u³² = b₂₁₆) — both caught
  only by numerical validation, not by reasoning.
- Early non-residue searches looped forever (searched F_p and the diagonal,
  where no non-residue exists in F_{p²}); fixed by scanning (x,1)-type elements.
- p = 1009 toy probes were meaningless (1009 ≡ 1 mod 4 ⇒ F_p[i]/(i²+1) is not
  a field); had to redo probes with p ≡ 3 mod 4.
- The 3-way μ₃ ambiguity in the dual-step scaling when a_old = 0 is resolved
  by the [2]-test; a purely algebraic choice was not attempted.

## Files
- `solve.py` — parser + driver; `isog_lib.py` — F_{p²}, EC, Vélu chain, dual, DLP.
- `test_small.py` — end-to-end validation on tiny instances; `debug_small.py` — dual-chain probes.
- `flag_dual_masters.txt` — the flag.

## Vulnerability (plain words)

Alice replaces SIDH's two public image points by the single point phi(Q_a) and
calls it "safer". It is not. The secret kernel ⟨P_a + n·Q_a⟩ is the graph of
multiplication by n, so every image point is a multiple of the one leaked point:
phi(P_a) = −n·phi(Q_a). Hence the whole torsion image phi(E[2^216]) = ⟨phi(Q_a)⟩
is computable from public data alone — and the dual isogeny's kernel IS the torsion
image, ker(phi_hat) = phi(E[deg phi]). Anyone can therefore build phi_hat from the
public key, dualize it back into phi, evaluate phi(P_a), and read n off a discrete
log in a 2-group. This is the auxiliary-image / dual-isogeny recovery picture: once
phi is known on the full torsion basis the secret kernel is recoverable — and with
a graph-shaped kernel, one image point already spans that basis.

## How the answer follows

- Q' = phi(Q_a) has order 2^216 on E_A; ker phi_hat = ⟨Q'⟩. Build phi_hat as a
  chain of 216 Vélu 2-isogenies from E_A: step k kills the order-2 subgroup
  generated by 2^{215−k}·T, where T is the running image of Q'.
- Dualize the chain step-by-step — the dual of a Vélu 2-step with kernel {(e,0)}
  is the Vélu 2-step on the codomain by the complementary 2-torsion kernel — with
  rescalings (x,y) ↦ (u²x, u³y) to undo twist drift (u² = b·ad/(bd·a); sign and,
  when a = 0, the μ3 choice pinned by testing phi_hat_hat ∘ phi_hat-step = [2] on
  a tracked generic point). Composing the duals in reverse gives phi.
- H = phi(P_a) lies in ⟨Q'⟩; solve H = k·Q' by 2-adic bit lifting (order-2
  candidate table, 216 doublings per bit). n ≡ −k (mod 2^216); the flag is exactly
  216 bits, so nothing is lost: n = 40503603885770094348265111722076962450835331292559523493818154785 →
  bytes → [flag — recorded in FLAGS/isogenies/challenge-220-cryptohack-dual_masters/flag.txt].
- Engine validated end-to-end on tiny analogous instances before the 216-step real
  run (~2 min, pure Python + gmpy2).

## Limitations / attempts that failed

- First attempt used a wrong Vélu y-sign and a wrong twist parametrization
  (u³ = ±1 instead of u3² = b_216) — caught only by numerical validation.
- Non-residue / non-cube searches over F_p or the diagonal loop forever: every
  element of F_p is simultaneously a square and a cube in F_{p²}; scan elements of
  genuinely non-residue norm instead.
- p = 1009 toy probes were meaningless (1009 ≡ 1 mod 4 ⇒ F_p[i]/(i²+1) is not a
  field); probes redone with p ≡ 3 mod 4.
- The μ3 scaling ambiguity when a_old = 0 was resolved numerically by the [2]-test;
  a purely algebraic choice was not attempted.

## Sources

- Vélu 2-isogeny formulas and the dual-isogeny identity
  ker(phi_hat) = phi(E[deg phi]) — textbook-level knowledge (retrieval stated
  plainly; no paper named in run log).
- No third-party writeups or solution pages consulted (run log).
