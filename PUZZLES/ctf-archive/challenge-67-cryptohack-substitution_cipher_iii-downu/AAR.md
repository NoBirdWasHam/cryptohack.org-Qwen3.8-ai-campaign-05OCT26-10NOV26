# AAR — substitution_cipher_iii-downu (DownUnderCTF2020 "Substitution Cipher III")
(prior attempt: challenge-296-...-downunderctf2020 — FAILED, no flag; this folder = retry with real F4)

## Challenge (recap)
Not a substitution cipher: Matsumoto-Imoto C* over GF(2), n=80. output.txt = 80 dense
QUADRATIC Boolean polys (public key) + ct1 (msg1 = inner[:10]) + ct2 (msg2 = inner[10:],
zero-padded to 80 bits). Inner flag <= 20 chars. Static, no listener.

## Toolchain saga (this session)
- python F4 (prior session) too slow; no Sage/Singular wheels on Windows.
- Built openf4 (C++ F4, GF2) with winlibs mingw64 gcc16: WORKS for plain GB but
  SEGFAULTS in transform() when x^2+x field equations are in the input (latent bug).
- Solution: prebuilt MSYS2 mingw-w64-ucrt-x86_64-msolve 0.11.0 package, extracted DLLs
  by hand (flint/gmp/mpfr/libgomp/openblas/zstd from winlibs+msys2 mirror) into
  ~/tools/msolvedir/ucrt64/bin. msolve.exe = neogb F4 + FGLM, full MQ solver.

## Attack
Direct MQ solving (no need for MI key-recovery): system = {f_i + ct_i} + Boolean
constraints. For msg2: exploit zero padding — if inner length L in [15,20] (prior session
proved >=15 by exhaustive guess-determine UNSAT for 11..14), then msg2 unknowns = first
L-10 bytes; variables x_{8b..79} fixed to 0 => b=5..10 gives 40..80 unknowns.
msg1: all 80 unknowns (+ASCII bit7=0 linear constraints as extra polys).

## Status
IN PROGRESS — sweep running (ms_sweep.log).

## Resume session (same day) — ROOT CAUSES FOUND
1. **ASCII-constraint bug (fatal for prior msg1/msg2 attempts):** encrypt() encodes each
   char MSB-first (`f'{c:08b}'`, zip(gens,B)), so printable-ASCII bit7=0 means
   **x_{8k}=0**, not x_{8k+7}. Prior ms/msg1_ascii.in etc. fixed the WRONG bits → msg1_ascii
   came back [-1] (UNSAT) and msg2_b10 "timed out" (no Boolean solution for wrong constraints).
2. **msg2 length:** correct-convention sweep already implied UNSAT for b=5..9 padding, and
   msg2 is at most 10 bytes ⇒ inner is exactly 20 chars, no padding. msg1 = 10 chars exactly.
3. **Old synth1 "17 BAD" mystery:** stale artifact; fresh fully-self-derived MI generator
   (mi_gen2.py, GF(2^80) bit-arith, Mobius quadratic coeff extraction, ct via bit-encode
   exactly as .sage) + fresh pipeline gives 0/80 violations and recovers known plaintext.
4. **Parametrization decode was fragile:** msolve RUR per-var rational values need w in
   GF(2^80); switched to `msolve -g 2` reduced GB (linear polys x_i+c ⇒ x_i=c, unambiguous).

## Validated pipeline
- mi_gen2.py: self-derived MI generator → synth80.txt with KNOWN msg1/msg2.
- mq.py build_input: substitute fixed 0 bits at x_{8k} (MSBs), 80 quad + 70 Boolean polys.
- msolve 0.11 `-t 2 -g 2`: synth80 70-var system solved in ~60 s; decode GB linear part;
  verify all 80 equations against synth ct (bad=0) and ASCII == planted plaintext. EXACT MATCH.

## Real run
m1real.in / m2real.in (real output.txt, 70 free vars each) solved with same settings.
Both GB runs finished in ~3 min (-t 2). Full linear reduced GB ⇒ unique solution:
msg1 = first 10 chars, msg2 = next 10 chars of the 20-char inner flag. Each half verified
by evaluating all 80 public polynomials at the recovered bits against the real ciphertexts
(0 violations each). FLAG: see flag_substitution_cipher_iii-downu.txt. Submitted via
submit_flag.py: ok:true HTTP 200, live solved-count 288→289, "Substitution Cipher III
(DownUnderCTF)" now present in the live solved list (reconcile truth check).

## Learning points
- VERIFY BIT-ORDER CONVENTIONS FROM THE SOURCE before constraining: one index off
  (8k vs 8k+7) poisoned the whole prior sweep and its "UNSAT ⇒ length" conclusion.
- A solver result that violates its own equations is a pipeline bug, never a crypto hint:
  re-ground with a fully self-generated instance whose plaintext is planted (mi_gen2.py).
- msolve `-g 2` (reduced GB) decodes unambiguously (x_i+c ⇒ x_i=c) whereas the rational
  parametrization needs GF(2^80) arithmetic to read; use the GB route when the ideal is
  expected 0-dimensional with linear staircase.
- ASCII MSB constraints cut the MQ from 80 to 70 unknowns — this is what made msolve
  finish in minutes instead of the prior 1500 s timeouts.

## Limitations
- Did not attempt MI key-recovery (Patarin-style); direct MQ is sufficient here.
- msg2-shorter-than-10 case was inferred (UNSAT sweep + ≤10 byte bound), not re-swept
  with correct bit order; not needed — recovered msg2 is exactly 10 printable chars and
  verifies against ct2.

## Files
- mi_gen2.py  — self-derived MI generator (synth ground-truth instances)
- mq.py       — instance parser / input builder (fixed-ASCII substitution) / msolve runner
- decode_v2.py, runsolve.py, verify.py — decode + verification helpers
- s80m1.in/.out/s80m1_gb.out — validated self-test (recovered planted 'W)-$L3,<s}', 0 bad)
- m1real.in/m2real.in, m1real_gb.out/m2real_gb.out — real solve
- flag_substitution_cipher_iii-downu.txt — the flag

## Sources
No external sources; provided materials only plus own in-campaign prior attempt/fresh self-derived tooling. Disclosure wording preserved verbatim:
> (prior attempt: challenge-296-...-downunderctf2020 — FAILED, no flag; this folder = retry with real F4)
> fresh fully-self-derived MI generator

## Current state of the attack
Ledger-hygiene annotation (2026-11-02 twin sweep; append-only, claims untouched):
CANONICAL folder for substitution_cipher_iii (DownUnderCTF2020). The solve and the
single ledger credit live HERE (real msolve pipeline, both halves verify 0/80, flag
submitted ok:true, live readback 288→289 — lines 46-53). The sibling
`challenge-296-cryptohack-substitution_cipher_iii-downunderctf2020/` is the
ATTEMPT-ARCHIVE of the earlier failed session (its AAR line 39 'No flag recovered';
lineage recorded at this AAR line 2: '(prior attempt: challenge-296-...-downunderctf2020
— FAILED, no flag; this folder = retry with real F4)'). One credit, counted here;
cross-refs now present in both AARs.
