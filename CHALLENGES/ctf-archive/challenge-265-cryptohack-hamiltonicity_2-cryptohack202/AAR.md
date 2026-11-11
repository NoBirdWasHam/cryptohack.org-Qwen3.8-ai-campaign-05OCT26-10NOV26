# AAR — hamiltonicity_2-cryptohack202 (folder 265)

**Result: NEGATIVE (evidenced).** The hosted instance is sound as hosted by my
independent analysis; no flag obtained; nothing submitted. Per SOLVER_BRIEF,
an evidenced negative-result AAR is a success case here. No third-party
writeups/solutions consulted; no flag sourced from any answer file.

## What the challenge is
Non-interactive ZKP (global Fiat-Shamir) that the server's fixed 5-node digraph
(3-cycle + 2-cycle, NO Hamiltonian cycle) has a Hamiltonian cycle. 128 rounds;
prover sends A (25 Pedersen commitments) + z (response) per round BEFORE any
challenge exists; challenges = low 128 bits of the FINAL chained sha256 state.

## Fingerprint evidence (live == posted build)
- MD5s of provided files match the /static/challenges/ URL hashes exactly (site.md).
- Live traceback frames `/app/chal.py:75` and `/app/hamiltonicity.py:70` match
  the posted files line-for-line (_local/probe1.log, attack1.log).
- Server's hidden G == posted else-branch G: honest permuted-G commitments
  were ACCEPTED in bit-0 rounds (probe1: rounds 0-1 accepted).
- Challenge derivation confirmed GLOBAL-FINAL-LSB-slice: 3 live bits `001`
  matched the final-state low-bit prediction, while per-round-chained-LSB (110),
  per-round-independent-LSB (111), global-MSB (111), per-round-chained-MSB (110)
  all disagreed. Grind experiment (solve2.py, want LSB(state_i) per round,
  round0 want=0): live announced bit=1 -> per-round derivation excluded twice.

## Why the hosted build is sound (reduction)
1. **Commitments binding.** P=2q+1 (P 1025b, q 1024b prime), h1,h2 hardcoded
   squares => order q. BSGS for dlog_{h2}(h1) negative up to 2^22 (~4M table,
   gmpy2). Without dlog, an entry opens to at most one of {0,1} -> no per-entry
   equivocation (classic Pedersen fact; HPS-style textbook reasoning).
2. **Per-round dichotomy.** bit=1 needs 5 cycle entries opening to 1 (testcycle);
   bit=0 needs ALL 25 entries opening to some permutation of the true G
   (open_graph asserts + matrix equality). Binding => a matrix passes e=1 iff its
   1-entries contain a 5-cycle (impossible for permuted G: edges form 3+2 cycle;
   Hamiltonian cycle in a bipartite-image argument also impossible for duplicate-
   row "permutations" since 5 is odd and testcycle asserts a single cycle).
   A matrix passes e=0 iff it is exactly a permuted-G commitment. Both at once:
   requires equivocation -> excluded by 1.
3. **No universal response shape.** z=[ints,...] crashes e=1 (`int[0]`
   TypeError — observed twice in live tracebacks); z=[pairs,...] crashes e=0
   (G[[..]] / G[".."] TypeError). Bools alias to ints only, never both shapes.
   JSON type seams (float/str/bool/dict/inf/NaN rows) reach only TypeErrors or
   assert-failures = connection death, never "accepted".
4. **Bits unpredictable and globally coupled.** Prover controls A fully
   (incl. +kP stringification freedom per entry, hash-input seam), but the bit
   vector is a 128-bit function of ALL commitments; any per-round strategy change
   rewrites every bit => success requires a 2^128 fixed point / 128-zero-bit digest.
5. `python -O` hypothesis checked by reasoning: removing asserts cannot repair
   the shape wall (TypeErrors survive -O; G[str] still crashes e=0).

=> Prover success prob <= 2^-128 as hosted. 199 historic solves must predate
this exact build (2020-era original likely had per-round/non-chained hashing,
which IS grindable — my solve2.py implements that attack and stands ready;
it failed against live, excluding the hypothesis empirically).

## Attempts (what was tried / outcomes)
1. Honest prover (example.py logic, raw sockets) — passes bit-0 rounds by
   construction; dies at first bit-1 on no-Hamiltonian G (expected). solve.py, probe.py.
2. Pedersen parameter audit: safe-prime structure, orders, h1*h2==1, small dlog
   BSGS 2^22 — all negative.
3. Prefix/per-round FS grind (strategy alternating real/fake, LSB of running
   state): 250 grinds, live bit0 mismatch -> hypothesis excluded (solve2.py).
