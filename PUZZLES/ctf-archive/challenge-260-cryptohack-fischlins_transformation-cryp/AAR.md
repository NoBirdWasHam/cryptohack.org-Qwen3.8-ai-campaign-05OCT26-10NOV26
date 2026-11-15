# AAR - fischlins_transformation (CSC Belgium, archive twin of sigma-fischlin)

STATUS: SOLVED - original row credit 2026-10-25; own live-service derivation recorded during the verification audit run completed 2026-11-14 (audit-run submit receipt: solved 314 -> 315).

## Problem
Fischlin OR-proof game over service archive.cryptohack.org:3583, 64 rounds. Each round
leaks w0 (response to input 0); prover runs a Fischlin-OR transform with hidden bit b;
solver must determine b (16 attempts/round; the guess applies to the last attempt).

## Attack - b=0 replay
Under the b=0 hypothesis, side 0 is real: e_sim = e1, r_b = (z0 - e0*w0) mod q, and
a0,a1,z1 are constant across the prover e-loop, so for every e-prime <= e_cur recompute
e0-prime = e-prime^e1, z0-prime = r_b + e0-prime*w0 mod q, and check
RO(a0,a1,e-prime,e0-prime,e1,z0-prime,z1) < 2^506. Replaying the server search path:
exact reproduction (no hit below e_cur, hit at e_cur) = consistent with b=0 (posterior
error (63/64)^(e_cur+1)); ANY deviation = CERTAIN b=1 signal.
64/64 rounds decided without contradiction; flag released by service.

## Flag
crypto{fishy_fischlin_www.youtube.com/watch?v=tL6dcQEY62s}

Identical to the sigma-fischlin flag (same challenge, archive twin). This row was
independently re-derived against the live archive service, not copied: the prior credit
had NO own derivation (errata E8); this one does.

## Artifacts
artifacts_2026-11-14/ - solver fis_play.py / fis_relay.py; diagnostics fis_diag.log,
fis_dist.py, fis_dp_check.py; server semantics fischlin_chal.py, fischlin_lib.py, params.py.
Full derivation record: scratch ch_results_w7b.json; transcript deleg_c452499c/task-0.

## Limitations
Per-round soft evidence when the replay reproduces exactly (posterior above); a full-game
contradiction-free run plus service flag release is the end-to-end verification.
Flag format: crypto{...} containing a URL - submit verbatim.
