---
record: agent-aar
puzzle: challenge-293-cryptohack-smithing_contest-ecsc_2024_it
category: ctf-archive
url: https://cryptohack.org/challenges/smithing_contest-ecsc_2024_it/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-19-cryptohack-smithing_contest-ecsc_2024_it/flag.txt"
flag_sha256: f607dddf96d1952c5802c726fbe3612dc5b545f4543ad37162badced3b3d2ced
skills: []
human_twin: AAR.md
---

# AGENT — smithing_contest-ecsc_2024_it (SOLVED)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
The interactive blinded verification (verifier sends C=x·y·R for secret x,y; "signer" replies t,r) is
**existentially forgeable for any (R,S) by anyone**: both check equations

  (0) e(R,S)^x = e(Q,Qid)^(x) · r^(H(m)·y⁻¹)
  (1) r^(y⁻¹) · t^x · e(P_G1,Qid)^x = e(R+Q,P_G2)^x

are satisfied by publicly-computable pairings once we choose R and S with matching pairing-profiles.
The two-round blinding stops a cheating *signer*, not a forger who never needs the secret key.
(Not an implementation bug in the pairing/PKG — those are fine, as the header claims.)

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Earlier files attack.py/attacker.py/atk_run.py/fp2solve*.py/elim.py/identify.py/toy*.py explored
  extracting u or s via Fp2 dlog/tower identification (fp2solve*, identify, elim) — abandoned as ~2^64+ work
  once the key-free forge was seen; they are not needed.
- H0 root-choice ambiguity vs Sage `lift_x` was calibrated live (min-root matched; flip fallback coded but unused).
- Could not distinguish pairing e from e^c by any local test (bilinearity is c-invariant) — the decisive
  check was the live e(P_G1,du0)==e(Q,Qid_me) identity + final accepted verification.

## artifacts [OBSERVED]
- code: atk_run.py, attack.py, attacker.py, elim.py, forge.py, identify.py, probe_srv.py, scratch_ell_point.py, tower.py
- data/logs: flag_smithing_contest-ecsc_2024_it.txt, forge3.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Challenge-provided scheme source + live listener (archive.cryptohack.org:25469). Academic reference named by the original AAR: SageMath source `ell_point.py` (sagemath/sage repo) fetched to pin ate_pairing/_miller_ semantics — a math/library reference, not a challenge writeup. Pairing/tower arithmetic from standard pairing literature. No third-party writeups consulted; flag handed by the live service after our own forgery was accepted.
