# ECDSA nonces with HIDDEN recurrence modulus — literature-gap map

Use when facing "ECDSA/LCG or biased-nonce" walls where the recurrence/lattice modulus p is NOT the curve order n (or otherwise secret). Decide EARLY whether published math applies; all checks are paper-premise checks, not compute questions.

## Premise gates (fail any one = published families cannot apply)
1. **Observability (FHKLS'87/88, Stern'88, Contini–Shparlinski ACISP'05):** truncated-LCG recovery needs observable LCG outputs. Nonces masked by secret key (s·d combos) fail the input premise — no sample count saves this.
2. **Known-modulus bias (BV'96 → HGS'01 → Nguyen–Shparlinski → Albrecht–Heninger'21 → Sun TCHES'22 → Gao ePrint 2024/296):** all HNP variants define bias mod a KNOWN modulus. If nonces are uniform mod secret p, their image mod known order n is uniform noise — bias vanishes. No published HNP supports a hidden sample modulus.
3. **Open-problem flag:** Macchetti ePrint 2023/305 handles LCG nonces with unknown coefficients **mod the curve order** and explicitly names "recurrence modulus ≠ curve order" as OPEN future work. If a challenge is exactly that setting, it sits on a literature gap.
4. **ACD perturbation budgets (Howgrave-Graham LNCS 2146; Cohn–Heninger ePrint 2011/437, bound (∏X_i)^{1/m} < N^{β(m+1)/m} with exact multiple):** requires an exact multiple and perturbation budget far below N^β. Cofactor-SIZED dust (e.g. 2^308 vs p≈2^311, i.e. p^{0.99}) is the DGH/DGHV hardness-assumption regime — beyond budget by ≥2^150 at typical scales, and no exact multiple exists when the only known multiple is p itself.
5. **Curve-equation modulus pinning:** p (secret recurrence modulus) appears in NO curve equation when the curve is fixed (secp256k1); no algebraic handle to pin it.

## Consequences for planning
- Sample counts are almost never the blocker for these walls (families need 2–6 outputs; having 17+ changes nothing if premises fail).
- CVP arsenal sizing: surveyed constructions all fit dim ≤ ~120 — if premises ever pass, fpylll/HeapPruned is enough; such a wall is hypothesis-shaped, not tool-shaped.
- Correct writeup shape: vacuity theorem (if applicable) + premise-failure per family + "this is the published-defense regime" (Minerva ePrint 2020/728 §3.4.2 RECOMMENDS unreduced oversized nonces as HNP defense — the challenge IS the defense).
