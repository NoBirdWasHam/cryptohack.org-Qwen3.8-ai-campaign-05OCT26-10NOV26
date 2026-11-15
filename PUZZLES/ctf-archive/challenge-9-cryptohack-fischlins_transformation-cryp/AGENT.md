---
record: agent-aar
puzzle: challenge-260-cryptohack-fischlins_transformation-cryp
category: ctf-archive
url: https://cryptohack.org/challenges/fischlins_transformation/
status: solved
date: 2026-10-25
flag_ref: "FLAGS/ctf-archive/challenge-9-cryptohack-fischlins_transformation-cryp/flag.txt"
flag_sha256: sha256:5b04e70e0d89f45430968fb88299511f487ec5282d4207b55b89ee9ea2bebd6c
skills: [zkp-fiat-shamir-ctf]
human_twin: AAR.md
---

# AGENT — fischlins_transformation (CryptoHack ctf-archive, CSC Belgium)
Machine twin of AAR.md. Archive twin of sigma-fischlin (same game, same flag string).

## System [OBSERVED]
- Fischlin OR-proof game vs archive.cryptohack.org:3583; 64 rounds; each round leaks w0 (response to input 0).
- Prover runs a Fischlin-OR transform with hidden bit b; solver guesses b; 16 attempts/round, guess applies to the last.

## Attack — b=0 replay of the server search path [OBSERVED, self-derived 2026-11-14 audit run]
- Under b=0: side 0 real -> e_sim = e1, r_b = (z0 - e0*w0) mod q; a0,a1,z1 constant across the prover e-loop.
- For every e' <= e_cur: e0' = e'^e1, z0' = r_b + e0'*w0 mod q; check RO(a0,a1,e',e0',e1,z0',z1) < 2^506.
- Exact reproduction of the server's search (no hit below e_cur, hit at e_cur) = consistent with b=0
  (posterior error (63/64)^(e_cur+1)); ANY deviation = CERTAIN b=1 signal.
- 64/64 rounds decided without contradiction; service released the flag.

## Pitfalls
- This row's 2026-10-25 credit had NO own derivation (errata E8); this replay is the derivation. Do not
  treat the sigma-fischlin solve as evidence for this row or vice versa beyond the shared flag string.

## Verify
artifacts_2026-11-14/: fis_play.py / fis_relay.py solvers; fis_diag.log; server semantics fischlin_chal.py,
fischlin_lib.py, params.py. Offline replay check reproduces hit/no-hit pattern per round.
