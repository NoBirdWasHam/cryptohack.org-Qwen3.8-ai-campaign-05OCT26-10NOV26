# ERRATA UPDATE — 2026-11-14 (post owner account clear)

Historical note: ERRATA-LEDGER-2026-11-09 remains the frozen audit record of that date;
this file records only the deltas between it and the final 2026-11-14 corpus state.
Reconciliation at close: LIVE score=17370 solved=316 == local 316 == queue 316,
unmatched in both directions = 0, score diff = 0 (`reconcile.py` output, 2026-11-14).

## Row-class changes

1. **#260 fischlins_transformation (E8 SUPERSEDED).** Folder
   `challenge-260-cryptohack-fischlins_transformation-cryp` created; full AAR from an OWN
   live-service replay derivation (worker w7b, b=0 replay of the Fischlin-OR search path,
   64/64 rounds, service flag release); artifacts_2026-11-14/ copied in; ledger flag +
   solved_date set. Submit receipt: solved 314 -> 315. The 2026-10-25 twin-fold credit is
   no longer the evidence class for this row.

2. **#247 authenticator-firebird_intern (folder-field correction + independent re-solve).**
   Ledger folder field corrected from the legacy misname
   `challenge-247-cryptohack-blind-ecsc_2023_norway2023` to the real folder
   `challenge-13396-cryptohack-authenticator-firebird_intern`. Post-clear badge re-earned
   with a DIFFERENT algorithm (rainbow tables, rb2.c ~12 min/16 cores vs the 2026-10-28
   GPU blake3 brute); dated AAR section + artifacts_2026-11-14/. Submit receipt:
   solved 313 -> 314.

3. **#304 unbalanced-icc_athens2022 (NOT SOLVED -> SOLVED).** Durfee-Nguyen trivariate
   Coppersmith (m=8, t=5, a=1; rank-126 lattice; determinant margin ~+46 bits/dim;
   Bareiss-resultant extraction; p|N verified). AAR header now SOLVED with the resolution
   on top; the 2026-10-31 evidenced-negative sections remain valid FOR THE BIVARIATE ROUTE
   ONLY. flag file + ledger flag set; artifacts_2026-11-14/. Submit receipt:
   solved 315 -> 316.

4. **#zkpintro / #letsproveit.** Badges re-earned post-clear 2026-11-14 (fresh
   derivations); ledger notes carry the receipt reference.

## Verification audit run (completed 2026-11-14)

The owner clear (2026-11-12 window) dropped 87 badges; all were INDEPENDENTLY RE-DERIVED
2026-11-13/14. Original solve dates stand; this run is the audit completion notation.
Documented in `VERIFICATION-AUDIT-2026-11-14.md` (87 rows, per-file raw
counts, 26 hard ledger joins by normalized slug/name, remainder worker name-labels) with
raw solve scripts preserved in `SUPPORT/2026-11-14-verification-audit/` (106-file tarball +
result JSONs + full-clear capture `FULLCLEAR_316_2026-11-14.png`, vision-verified: all
14 category cards n/n, CTF Archive 76/76).

## Tally deltas vs 2026-11-09 audit

* Flag-recorded ledger rows: 200 -> 202 (#260, #304 gained flags).
* No-flag documented rows (NOT_RECORDED + E1 class): 86 -> 84.
* Credited rows missing folder-or-AAR: challenge-tier 0 (83 remaining are course-tier
  rows, class E1, documented — course lessons have no challenge folder by design).
* E8 open items: 1 -> 0.
* AARs carrying a 2026-11-14 section: 3 (+ this file + WAVE-2026-11-14.md).

## Skill-corpus portability gate (new, 2026-11-14)

Standing rule now recorded in ctf-practice-runs: before any publication the SKILL corpus
is grepped for host-identifying tokens outside the two designated host-state skills
(windows-crypto-toolchain; ctf-practice-runs Host-local section). First sweep caught 4
CTF skills with absolute tool paths (cado-nfs-msys-port, ecdsa-lcg-nonce-unknown-modulus,
groebner-mq-toolkit, wireshark-tshark); all replaced with `<toolroot>`-style placeholders.
Sweep is CLEAN as of 2026-11-14 (challenge-skill corpus).

## Provenance red lines (unchanged, restated for the final state)

Submitted flags are exclusively self-derived or service-given. The one disclosed
retrieved-flag row (unrandom_dsa, TAINTED class, flag banked per owner ruling) retains
its provenance note. No writeups/solution pages were consulted at any point in the
post-clear wave.
