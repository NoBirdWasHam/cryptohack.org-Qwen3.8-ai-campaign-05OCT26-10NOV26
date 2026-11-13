# AAR — Where's the Supersingular Curve (a_spot_super)

## Result
**SOLVED.** Flag = `[flag — recorded in FLAGS/isogenies/challenge-203-cryptohack-a_spot_super/flag.txt]` (the Montgomery
coefficient A, bare). Submitted 2026-10-12, +25 points (score 6400 → 6425),
API-verified via `submit_flag.py` score_delta.

## Source
- Statement page: https://cryptohack.org/challenges/isogenies/ (a_spot_super card).
- Provided file: `curves_1e476e7d608576c05a13b269d1481602.sage`
  (URL `https://cryptohack.org/static/challenges/curves_1e476e7d608576c05a13b269d1481602.sage`,
  verbatim copy in this folder).
- NOT consulted: `/solutions/`, `/solves/`, search-engine writeups. The Sutherland
  lecture notes / Wikipedia link (listed in the challenge) were NOT used as the answer.

## The flag (and verification)
`[flag — recorded in FLAGS/isogenies/challenge-203-cryptohack-a_spot_super/flag.txt]` — the **bare** Montgomery A of the one
supersingular curve among the 100. Verified: `ellcard` of that curve = p+1 exactly
(Frobenius trace 0), and it was the **unique** hit across all 100. Submitted via
`submit_flag.py a_spot_super <A>` → score_delta +25.

## How it was solved
1. Parsed `A_coefficients` (100 values) from the provided `.sage`; each curve is
   `y² = x³ + A·x² + x` over p = 2^127−1 (Sage `EllipticCurve(F, [0, A, 0, 1, 0])`).
2. **Supersingular test:** a curve over F_p is supersingular iff its Frobenius trace
   a = p+1−#E(F_p) is 0, i.e. **#E(F_p) = p+1**. Computed the exact point count with
   PARI/GP Schoof's algorithm (`ellcard`), ~400 ms/curve:
   ```gp
   default(parisizemax, 1<<30);            /* ellcard overflows the default 8 MB stack */
   p = 2^127-1;
   E = ellinit(Mod([0, A, 0, 1, 0], p));
   if (ellcard(E) == p+1, print("SUPER A=", A), 0);
   ```
3. Looped over all 100 A's (`solve.py` generates `ss_check.gp`). Exactly one hit:
   **idx 60, A = [flag — recorded in FLAGS/isogenies/challenge-203-cryptohack-a_spot_super/flag.txt]**, card = p+1.
4. Submitted the bare A.

## Learning points (the part worth keeping)
- **Do NOT test supersingularity by j-invariant in F_p.** Two traps, both hit this run:
  1. `j ∈ {0, 1728}` is NOT the supersingularity test over F_p — for p≡3 mod 4 there
     are ~p/12 distinct supersingular j-values mod p, not two (0 and 1728 are only the
     two *rational* ones). This test found nothing but the A=0 (j=1728) distractor.
  2. `j^((p-1)/2) ∈ {1,−1}` is **vacuously true for every nonzero j** (Euler's
     criterion) — it flags ALL 100 curves. It is not a supersingularity test.
  The robust test is the point count: supersingular ⟺ #E(F_p) = p+1.
- **PARI `if` is a 3-arg function** `if(cond, then, else)` — NOT a block statement.
  `if (c) stmt;` is a syntax error; put `print(...)` in the then-slot.
- `ellcard` overflows the default PARI stack; start the script with
  `default(parisizemax, 1<<30)`.

## What I did / did not do
- Did: parse the provided file, run Schoof point-counting on all 100 curves, identify
  the unique #E=p+1 curve, submit the bare A.
- Did not: use the lecture notes / Wikipedia as the answer; use any writeup.

## Limitations
None — flag submitted and API-verified (score_delta +25).

## Configuration
- Date: 2026-10-13 09:38 UTC (AAR written; solve submitted 2026-10-12).
- Host: Windows 11, shell bash (git-bash/MSYS), user OWNER.
- Interpreter: Python 3.12.0 (venv `~\tools\crypto-ctf\venv`).
- PARI/GP: `~\tools\gp64.exe` 2.17.4 standalone.
- Working dir: `~\Practice_runs\cryptohack_org`.
- Tools: `submit_flag.py` (cookie + requests), gp64 (Schoof). Artifacts: `solve.py`,
  `ss_check.gp` (generated), `curves_...sage`.
- Network contacts: cryptohack.org (statement + provided file), API (submit/verify).

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
