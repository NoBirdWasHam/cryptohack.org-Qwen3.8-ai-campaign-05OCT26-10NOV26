# AAR — rsa_permutation (WACON 2022), challenge-285 — SOLVED

**Flag (self-derived; handed by the service after my factorization was accepted):**
`[flag — recorded in FLAGS/ctf-archive/challenge-48-cryptohack-rsa_permutation-wacon2022/flag.txt]`
Submitted 2026-10-29: `ok:true`, per-challenge solved 276→277 (archive: score_delta 0 = credited-archived, expected).
Saved in `flag_rsa_permutation-wacon2022.txt`. No third-party solution/writeup consulted.

## The challenge
Listener `archive.cryptohack.org:45400`, chal.py (matches live behavior exactly):
- e = 293, strong 1024-bit p,q with gcd(e, p−1)=gcd(e, q−1)=1.
- Server prints `n = p·q`, then the 256-hex-digit strings of `d_p = e⁻¹ mod (p−1)` and
  `d_q = e⁻¹ mod (q−1)`, each run through an **unknown random permutation of the 16 hex
  symbols** (same permutation for both strings).
- Then asks for u,v with `1 < u,v < n`, `u·v = n` → prints FLAG.
- Guards: sha256 PoW (6-hex-zero prefix) and `signal.alarm(300)` for the whole session.

## The attack
Core relations: `e·d_p = k_p·(p−1) + 1`, `e·d_q = k_q·(q−1) + 1`, with `k_p, k_q ∈ [1,292]`,
plus `p·q = n`. Unknowns: k_p, k_q, and the symbol map M (observed→true, a bijection on 16 digits).

**Digit-DP (LSB-first base-16 DFS)** over the three simultaneous multi-precision
identities, state = (position i, carry of n-multiplication, two split carries of the
`e·d − k·p` chains, partial injective map M, p0, q0):
- i=0: p0 odd with `p0·q0 ≡ n₀ mod 16`; q0 forced; `e·d_{p,0} ≡ 1−k_p+k_p·p₀ (mod 16)`
  fixes M[obs_p[0]] (13 = e⁻¹ mod 16), similarly for d_q.
- digit i: branch on true digit `pᵢ` (16 choices); `qᵢ` is then uniquely forced by the
  `p·q = n` digit equation (p0 odd ⇒ invertible mod 16); the d_p/d_q equations then
  uniquely force the required true digits `d_{p,i}, d_{q,i}`, which must be consistent
  with M or extend it injectively. Two forced constraints per branch ⇒ the DFS
  collapses to ~1.1k nodes per (k_p,k_q) pair; full 292×292 scan ≈ 99M nodes ≈ **10–40 s**
  in C (`dp4.exe`).
- Leaf: exact big-int check of `e·d_p = k_p(p−1)+1`, same for q, and `p·q = n`; prints p.

Send `u = p`, `v = n//p` → server prints the flag.

Key numbers (live session): PoW answer found in 1–6 s (multiprocessing, 2²⁴ tries expected);
DP scan 1.6–38 s; well inside alarm(300).

## Validation
- Synthetic clone (`local_gen.py`, seed 1, ground-truth p/q/perm in `local_instance.json`):
  full-range `dp4.exe local_instance.txt` recovered the **exact ground-truth p** and a map
  consistent with `e·d_p = k_p(p−1)+1` exactly.
- Live `live_dp.log`: unique SOLUTION, 256-hex p divides live n; both factors pass `sympy.isprime`.

