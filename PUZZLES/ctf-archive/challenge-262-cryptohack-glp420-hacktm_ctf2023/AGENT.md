---
record: agent-aar
puzzle: challenge-262-cryptohack-glp420-hacktm_ctf2023
category: ctf-archive
url: https://cryptohack.org/challenges/glp420-hacktm_ctf2023/
status: solved
date: 2026-10-28
flag_ref: "FLAGS/ctf-archive/challenge-262-cryptohack-glp420-hacktm_ctf2023/flag.txt"
flag_sha256: 05685136bb0376c538cdc47c18ec91dd00663b3948937627dbd023533f90e61f
skills: []
human_twin: AAR.md
---

# AGENT — GLP420 (HackTM CTF 2023, CryptoHack ctf-archive, nn 262)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
`e = t − a·s` (and s) are ternary ⇒ the ring-LWE instance is catastrophically weak:
the Kannan/CVP lattice has determinant q^210 per 420 dims while the target point sits
at distance ‖(s_fold, e_fold)‖ ≈ 24, i.e. a unique-CVP gap of ~5·10^5. Plain LLL+Babai
recovers it. The hint that the ring splits over Z as (x^210−1)(x^210+1) cuts the lattice
in half and keeps the folded secret/err entries in [−2, 2].

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- BKZ-40 / LLL (fpylll proved) on the 840×420 degenerate lattice ({M·s + q·v} = Z^420
  since M is invertible mod q ⇒ CVP meaningless): >400 s with no result, killed; the
  degeneracy was realized from theory afterwards.
- ζ=±i 4-component and 12th-root 12-component splits: Babai output max|fold| > bound
  (huge values), root cause above.
- Live: attempt 1 timeout (extra rdline ate `a_enc` — no banner on socket); attempt 2
  lll5 rare "stuck" guard → retry; attempt 3 SUCCESS in ~31 s:
  `flag = '[flag — recorded in FLAGS/ctf-archive/challenge-262-cryptohack-glp420-hacktm_ctf2023/flag.txt]'`. Submitted
  (submit_flag.py: ok 200, solved 270→271); progress.json → solved; reconcile.py clean.

## artifacts [OBSERVED]
- code: probe.py, probe2.py, probe3.py, server.sage, solve.py, solve_v2.py, solve_v3.py, solve_v4.py, solve_v5.py, solve_v6.py
- data/logs: FLAG.txt, det_done.txt, f1_result.txt, flag_glp420.txt, gtrue.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Platform: CryptoHack, ctf-archive card 'GLP420 (HackTM CTF)' (challenge file per site.md).
- Statement provenance: statement.txt in folder (begins: "GLP420 (HackTM CTF 2023) — CryptoHack ctf-archive  I have developed a variant of...")
- Provided material as stored in folder: FLAG.txt, det_done.txt, f1_result.txt, flag_glp420.txt, gtrue.txt, probe.py, probe2.py, probe3.py
- Not consulted: /solutions/ pages, third-party writeups (campaign no-cheat rule).
