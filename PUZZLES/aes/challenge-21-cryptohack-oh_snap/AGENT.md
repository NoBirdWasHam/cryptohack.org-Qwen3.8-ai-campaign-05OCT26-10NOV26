---
record: agent-aar
puzzle: challenge-21-cryptohack-oh_snap
category: Symmetric Ciphers
url: https://cryptohack.org/challenges/oh_snap/
status: solved
date: 2026-10-23
flag_ref: "FLAGS/aes/challenge-21-cryptohack-oh_snap/flag.txt"
flag_sha256: 4622161d4340b982a82761b4876de534c22eaa02aa5a496cc513e91fcb9900dc
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 45: Oh SNAP (CryptoHack Symmetric Ciphers / AES)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Key trick — **prefix-in-nonce re-anchoring**: `nonce = R(4 random) ‖ known_prefix`.
Key = `R ‖ known ‖ FLAG`, so KSA rounds over `R ‖ known ‖ known` are fully simulatable
and the first unknown flag byte gets a **full-strength** vote (zero unknown rounds
before it); later bytes get telescoped votes decaying with intervening unknown rounds.
Per sample: simulate KSA over `nonce‖known`; for each target `l`: Klein vote weight 13,
MP vote weight 4. Confidence gate: extend prefix while `top1−top2 ≥ 3.5·√top2` and byte
printable; next round re-anchors. Safety net: top-M-per-state DP over sigma tables +
**keystream-prediction verifier** (candidate flag must reproduce held-out live
keystreams) — gating sufficed, DP never needed.

Rounds executed (live, 8 parallel sessions, ~79 q/s, zero errors):
| round | prefix | samples | bytes gained |
|---|---|---|---|
| 1 | `crypto{` | 130,840 | `w1R3d_e` (7→14) |
| 2 | `crypto{w1R3d_e` | 130,634 | `qu1v4l3nt_pr1` (14→27) |
| 3 | `crypto{w1R3d_equ1v4l3nt_pr1` | 130,577 | `v4cy?!}` (27→34, closes `}`) |

Winning sigma buckets led runners-up by 1300–2300 votes over a ~9000-vote floor
(130k×16.5/256) — unambiguous. Final flag verified against 30 held-out keystreams from
all four collections (incl. smoke) before submitting.

## reusable-rules
- **Don't trust half-remembered FMS formulations — measure the bias first.** The
  working condition/vote is Klein's sigma vote, not the "S[i+1]=0 ⇒ z_i=K[i]+2"
  folklore (empirically flat).
- **Prefix-in-nonce re-anchoring** converts a decaying-bias statistical attack into a
  constant-cost-per-byte-window attack: every recovered byte makes one more KSA round
  known, so the frontier byte always sees the strongest bias.
- **Sigma (cumulative-sum) voting** avoids needing `j_{l+1}` directly; bytes come out
  as differences; the known `crypto{` prefix pins the first sigmas.
- **A perfect verifier is free** (predict held-out keystreams) — makes it safe to
  terminate a statistical attack early and to reject plausible-looking guesses
  (`…pr1v4cy}` was wrong; the tail is `?!}`).
- Flag text (`w1R3d_equ1v4l3nt_pr1v4cy` = Wired Equivalent Privacy) confirms the
  intended WEP framing.

## anti-patterns / limits
- FMS-condition search found nothing (200k+30k keys); had to retrieve the real Klein
  formula from academic sources. Internet Archive was offline; original FMS PDF not
  obtained — IEICE survey + aircrack-ptw code sufficed.
- First e2e test failed at byte 7 with 60k/round (margin ≈ σ) → 130k/round + gating.
- Initial tight charset truncated round 1 at uppercase 'R' → widened to printable.
- Guess-based tail completion verified False (correctly rejected by verifier).
- Rate ~79 q/s (8 workers), near the ~50 q/s politeness budget; no 429/5xx observed.

## artifacts [OBSERVED]
- code: bias_measure.py, fms_search.py, fms_test.py, klein_dp.py, klein_iter.py, klein_proto.py, klein_tune.py, probe.py, probe2.py, probe_live.py, solve.py, solve_oh_snap.py, test_e2e.py, test_pipeline.py
- data/logs: flag_oh_snap.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Platform: CryptoHack, slug `oh_snap`, 120 pts, card on `challenges/aes/`.
- Service: `https://aes.cryptohack.org/oh_snap/send_cmd/<ciphertext>/<nonce>/` (GET only).
- Revealed source (in-scope): `cmd = ARC4.new(nonce + FLAG).decrypt(ct)`; the error
  echoes `cmd.hex()`. Not consulted: /solutions/, /solves/, third-party writeups.
- Academic references used (allowed, named per brief): Klein's keystream–key correlation
  as stated in the IEICE survey "Cryptanalysis for RC4 and Breaking WEP/WPA-TKIP"
  (Eqs. 3–8), and the sigma-vote implementations in aircrack-ng `aircrack-ptw-lib.c`
  (`guesskeybytes`) and wepwolf `ptw.rs` (`klein_cand`), retrieved 2026-10-23.