4. Live bit-derivation fingerprint vs 5 hypotheses — global-final-LSB confirmed.
5. Port neighborhood scan 34560-34644: only 34597 alive (no old build).
6. Type/shape seam inventory (see reduction 3): crash-only, never accept.

## Limitations
- Could not brute-force the bit vector (2^128) — believed impossible, not proven.
- dlog BSGS stopped at 2^22; a planted medium dlog (~2^40+) is not excluded,
  though the hardcoded bases look like honest randoms (comment says generated
  by random randint-squared).
- Did not attempt social/meta routes (forbidden or out of scope per brief).

## Learning points
- Bytes-repr prompt (`b'...'` echoed) = Python-2-era prompt quirk but the live
  traceback line numbers here match a Py3 file — banner artifacts can mislead;
  line-number/traceback diffing is the reliable build fingerprint.
- 3 printed bits + a traceback are enough to fingerprint the FS derivation
  against multiple hypotheses; grind experiments must be designed as
  hypothesis discriminators, not just attempts.

## Files
- solve.py (honest prover, runnable), solve2.py (prefix-grind attack, runnable),
  _local/probe.py, _local/probe1.log, _local/attack1.log, _local/probe1_A.json,
  _local/relay.py (local test relay), statement.txt, site.md.

## The challenge (plain words)
A non-interactive ZKP (global Fiat-Shamir) claiming the server's fixed 5-node digraph -- a 3-cycle + a 2-cycle, which has NO Hamiltonian cycle -- has one. 128 rounds; the prover must send A (25 Pedersen commitments) + response z per round BEFORE any challenge exists, and the 128 challenge bits are the low bits of the FINAL chained sha256 state -- so the bit-vector is a 128-bit function of every commitment the prover ever makes.

## Current state of the attack
Evidenced NEGATIVE: the hosted instance is sound as hosted -- prover success probability <= 2^-128 by the recorded reduction -- and the 199 historic solves must predate this exact build (a 2020-era original with per-round/non-chained hashing WOULD be grindable; solve2.py implements that attack and stands ready; it failed against live, excluding the hypothesis empirically). Build fingerprint (live == posted): MD5s of provided files match the /static/challenges/ URL hashes; live traceback frames /app/chal.py:75 and /app/hamiltonicity.py:70 match the posted files line-for-line; the server's hidden G == posted else-branch G (honest permuted-G commitments ACCEPTED in bit-0 rounds); challenge derivation = global-final-LSB-slice (3 live bits 001 matched; per-round-chained-LSB 110, per-round-independent-LSB 111, global-MSB 111, per-round-chained-MSB 110 all disagreed).

## What has been ruled out and why
- Commitment equivocation: P = 2q+1 (P 1025-bit), h1,h2 hardcoded squares => order q; BSGS for dlog_{h2}(h1) negative up to 2^22 (~4M table, gmpy2); without the dlog each entry opens to at most one of {0,1}.
- A response shape passing both branches at once: bit=1 needs 5 cycle entries opening to 1 (testcycle); bit=0 needs ALL 25 entries opening to a permutation of the true G; a permuted G cannot contain a 5-cycle (edges form 3+2; Hamiltonian-cycle-in-bipartite-image argument; 5 odd + testcycle asserts a single cycle). z=[ints,...] crashes e=1 (int[0] TypeError -- observed twice live); z=[pairs,...] crashes e=0 (G[[..]]/G[".."] TypeError); JSON type seams (float/str/bool/dict/inf/NaN rows) reach only TypeErrors or assert-failures = connection death, never "accepted".
- Bit prediction / grinding: any per-round strategy change rewrites ALL bits -> success requires a 2^128 fixed point / 128-zero-bit digest; 250 prefix-grinds (solve2.py, round0 want=0) hit live bit=1 -> per-round derivation excluded twice; port neighborhood scan 34560-34644 found only 34597 alive (no old build).
- `python -O` hypothesis: checked by reasoning -- removing asserts cannot repair the shape wall (TypeErrors survive -O; G[str] still crashes e=0).
- Not excluded (recorded limits): dlog BSGS stopped at 2^22, so a planted medium dlog (~2^40+) is not excluded (hardcoded bases look like honest randint-squared randoms); brute-forcing the bit vector itself is believed impossible, not proven. Honest-prover baseline (solve.py) passes bit-0 rounds by construction and dies at first bit-1 as expected; failed attempts and probes logged in _local/.