## Limitations / honest notes (failures with evidence)
1. **`dp5.exe` (child's last scanner) is broken**: targeted run at the *correct*
   (k_p,k_q)=(259,49) on the local instance explores only 1459 nodes and finds nothing,
   although the ground-truth solution must satisfy its constraints — unsound pruning was
   introduced in dp5. `dp4.exe` solves the same input. The pre-existing `full.log`/`prog.log`
   "done" with no solution was a dp5-era full scan (identical node counts to my dp5-class
   runs); the "scan exhausted, no answer" conclusion inherited from the child was **wrong**.
   Do not resume/extend dp5.
2. **First live session returned "fail"** because the client parsed the DP output with
   regex `p=([0-9a-f]+)`, which matched the `kp=85` on the SOLUTION line and sent 133.
   The correct factor was in the same log (`\np=` fix → solved on retry).
3. No Sage/fpylll needed; pure integer digit DP.

## Files
- `dp4.c/.exe` — working solver; usage: `dp4.exe <file: n_dec, sp, sq>` (writes found.txt)
- `dp5.c/.exe` — BROKEN (see Limitations 1); `dp2/dp3` superseded
- `local_gen.py`, `local_instance.{txt,json}` — validation rig with ground truth
- `solve_live2.py` — full live client (PoW + DP + factor submit); regex fixed 2026-10-29
- `live_dp.log`, `full4.log` — successful live/local full scans (SOLUTION lines)
- `flag_rsa_permutation-wacon2022.txt`

## Learning points
- "Permutation of hex digits" on d_p/d_q + n is a **digit-DP problem**: two forced-digit
  equations plus the multiplication collapse the search to ~1k nodes per (k_p,k_q);
  the flag's Heninger–Shacham pun is the hint that factorization from d-like leakage is the theme.
- Parse structured solver output with anchored patterns (`\np=`); `kp=85` poisoned a live session.
- If a solver scans the full parameter space and finds nothing on a **ground-truthed**
  instance, suspect the solver — targeted test at the known-correct parameters is the
  cheapest soundness check (this is exactly what exposed the dp5 regression).

## Vulnerability (plain words)
The server hands out n = p·q and BOTH RSA CRT exponents d_p = e⁻¹ mod (p−1), d_q = e⁻¹ mod (q−1) — but with the 16 hex symbols of both strings shuffled by one shared unknown permutation. The leak is still d-like (the flag itself puns on Heninger–Shacham): e·d_p − 1 is a small multiple of p−1 with multiplier k_p ∈ [1,292]. Factoring then reduces to discovering, simultaneously and digit-by-digit in base 16, the symbol permutation and the two tiny multipliers.

## How the answer follows
1. Three identities must hold at once: p·q = n, e·d_p = k_p(p−1)+1, e·d_q = k_q(q−1)+1.
2. LSB-first base-16 digit DP: branch on the true digit p_i (16 choices); q_i is *forced* by the multiplication identity (p0 odd ⇒ invertible mod 16); the two exponent identities then *force* the true digits of d_p, d_q, which must agree with the partial map M or extend it injectively. Two forced constraints per branch ⇒ ~1.1k nodes per (k_p,k_q); full 292×292 scan ≈ 99M nodes ≈ 10–40 s in C (dp4.exe).
3. Leaf = exact big-int check of both identities + p·q = n. Send u = p, v = n//p → server prints the flag. Timing fit the 300 s alarm (sha256 PoW 1–6 s, scan 1.6–38 s).
4. Validation: on a synthetic clone with ground-truth p/q/perm, dp4.exe recovered the exact p; the live scan returned a unique SOLUTION with 256-hex p dividing the live n and both factors passing sympy.isprime.

## Limitations / attempts that failed
- dp5.exe had unsound pruning — it finds nothing on the ground-truth instance even at the *correct* (k_p,k_q)=(259,49) (1459 nodes); the earlier inherited "scan exhausted, no answer" conclusion was a dp5-era false negative, exposed by a targeted test at known-correct parameters. Do not resume dp5.
- First live session sent 133: the client's regex `p=([0-9a-f]+)` matched `kp=85` on the SOLUTION line; anchored `\np=` fixed it (solved on retry).

## Sources
chal.py (matches live behavior) + the live listener only; flag was handed by the service after our own factorization was accepted. No third-party solution/writeup consulted (per AAR). Mathematics: elementary modular arithmetic + carry-tracking digit DP; the e=293 small-multiplier range follows from gcd(e, p−1)=gcd(e, q−1)=1 with strong 1024-bit primes.
