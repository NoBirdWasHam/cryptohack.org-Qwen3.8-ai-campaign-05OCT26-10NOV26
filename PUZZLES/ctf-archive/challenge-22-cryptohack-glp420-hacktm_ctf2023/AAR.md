# AAR — GLP420 (HackTM CTF 2023, CryptoHack ctf-archive, nn 262)

## Outcome
- solved: YES (live 2026-10-28; submit API 200, site solved 270→271; archive 0 pts)
- flag: `[flag — recorded in FLAGS/ctf-archive/challenge-22-cryptohack-glp420-hacktm_ctf2023/flag.txt]`
- live wall time ~31 s connect→flag; solver = **solve_v6.py + lll5.exe** (5 components:
  x^105∓1, x^70+1, Φ12Φ60Φ84(44), Φ420(96); all lattices ≤210 dims; INVERSE form
  lattices [I|mult(a^{-1} mod g)]+[0|qI] — direct form for sparse g is an LLL trap:
  raw basis is already "LLL-valid", zero swaps, Babai garbage). s from cached fold-matrix
  inverse `_finv6.json`. FLAG.txt / flag_glp420.txt here.

## What the challenge actually is
`server.sage` implements a **GLP/Dilithium-style ring signature** (NOT an Edwards-curve /
isogeny problem, despite the task-card hint): R = Z_q[x]/(x^420 − 1), q = 8383489,
b = 16383, w = 3, n = 420. keygen samples s, e with ternary coefficients, t = a·s + e.
The server gives a, t and demands a valid signature on the fixed message b"sign me!".
There is **no signing oracle** — the only path is key recovery from t.

## Vulnerability
`e = t − a·s` (and s) are ternary ⇒ the ring-LWE instance is catastrophically weak:
the Kannan/CVP lattice has determinant q^210 per 420 dims while the target point sits
at distance ‖(s_fold, e_fold)‖ ≈ 24, i.e. a unique-CVP gap of ~5·10^5. Plain LLL+Babai
recovers it. The hint that the ring splits over Z as (x^210−1)(x^210+1) cuts the lattice
in half and keeps the folded secret/err entries in [−2, 2].

## Attack (final impl: solve_v6.py + lll5.exe; v3/lll.c were earlier 2-component drafts —
## dim-420 lattices proved numerically unstable, hence the 5-component ≤210-dim split
## with INVERSE-form lattices; see Outcome. Old sketch below kept for the math.)
1. CRT-split R → R± = Z_q[x]/(x^210 ∓ 1) via the projections s ↦ u (2-term + fold) and
   s ↦ v (2-term − fold); t, a fold the same way (ring homomorphisms).
2. In each component solve CVP in L = {(r, M·r + q·z)} (dim 420, det q^210, GH ≈ 1.4e4):
   target (0, t_fold); closest lattice point differs by exactly (−s_fold, e_fold),
   entries in [−2, 2]. Gap ≫ Babai's error bound after LLL ⇒ exact.
3. Re-synchronize: s_k = (u_k + v_k)/2, s_{k+210} = (u_k − v_k)/2; check s ternary, then
   e = t − a·s and check e ternary (catches any wrong component).
4. Forge with y1 = y2 = 0: c = hash2poly(sha256(encode(0) ‖ "sign me!"));
   z1 = s·c, z2 = e·c. Then a·z1 + z2 − t·c ≡ 0, so verify's hash reproduces c exactly;
   coefficient bounds |z| ≤ ~280 ≪ b−w = 16380. (This "y=0 self-consistent hash" trick
   works because c is only constrained to be a hash *output* — the signer's rejection
   bound is the only thing forcing y ≠ 0, and 0 is trivially in-bounds.)

## Key numbers
- q = 8383489 (prime), n = 420, det L± = q^210, GH ≈ 1.43e4, solution norm ≈ 24,
  unique-CVP gap ≈ 600 (folded) / ≈ 700 (unsplit 840-dim form).
- C fp64/textbook LLL: **77.7 s** for the 420-dim component lattice (this host).

## Toolchain gotchas (this host, cost the most time)
- fpylll 0.6.4 wheel (crypto-ctf venv): `LLL.reduction(method='fast'/'heuristic',
  float_type='ld'/'mpfr')` dies with `ReductionError: "infinite loop in babai"` on this
  qary matrix; only proved-int mode works, and it took **224 s at dim 210** (≈ 3600 s+
  at 420 — busts the server's `signal.alarm(600)`). `method='wrapper'` ran > 8 min.
  ⇒ wrote own textbook LLL in long-double C (`lll.c`, 80 lines, matches fplll minimum
  norm on n=10/60 random lattices) and kept fpylll only for `CVP.babai` (works fine).
- My first C LLL hung because `mu[j][j]` was left 0 instead of 1 (size-reduction made
  no progress). Fixed; n=10 min-norm identical to fplll's.
- **Math pitfall**: folding by non-±1 roots (e.g. ζ = i or 12th roots of unity, which DO
  exist in F_q since 12 | q−1) does NOT keep folded secrets small — ζ^j mod q is a huge
  field element. Only ±1-coefficient folds (x^m ∓ 1 factor chains) preserve smallness.
  This killed two "clever" smaller-lattice variants (4-comp ζ-folds, 12-comp) — both
  failed the smallness check exactly as the theory says they must.
- The "obvious" 420-dim CVP with lattice {M·s + q·v} is **trivial/degenerate**: M is
  invertible mod q ⇒ that set is all of Z^420. The homogenized (s, e)-pair form above
  is the correct one.

## Flag provenance
Flag received directly from the listener `archive.cryptohack.org:26931` after a locally
pre-verified forgery passed server-side `verify`. Not taken from any repo/description/
writeup; none consulted.

## Limitations / failures (evidence)
- BKZ-40 / LLL (fpylll proved) on the 840×420 degenerate lattice ({M·s + q·v} = Z^420
  since M is invertible mod q ⇒ CVP meaningless): >400 s with no result, killed; the
  degeneracy was realized from theory afterwards.
- ζ=±i 4-component and 12th-root 12-component splits: Babai output max|fold| > bound
  (huge values), root cause above.
- Live: attempt 1 timeout (extra rdline ate `a_enc` — no banner on socket); attempt 2
  lll5 rare "stuck" guard → retry; attempt 3 SUCCESS in ~31 s:
  `flag = '[flag — recorded in FLAGS/ctf-archive/challenge-22-cryptohack-glp420-hacktm_ctf2023/flag.txt]'`. Submitted
  (submit_flag.py: ok 200, solved 270→271); progress.json → solved; reconcile.py clean.

## Source (section added by 2026-11-09 corpus audit — AAR body text unchanged)
- Platform: CryptoHack, ctf-archive card 'GLP420 (HackTM CTF)' (challenge file per site.md).
- Statement provenance: statement.txt in folder (begins: "GLP420 (HackTM CTF 2023) — CryptoHack ctf-archive  I have developed a variant of...")
- Provided material as stored in folder: FLAG.txt, det_done.txt, f1_result.txt, flag_glp420.txt, gtrue.txt, probe.py, probe2.py, probe3.py
- Not consulted: /solutions/ pages, third-party writeups (campaign no-cheat rule).
