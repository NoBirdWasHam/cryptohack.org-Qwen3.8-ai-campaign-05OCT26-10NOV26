# AAR — Challenge 130: The Matrix Revolutions

**Result:** **SOLVED + API-VERIFIED 2026-10-20** — flag `[flag — recorded in FLAGS/diffie-hellman/challenge-130-cryptohack-matrix_revolutions/flag.txt]`
submitted via `submit_flag.py matrix_revolutions`; score 9610→9735 (+125), solved 185→186.
**Date:** 2026-10-20 (UTC)

## Sources
- Statement page: https://cryptohack.org/challenges/diffie-hellman/ (card "The Matrix Revolutions", 125 pts).
- Provided file: https://cryptohack.org/static/challenges/matrix_revolutions_2d9c03dde281a05e89519d9cd356d19c.zip
  → unzipped/ (matrix_revolutions.sage, generator.txt, alice.pub, bob.pub, flag.enc).
- NOT consulted: /challenges/matrix_revolutions/solutions/, any writeup, any third-party flag.

## The flag
Recorded in `FLAGS/diffie-hellman/challenge-130-cryptohack-matrix_revolutions/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## How it was solved (reproducible)
1. **Structure** (`getpols.py` + gp64): charpoly(G) = f1·f2, irreducible deg 61 & 89, exps 1.
   ⇒ algebra F2[x]/charpoly ≅ GF(2^61)×GF(2^89); ord(G) = (2^61−1)(2^89−1), both Mersenne primes.
2. **Targets** (`step1.py`): Krylov solve A_pub = h_A(G) over the basis {G^k}; rA1 = h_A mod f1,
   rA2 = h_A mod f2 (same for B) → `targets.json`. (Krylov correctness is implied by step 5's gates.)
3. **DLOG by index calculus** (`ic6.c`, C, u128 bitmasks):
   - Factor base = monic irreducibles deg ≤ D (buildfb, ascending).
   - Relation search: walk a = x^i (mulx-reduced), accept iff squarefree + all irreducible
     factors deg ≤ D (exact `ddf` + exact division; NO norm heuristic in ic6).
   - 89-bit block: D=14 (nfb=2537), P(smooth)≈2.9e-6; 7 parallel searchers, offsets 1e9…7e9,
     5200 general relations. 3 factor-base elements never appeared → **targeted search** (mode T:
     walk x^i·p, relation gets coefficient −1 for p; ~2e6 iterations each).
   - Linear algebra over Z/(2^m−1) (Φ prime for m=61,89): Gauss-Jordan with modinv.
     Final rank 2536/2537 (89-bit) and 745/746 (61-bit): solved anyway — target log is
     determined iff target vector ⊥ kernel: slope = [free col in factors] − Σ_piv e_j·A_RREF[j][free];
     print only when slope==0.
   - **Self-verification built into Z mode:** x^lg == h (poly modexp) must hold before printing
     (`VERIFY … OK` on stderr). This gate is what caught the muln bug below.
4. **61-bit block:** D=8 was 5000× too slow (P≈1.9e-8 empirically); D=12 (nfb=746, P≈9e-5) →
   1800 relations in ~50 s.
5. **Assembly** (`step3.py`): CRT(l61 mod 2^61−1, l89 mod 2^89−1) → A, B; gates; key =
   SHA256(''.join(bits of shared rows))[:32]; AES-CBC decrypt → flag.

## Bugs found en route (the real cost of this challenge)
- **`muln` (mod-Φ multiply) was hard-coded for Φ=2^89−1** (45/44-bit Karatsuba split assuming
  2^90 ≡ 2). For MD=61 the wrap constants are wrong → every mod-Φ operation silently wrong →
  the earlier ic5 61-bit logs AND the first ic6 61-bit logs were garbage, while 31- and 89-bit
  runs were correct (the split happens to be valid for MD=31 and MD=89). Fix: direct
  `foldn(a*b)` for MD≤63 (product fits u128), split path only for MD=89; `foldn` made a loop
  (multi-fold) so large intermediates can't escape one subtraction.
  **Lesson: pin EVERY field size with a regression; a size-specialized modular multiply fails
  silently, and full-rank-looking linear algebra hides it.**
- **Regression targets must be generated in the SAME field** as the solver: one "solver bug"
  scare came from generating x^r with PARI over a degree-32 f while the solver used the
  degree-31 f. (PARI `ffgen(f,'a)` + `lift` + Vec hex dump; note `hex` is a PARI builtin name.)
- **Rank deficiency ≠ blocked:** with 1 free column, the target log is still determined when the
  target factorization is orthogonal to the kernel (slope test). Verified by x^lg==h anyway.
- **Isolated factor-base elements** (never dividing any x^i in the sampled range): fix with the
  targeted x^i·p walk (mode T) instead of brute-force scaling the whole search.

## Learning points
- Matrix DH over GF(2) with split charpoly = direct product of extension fields; DLOG reduces
  to per-factor index calculus; CRT the exponents; ord(G) = lcm of the field group orders.
- Function-field smoothness at q=2 deviates strongly from ρ(u) at small D (61/8 measured 1.9e-8
  vs ρ≈1e-6): MEASURE P(smooth) on ~5e5 iterations before committing to a search budget.
- 2^61−1 and 2^89−1 are both prime (Mersenne exponents) → Z/Φ is a field, Gauss-Jordan with
  Fermat modinv is valid; composite Φ would have needed per-prime-factor CRT Gauss.
- Parallel relation search: disjoint i0 windows, merge files, ONE Gauss pass; ~1.5e5 tests/s/core.

## What I did / did not do
- Worked only from the provided zip + my own code. No solutions page, no writeups, no shared flags.
- Did NOT modify the Krylov step (its output is validated end-to-end by G^A==A_pub).
- Submissions: exactly one flag submission for this challenge (score_delta +125).

## Limitations
- Flag derived AND submitted (leaderboard-verified) — no limitation on verification.
- The 89-bit relation matrix reached rank 2536/2537, not full; correctness rests on the slope
  test + x^lg==h self-check + the G^A==A_pub gate (all passed).

## Configuration
- Host: Windows 11, git-bash/MSYS; user OWNER; date 2026-10-20 UTC.
- gcc (winlibs mingw64) -O2 for ic6.exe; venv python 3.12
  (`~\tools\crypto-ctf\venv\Scripts\python.exe`, PyCryptodome);
  PARI/GP gp64 2.17.4 (`~\tools\gp64.exe`).
- Working dir: `~\Practice_runs\cryptohack_org\challenge-130-cryptohack-matrix_revolutions\unzipped`.
- Agent: Hermes Agent (desktop), model qwen3.8-flash-next-unsloth-ud-q4_k_xl via qwen3-8-flash.
- Network: cryptohack.org (API + /submit/matrix_revolutions/), socket services NOT used
  (static challenge).
