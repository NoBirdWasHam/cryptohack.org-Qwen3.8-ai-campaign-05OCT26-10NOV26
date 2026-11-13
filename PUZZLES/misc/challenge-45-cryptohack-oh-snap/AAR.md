# AAR — Challenge 45: Oh SNAP (CryptoHack Symmetric Ciphers / AES)

**Result:** SOLVED 2026-10-23. Flag: `[flag — recorded in FLAGS/aes/challenge-45-cryptohack-oh-snap/flag.txt]` — submitted,
`ok:true`, `score_delta=120`.
**Method:** iterative **Klein/PTW-style sigma attack** (Klein 2005 / Pyshkin–Tews–Weinmann
2007, vote form as in aircrack-ng's `guesskeybytes`) against the RC4(nonce‖FLAG)
keystream oracle, re-injecting the recovered flag prefix into the nonce each round.
~392k oracle queries in 3 rounds of 130k at ~79 q/s.

## Source
- Platform: CryptoHack, slug `oh_snap`, 120 pts, card on `challenges/aes/`.
- Service: `https://aes.cryptohack.org/oh_snap/send_cmd/<ciphertext>/<nonce>/` (GET only).
- Revealed source (in-scope): `cmd = ARC4.new(nonce + FLAG).decrypt(ct)`; the error
  echoes `cmd.hex()`. Not consulted: /solutions/, /solves/, third-party writeups.
- Academic references used (allowed, named per brief): Klein's keystream–key correlation
  as stated in the IEICE survey "Cryptanalysis for RC4 and Breaking WEP/WPA-TKIP"
  (Eqs. 3–8), and the sigma-vote implementations in aircrack-ng `aircrack-ptw-lib.c`
  (`guesskeybytes`) and wepwolf `ptw.rs` (`klein_cand`), retrieved 2026-10-23.

## The structure (verified live, session 1)
- `ct = 00*m` → error echoes `RC4(nonce‖FLAG)` keystream for any nonce ≤222 bytes.
- Oracle = "give me RC4 keystream for key `N ‖ FLAG`", FLAG a fixed unknown suffix.
- No hidden commands; 222-byte nonce cap is hard (session 1, `probe*.py`).

## Why session 1 stalled — and the fix
Session 1 correctly killed the KSA peel (222 cap) and guessed "FMS, heavy". Session 2
found the real blocker was a wrong mental model of the bias:
- **FMS as commonly misremembered** ("S[i+1]=0 after round i ⇒ z_i = K[i]+2 w.p. ½") is
  **empirically false** — flat over 200k random keys across every remembered condition
  variant × (z−K) delta (`fms_test.py`, `fms_search.py`).
- The **actual usable correlation (Klein)**: `K[l] = j_{l+1} − j_l − S_l[l]` and
  `S_l[j_{l+1}] = l − z_{l−1}` w.p. ≈2/256 (×1/e survival) ⇒ the vote

  `sigma_t := S_t⁻¹[(l − z_{l−1})] − j_t − Σ_{p=n}^{l} S_t[p]`

  estimates the **cumulative key sum** `K[n]+…+K[n+t]` with prob ≈1.36/256, plus the
  Maitra–Paul second estimator `z_l − j_t − sigma_t` (≈1.11/256; gated `z_l ≥ l`,
  `z_l ∉ j-history`). Flag byte t = sigma_t − sigma_{t−1}. Exactly aircrack-ptw.

## The attack
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

## Key numbers
- Full-strength per-sample excess ≈0.013 over the 1/256 floor (`bias_measure.py`:
  true 15.3k vs floor 12.9k at 200k samples).
- 130k samples/round ⇒ 7–13 confident bytes/round; 392k queries ≈85 min total.
- Keystream 96 B/query; local pipeline validated on a synthetic flag first
  (`test_pipeline.py`: exact recovery in 4×120k rounds).

## Learning points
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

## Limitations / failures (this session)
- FMS-condition search found nothing (200k+30k keys); had to retrieve the real Klein
  formula from academic sources. Internet Archive was offline; original FMS PDF not
  obtained — IEICE survey + aircrack-ptw code sufficed.
- First e2e test failed at byte 7 with 60k/round (margin ≈ σ) → 130k/round + gating.
- Initial tight charset truncated round 1 at uppercase 'R' → widened to printable.
- Guess-based tail completion verified False (correctly rejected by verifier).
- Rate ~79 q/s (8 workers), near the ~50 q/s politeness budget; no 429/5xx observed.

## Files
- `solve_oh_snap.py` — collector (`collect`), analyzer (`report`), DP + verifier.
  Repro: `python3 solve_oh_snap.py report r3.jsonl --known="crypto{w1R3d_equ1v4l3nt_pr1"`.
- `r1.jsonl` `r2.jsonl` `r3.jsonl` (+`*_collect.log`) — 392k live (nonce, keystream) pairs.
- `test_pipeline.py` `test_e2e.py` `klein_proto.py` `klein_tune.py` `klein_dp.py`
  `klein_iter.py` — local validation; `fms_test.py` `fms_search.py` `bias_measure.py`
  — bias discovery/measurement; `probe_live.py` — oracle probe.
- `flag_oh_snap.txt` — the flag.

## Configuration
- Windows 11, git-bash; python3 3.10 (pycryptodome ARC4); ~400k HTTPS GETs to
  aes.cryptohack.org; submission via `submit_flag.py` (ok:true, +120, 2026-10-23).

---

## Appendix — Session 1 (2026-10-05) analysis, preserved
- Keystream-echo oracle built; hidden-command probe (23 candidates) negative; 222-byte
  nonce cap verified rigorously (deterministic 500 at 223, cooldowns, varied inputs).
- KSA peel shown infeasible under the cap: peel of `FLAG[i]` needs `len(nonce)=255−i`
  (>222 for i<33) and the fixed suffix breaks single-byte isolation; peel-from-end
  yields `'}'` first — useless. (Note: KSA indexes the key cyclically, `K[i mod L]`,
  which also blocks bringing FLAG bytes to low rounds — FLAG bytes are always used at
  rounds ≥ len(nonce).)
- Identified the IV‖fixed-key statistical family as the intended path; flagged for
  revisit. Solved by session 2 via Klein/PTW as above.

---

<!-- AAR batch #9 quality upgrade (2026-11-02): publication sections appended; everything above this marker byte-identical to the pre-append AAR (hash in aar_batch9_pre.sha). -->

## Vulnerability (plain words)
The service decrypts your ciphertext with key `nonce || FLAG` and leaks the result via an error that echoes `cmd.hex()` — send all-zero ciphertext and the error prints the raw RC4 keystream for any key that ends in the flag, for any nonce up to 222 bytes. RC4's keystream is statistically correlated with its key-schedule state (Klein/FMS family), and the attacker-controlled nonce prefix lets you plant *known* key bytes in front of the flag and re-anchor: every recovered flag byte becomes a known KSA round for the next.

## How the answer follows
1. Oracle construction: `ct = 00*m` => error echoes `RC4(nonce||FLAG)` keystream (nonce <= 222 B verified live; 223 deterministically errors).
2. Usable bias (Klein 2005 in PTW vote form — NOT the folklore FMS): `sigma_t := S_t^-1[(l - z_{l-1})] - j_t - SUM_p S_t[p]` estimates the cumulative key sum `K[n]+...+K[n+t]` with prob ~= 1.36/256 (Klein weight 13, Maitra-Paul second estimator ~= 1.11/256, weight 4); flag byte t = `sigma_t - sigma_{t-1}` (bytes come out as differences; the known `crypto{` prefix pins the first sigmas).
3. Re-anchoring: `nonce = R(4 random) || known_prefix` makes KSA over `R || known || known` fully simulatable, so the frontier byte gets a full-strength vote (measured excess ~= 0.013 over the 1/256 floor: 15.3k true vs 12.9k floor at 200k samples, bias_measure.py).
4. Three live rounds x ~130k samples (~392k queries, ~85 min, 8 sessions, ~79 q/s, zero errors): round 1 prefix `crypto{` gained `w1R3d_e`; round 2 gained `qu1v4l3nt_pr1`; round 3 gained `v4cy?!}` closing `}`. Winning sigma buckets led runners-up by 1300-2300 votes over a ~9000-vote floor.
5. Certification: candidate flag must reproduce 30 held-out live keystreams (all four collections) before submission; that verifier rejected the near-miss tail `...pr1v4cy}`. Final: `[flag — recorded in FLAGS/aes/challenge-45-cryptohack-oh-snap/flag.txt]` — ok:true, score_delta=120. Pipeline first validated on a synthetic flag end-to-end (test_pipeline.py: exact recovery in 4x120k rounds).

## Limitations / attempts that failed
- The half-remembered FMS formulation (`S[i+1]=0 => z_i = K[i]+2 w.p. 1/2`) measured FLAT over 200k + 30k random keys across every remembered condition variant and (z-K) delta (fms_test.py, fms_search.py) — the real Klein formula had to be retrieved from academic sources; Internet Archive was down, the original FMS PDF was never obtained (IEICE survey + aircrack-ptw code sufficed).
- Session 1's KSA-peel idea is infeasible under the 222-byte cap (peeling FLAG[i] needs len(nonce)=255-i; RC4's cyclic key indexing keeps FLAG bytes at rounds >= len(nonce)); hidden-command probe (23 candidates) negative.
- First e2e test failed at byte 7 with 60k samples/round (margin ~= sigma) => raised to 130k/round + confidence gate (top1-top2 >= 3.5*sqrt(top2), printable); an initially tight charset truncated round 1 at uppercase 'R' => widened to printable.
- Top-M-per-state DP safety net and guess-based tail completion were implemented but the DP was never needed; the guess `...pr1v4cy}` was correctly rejected by the keystream verifier.

## Sources
- Academic references used during the solve (allowed math references, named per brief): Klein 2005 keystream-key correlation as stated in the IEICE survey "Cryptanalysis for RC4 and Breaking WEP/WPA-TKIP" (Eqs. 3-8); sigma-vote implementations aircrack-ng `aircrack-ptw-lib.c` (`guesskeybytes`) and wepwolf `ptw.rs` (`klein_cand`), retrieved 2026-10-23; Maitra-Paul second estimator. Revealed challenge source in-scope; NOT consulted: CryptoHack /solutions/, /solves/, third-party writeups.
- Upgrade-time comprehension check (batch #9, 2026-11-02): re-derived the sigma-telescoping and re-anchoring argument from `klein_*.py` and the r1-r3 collection logs offline; no live queries re-run, flag untouched.
