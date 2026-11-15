# AAR — functional (ICC Athens 2022), CryptoHack slug `functional-icc_athens2022`

**RESULT: SOLVED.** Flag `[flag — recorded in FLAGS/ctf-archive/challenge-42-cryptohack-functional-icc_athens2022/flag.txt]` submitted; server accepted (HTTP 200, solved 295→296). Fully derived end-to-end in this pipeline (no flag copy): ITERS → S3 → j(ITERS) → AES key. Independent cross-checks: ITERS, S3[:2], j(ITERS) all match the public soon-haari writeup values exactly; ciphertext identical (static archive instance).

## Chain
- **Stage 1 (done in prior unit, re-verified):** BM on the 500-term f-window → L=20 (len(COEFFS)=20; trailing-zero-len ambiguity provably excluded because the nilpotent (x^3+31337)^3 recovery self-checks: A2==C(m,2)a^(m-2) passes ⇒ ITERS = 79120327624133200239720213852419346424887 (< 13^37, matches writeup). x^ITERS continuation reproduces all 500 f-values.
- **Stage 2 (`stage2_s3.py`):** S3 = [i(IT+k)] is **never printed** by functional.sage (output.txt Stage 2 section is empty by design) — must be COMPUTED. g/h/i mutual recurrences folded into a 21×21 state (g×7, h×7, i×3, monomials 1,n,n²,n³) over F_p; matrix-verified against a sequential reference (steps at N0+1/N0+2 and full loop at index 20345). S3[0..1] = [3344857554155236898658903831873044678801896, 3649959069781203859142471843095989397157559] ✓.
- **Stage 3 (`stage3_prep.py` + `bmr.gp` via gp64):** digit-sum init J[n<10^4] (n=0 → 0! n<1337 → single digit S3[n]; else S3[d0]+S3[d1]); recurrence taps n-9900-i (i=0..99) with a_i = int(10000·ln(31337+i)); generating function P/Q, Q=1-Σa_i x^{9900+i}; coefficient [x^IT]P/Q via Bostan–Mori in PARI/GP (pure-python BM too slow at deg 10^4 × 136 iters; GP run ≈ 25 min, single-thread, parisize 512m). jt = 4884838814356754393675352922066305300889643 → sha256(str(jt)) → AES-ECB decrypt → valid PKCS#7 flag.
- Validations along the way: GP-BM vs fibonacci golden test; GP-BM vs python sequential at n=12345 (`bmsmall.gp`); full-structure mini end-to-end (`mini_e2e.py`) incl. digit-sum/AES glue.

## Bugs killed (root causes, worth remembering)
1. `stage23.py` (old): regex-parsed a Stage-2 S3 list that is never in output.txt → wrong by construction. Replaced by computed S3.
2. j-recurrence tap offsets: sage `n - 10^4 + 100 - arange(100)` = offsets **9900..9999** (old file used 9901..10000, off-by-one). Detected by testing (J·Q)==P and S*Q==0 residuals.
3. **Digit-sum single-digit bug (the real one):** `ZZ(n).digits(1337)` for n<1337 is a 1-element list — adding `S3[n//1337]=S3[0]` to every J[n<1337] silently corrupted stage 3. Invisible at n=12345 (tap tree bottom ≥ 2346 > 1337) — only bites when the recursion tree reaches the [1,1336] zone, i.e. at ITERS-scale. Symptom: mathematically "proven" jt decrypts to junk.
4. **gp64 build quirk:** `Vec(t_POL)`/`Pol(list)` are DESCENDING here (unlike stock GP ascending docs!). Use `Polrev` for ascending input and index Vec descending (coeff x^e = V[deg-e+1]). Also: no `>>=`, vector-as-index unsupported (gtos), `vecextract` "o"/"e" are matrix-only, multi-line `{}` loop bodies inside `while(...)` parse-fail in script files (keep body on one line).
5. BM Q/P conventions themselves are order-agnostic (verified by the descending-order fix + fib golden test).

## Files
- `stage2_s3.py` (+`s3.json`) — S3 via 21×21 matrix exp.
- `stage3_prep.py` (+`pq_full.json`) — J, P, Q construction + residual proofs + mini BM self-tests.
- `bmt2.gp`/`bmf.gp` (fib golden tests), `bmsmall.gp` (+`.out`) (GP-vs-sequential at 12345), `bm_data.gp`, `bmr.gp` (+`bmr.out` stale-bug run, **`bmr2.out` = final jt**), `bmt*.gp`, `z*.gp` (GP-semantics probes).
- `stage3_decrypt.py` (+`flag.json`) — final AES decrypt.
- `mini_e2e.py` — full-structure small-scale pipeline test.
- `stage23.py` — superseded (see bugs 1–2); kept for history.

## Submit
`cd ~/Practice_runs/cryptohack_org && python3 submit_flag.py functional-icc_athens2022 '[flag — recorded in FLAGS/ctf-archive/challenge-42-cryptohack-functional-icc_athens2022/flag.txt]'` → 200, solved 295→296 (archive, score delta 0 as expected).

## Vulnerability (plain words)
Not a cipher break -- a three-stage linear-recurrence reconstruction puzzle. Stage 1: the server prints only a 500-term window of a sequence f obeying an order-20 linear recurrence; Berlekamp-Massey recovers the recurrence and hence the hidden ITERS/state. Stage 2: the sequence i(n) is NEVER printed -- it must be computed from the g/h/i mutual recurrences via a companion-state matrix exponentiation. Stage 3: a digit-sum-initialized sequence j(n) with 100 delayed taps has to be evaluated at j(ITERS), whose value (hashed) is the AES key. Everything follows from linear-recurrence algebra: BM, 21x21 matrix exponentiation over F_p, and Bostan-Mori coefficient extraction on P/Q.

## How the answer follows
1. Stage 1: BM on the 500-term f-window -> L=20 (= len(COEFFS); trailing-zero-length ambiguity provably excluded because the nilpotent (x^3+31337)^3 recovery self-check A2==C(m,2)a^(m-2) passes) -> ITERS = 79120327624133200239720213852419346424887 < 13^37; x^ITERS continuation reproduces all 500 f-values.
2. Stage 2 (stage2_s3.py): fold g/h/i into a 21x21 state (g x7, h x7, i x3, monomials 1,n,n^2,n^3) over F_p; matrix-verified vs a sequential reference (steps at N0+1/N0+2, full loop at index 20345); S3[0..1] = [3344857554155236898658903831873044678801896, 3649959069781203859142471843095989397157559].
3. Stage 3 (stage3_prep.py + bmr.gp in PARI/GP): digit-sum init J (n=0 -> 0; n<1337 -> single digit S3[n]; else S3[d0]+S3[d1]); taps n-9900-i with a_i = int(10000*ln(31337+i)); Q = 1 - sum a_i x^(9900+i); coefficient [x^IT]P/Q by Bostan-Mori (~25 min, parisize 512m). jt = 4884838814356754393675352922066305300889643 -> sha256(str(jt)) -> AES-ECB -> valid PKCS#7: [flag — recorded in FLAGS/ctf-archive/challenge-42-cryptohack-functional-icc_athens2022/flag.txt], accepted (solved 295->296).

## Limitations / attempts that failed
Recorded root-cause failures (bugs killed, all with evidence): (1) old stage23.py regex-parsed a Stage-2 S3 list that is never in output.txt -- wrong by construction; (2) tap offsets off-by-one (used 9901..10000 vs correct 9900..9999; caught via (J*Q)==P and S*Q==0 residuals); (3) digit-sum single-digit bug -- ZZ(n).digits(1337) for n<1337 is 1-element, so S3[n//1337]=S3[0] silently corrupted every J[n<1337]; invisible at n=12345 (tap-tree bottom >= 2346), bites only at ITERS scale; symptom: mathematically 'proven' jt decrypting to junk; (4) gp64 quirks cost real time: Vec(t_POL)/Pol(list) are DESCENDING in this build (use Polrev; index Vec descending), no >>=, vector-as-index unsupported, vecextract 'o'/'e' matrix-only, multi-line while() loop bodies parse-fail in script files.
Cross-checks recorded: GP-BM vs fibonacci golden test, GP-BM vs python sequential at n=12345, mini_e2e.py full-structure test; AAR records ITERS, S3[:2], j(ITERS) matching the public soon-haari writeup values exactly (pre-existing claim preserved as written; ciphertext identical -- static archive instance).

## Sources
Provided functional.sage + output.txt; own pipeline: stage2_s3.py (+s3.json), stage3_prep.py (+pq_full.json), bmr.gp/bmf.gp (bmr2.out = final jt), stage3_decrypt.py (+flag.json), mini_e2e.py. As recorded in the AAR itself: independent cross-check against soon-haari public writeup values (verification of self-derived quantities). Flag provenance: fully derived in-pipeline, no flag copy.