## 2026-11-03 re-screen (resume run #2, model-dropout recovery)
Service LIVE (one documented connection, `_local/reprobe_2026-11-03.py` →
`_local/reprobe_2026-11-03.log`): same banner; round 0 of a fresh honest
commitment set announced bit=1 == my local global-final-LSB prediction; crash
traceback frames /app/chal.py:75 and /app/hamiltonicity.py:70 identical
line-for-line => NO BUILD DRIFT since 2026-10-28. Negative stands.
Two upgrades to the reduction, both new since run #1:
1. **The non-bijective-permutation gap is now closed exhaustively.** The
   verifier never checks that z's `permutation` is a bijection — permute_graph
   accepts repeated/negative indices, so bit-0 matrices include B_p[i][j] =
   G[p_i][p_j] for ANY index vector p, not just permutations. I brute-forced
   all 5^5 positive and all 9^5 in-range (with negatives) p: NO B_p has a
   Hamiltonian cycle among its 1-entries. Proof matching the data: a Hamiltonian
   cycle in B_p maps under i->p_i to a CLOSED WALK of length 5 in the server G
   (disconnected 3-cycle + 2-cycle); closed-walk lengths available there are
   {0,3,6,...} (3-comp) union {0,2,4,...} (2-comp) — 5 is impossible since no
   walk can switch components. Hence no "dual-strategy" matrix openable in both
   branches exists; every round is a forced 50/50 bet => <= 2^-128.
   (Replaces run #1's hand-wavy "bipartite-image / 5 is odd" line.)
2. **Independent parameter audit (fresh, this run):** P = 2q+1 exactly; isPrime(P)
   and isPrime(q) both True (MR, PyCryptodome); h1^q = h2^q = 1; h1,h2 not in
   {0,1,P-1}; h1 != h2; h1*h2 != 1. => order-q bases in a safe-prime group,
   binding under the generic q-order dlog assumption (~2^512), consistent with
   run #1's BSGS-2^22 negative.
Exact stall point: soundness wall as characterized; nothing left to derive
locally. Remaining paths to any flag: (a) server-side build change — re-probe
cheaply (1 connection) each campaign pass, the old-build attack (per-round FS
grind) is already implemented in solve2.py and stands ready; (b) a planted
dlog_{h2}(h1) beyond 2^22 (not excluded, judged unlikely); (c) none known.

## Sources
Provided chal.py/example.py/hamiltonicity.py; live listener + local relay (_local/probe.py, probe1.log, attack1.log, probe1_A.json, relay.py); 2026-11-03 re-probe (_local/reprobe_2026-11-03.py + .log); own solve.py/solve2.py. Reasoning standards named in AAR: classic Pedersen binding facts (HPS-style textbook reasoning). No third-party writeups/solutions consulted; no flag sourced from any answer file.

## 2026-11-05 validation unit (nn=265; web-only, ZERO listener connections spent)
1. **CONFIRMED COMPANION with folder 237 (sigma-hamiltonicity2) — same instance, shared
   intended path.** chal.py/example.py/hamiltonicity.py are BYTE-IDENTICAL between the two
   folders (md5 eedb8152…/ffb8932a…/bc3acea5…). The zkp course statement (live-fetched
   2026-11-05, `_local/cat_zkp_live.html`) says verbatim: "This challenge is hosted on the
   CTF archive. Find the corresponding challenge in that category, solve it, then enter the
   flag here." One listener (archive.cryptohack.org:34597), one flag, two submission points.
   site.md's earlier note "NOT the sigma-course variant (different host/build era)" is
   WRONG and corrected here; every 237 probe hit this same :34597 service, so all 237
   empirical findings apply to 265 verbatim (and vice versa).
2. **Posted-file drift check free of budget**: live archive card (`_local/cat_arch_live.html`)
   embeds md5s in file URLs — chal_eedb8152…, example_ffb8932a…, hamiltonicity_bc3acea5… —
   all == our copies. No posted-build drift as of 2026-11-05.
3. **NEW ANOMALY**: solve counters are STILL RISING vs our scrapes — archive 199→202,
   course 245→254 (late Oct → 2026-11-05). Cumulative counters, but +3 archive solves in
   ~a week against a listener every probe says is unsolvable-as-hosted. Hypotheses:
   intermittent/round-robin backends (old build sometimes served), recent re-solves of a
   cached flag path, or a community mechanism we haven't identified.
4. **Ledger data-quality warning**: progress.json flags for 237 ("h_{i+1}") and 265
   ("crypto{local_test_flag}") are HARVESTING JUNK — 265's came from the FAKE flag set in
   `_local/relay.py` line 3 (local test relay env var). No real flag exists for either card.
5. **Budget ledger (protocol sessions on :34597, documented)**: folder-237 era ≈15-17
   (probe1–9b + solve_edges 10-25; probe13/14 10-26, probe14 ≤5 grounds; solver#7 exactly 1
   10-28); folder-265 era 4 (probe1, attack1, solve2 fingerprint run, 2026-11-03 reprobe).
   Sanctioned rate = 1 drift re-probe connection per campaign pass; last spent 2026-11-03;
   2026-11-05 pass budget 1/1 UNUSED. Banner port-scans don't count (no protocol session).

## 2026-11-05 backdoor-window pass (nn=265; companion of folder-237 addendum)
1 connection SPENT (budget 1/1): max-coverage discriminator payload — per-round
LSB grind t_i=i%2 (solve2-style generalized: bit-1 rounds commit a REAL cycle
so they also pass a no-chaining testcycle; bit-0 rounds permuted-G). Offline-
validated both ways before sending: old per-round build clone => 128/128 +
local flag; current batch clone => 2 accepted + chal.py:75/hamiltonicity.py:70.
LIVE: 2 accepted, printed bits 011 == first 3 bits of the local final-digest
prediction, identical traceback frames (/app/chal.py:75 ->
/app/hamiltonicity.py:70). => current batch build served; NO old-backend
intermittency observed this draw; solve2 per-round hypothesis excluded live
3rd time. Artifacts: _local/discriminate_2026-11-05.py,
payloads_2026-11-05.json, _local/discriminator_2026-11-05.log.
Rising-counter anomaly remains unexplained by observed evidence; the payload
is now a standing win for any future single-connection probe IF a per-round
backend is ever served.
2. Pedersen binding final sweep [2^44,2^60] both directions launched as
self-tested multi-herd kangaroo (folder 237 kangaroo_window.py v3; scaled
self-tests 8/8 PASS, full-window shadow planted in the same window PASS/FAIL
appended below).

## Addendum 2026-11-06 — backdoor-window PASS CLOSED (kangaroo campaign + final verdict)

### Harness (kangaroo_window.py v3) — validated before use
- Scaled self-tests PASS 8/8 (planted recovery, W = 2^20/2^28/2^36/2^44 x both
  directions).
- Full-window shadow validation (planted x0 = 840705078688783942 in [2^44,2^60),
  production params: 2 tame + 2 wild herds, Sbar = sqrt(W)/2 = 5.77e8, DP trap
  2^20): h2h1 PASS and h1h2 PASS — exact recovery of planted x0 at 4.80e9 total
  steps in 1.22 h each, 1 cross, 0 false positives. Harness proven end-to-end at
  production scale.

### Production scan [2^44, 2^60), both directions, 6 h wall each (2026-11-06 02:18–08:18 EST)
- dlog_{h2}(h1): NOT FOUND — 24,335,645,959 total steps (6.084e9/herd),
  23,390 DPs, 1 flock round, 0 crosses (status budget-exhausted).
- dlog_{h1}(h2): NOT FOUND — 24,446,160,730 total steps, 0 crosses.
- Aggregate rate ~1.13e6 jumps/s sustained; checkpoints with per-herd distance
  records: kangaroo_h2h1.ckpt.json / kangaroo_h1h2.ckpt.json.

### Confidence (Monte-Carlo, shadow-calibrated geometric mean mu=6.2e8 steps,
conservative vs theoretical Sbar/2=2.7e8)
- P(miss | planted dlog uniform in window) ~ 5e-4; worst-position (x near 2^44)
  P(miss) = 1.7e-3. Positions near 2^60 excluded by ~1.2 h mark (shadow
  capture-time ratio).
- Combined with harness-validated BSGS negatives (< 2^44 both dirs) and dead
  Pohlig-Hellman (q-1 = 2 * 7 * hard-composite), the Pedersen binding-backdoor
  window [2^44, 2^60) is CLOSED: no planted dlog in either direction across the
  entire open range.

### Campaign verdict (237/265 one-connection pass)
1. Single sanctioned :34597 session spent 2026-11-05 as solve2-style max-coverage
   discriminator (128-round payload: wins old per-round build, fingerprints
   current batch build). Result: accepted 2, printed bits 011 == low-bit prefix
   of local chained-digest prediction, traceback /app/chal.py:75 ->
   /app/hamiltonicity.py:70 => CURRENT SOUND BATCH BUILD. No old-backend
   intermittency observed; rising solve counters are not attributable to a
   per-round-flawed backend during this window.
2. Kangaroo window: empty (both directions, bound above).
3. => 237/265 remain UNSOLVABLE-AS-HOSTED under the current build, with
   build-history rationale: the old per-round build (killable by solve_edges /
   solve2) is no longer served; the current batch build's chaining assert is
   sound; the parameter-generation binding backdoor exists only below 2^44
   (already exhausted) or above 2^60 (infeasible, > 2^59.9 kangaroo work).
