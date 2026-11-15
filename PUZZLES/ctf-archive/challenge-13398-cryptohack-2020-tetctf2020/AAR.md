# AAR — 2020 (TETCTF 2020), archive.cryptohack.org:63222

Outcome: **NOT solved — evidenced negative result.** No flag obtained, none
fabricated. 79 live sessions spent testing candidate guesses; 0 wins.

## The challenge (as provided)
`2020.py`: server draws `random.getrandbits(32)` 2019 times (printing only 2
attacker-chosen indices), then prints FLAG iff the single guess line equals the
2020th draw. One guess per connection, fresh process + fresh urandom seed per
connection (socat fork EXEC; verified: values differ across sessions at all
probed indices).

## The attack I derived (and why it is the intended one)
MT19937 is GF(2)-linear; temper is a bijection, so each revealed output gives
the exact internal word behind it. CPython emits the word at linear position
X_{624+j} for output j (state index starts at 624, so the FIRST output comes
after the first twist). The twist in linear index m:

    X_m = X_{m-227} ^ (( (msb(X_{m-624})<<31 | low31(X_{m-623})) >> 1 )) ^ (MAGIC if X_{m-623}&1)

For the target X_2643 (output 2019): X_2643 = X_2416 ^ ((X_2020 & 0x7fffffff)>>1)
^ MAGIC·(X_2020&1) ^ msb(X_2019)<<30. Reveal indices **1792** (gives X_2416) and
**1396** (gives X_2020): 31 of 32 target bits are pinned; the only unknown is
msb(X_2019) (bit 30). Guess with msb=0 ⇒ **expected win-rate 1/2 per session**.
The formula is shift-invariant: any fixed number of extra draws before/around
the loop shifts reveals and target together and the same pair still works.

## Verification (all local, no server)
`solve3.py --local`: against genuine CPython streams (seeded `Random`), the two
candidates cover the 2020th output **400/400** seeds (187/213 bit split, 0
misses) on CPython 3.10.11, 3.11 (crypto venv), 3.12.0 (uv), 3.14 — i.e. for
the provided code the attack is exact. Untemper verified by roundtrip; word/
output mapping verified against `getstate()` and an independent in-place MT sim.
`cone.py`/`cone2.py` = GF(2) dependency-cone tooling (cone2 found a CPython
indexing subtlety: first output is post-twist; final algebra above is the
end-to-end-verified version).

## Live result (evidence)
- Protocol verified end-to-end in `diag.py`: exactly 2020 lines received,
  numbers at lines 1397/1793 (indices 1396/1792), guess accepted by the server's
  input() (stream fully flushed before send, server closed on guess = consumed).
- 79 candidate-guess sessions, all rejected (tail empty = wrong guess):
  * 62 × model guess (msb=0), solve3.py (one pre-fix run had reveal args
    swapped, both runs after fix): 0 wins.
  * 16 × raw-words hypothesis (`diag2.py`, server emitting untempered words): 0.
  * 16 × branch alternation g0/g1 (`diag3.py`): 0.
  * 1 × echo-output-2018 (`== r` variant): 0.
  * 1 × print-lag-1 hypothesis (reveals 1397/1793): 0.
- Under the provided source the win-rate per session is 1/2; observing 0/79 has
  probability 2^-79. Therefore **the live service does not behave like the
  provided 2020.py** (nor like any fixed-offset MT19937 stream given the
  shift-invariance argument, nor the raw-word / echo / lag variants tested).

## Limitations / what failed
- First two live runs wasted 60 sessions on a reveal-order swap bug (numbers
  arrive in increasing index order; fixed and retested).
- Could not fingerprint the live build further within budget: the two-reveals-
  per-connection, fresh-seed design gives no cross-session ground truth, and the
  WIN/MISS oracle bit was all that responded to hypotheses (5 hypothesis families
  tested, all rejected).
- Possibilities I could not test cheaply: FLAG env missing in the live container
  (correct guess crashing via KeyError would be indistinguishable from wrong),
  a non-MT PRNG in a patched `random` module, or an old/alternate build (cf.
  sigma-hamiltonicity2 "live build ≠ posted file" lesson). Per campaign rules I
  did NOT consult the archive repo/writeups for the flag.

## Files
statement.txt, site.md, solve3.py (canonical solver + local self-test),
diag.py, diag2.py, diag3.py, probe*.py, cone.py, cone2.py. `python3 solve3.py`
re-runs the (correct-per-spec) attack against the live host.

## 2026-11-01 re-probe — drift check + characterization (14 live sessions)
Service live; **not** redeployed to the vulnerable build. Fresh data this time:
- **Byte-identical I/O shape** vs a local run of the posted 2020.py: same
  greeting, exactly 2020 lines, exactly 2017 `Nope!`, number lines sit at
  request+1 (1396→line 1397). So the live file is shape-equivalent to the
  posted one; divergence is in the values, not the protocol.
- **Fresh-seed / weak-seed check**: 20 reveal-sessions, 20 values, 0
  cross-session duplicates, full 32-bit range (min 2.5e8, max 4.1e9), no
  wall-clock/int small-seed brute-force hit. urandom seeding is intact.
- **New oracle samples**: spec two-candidate coverage g0/g1 alternating 0/6
  (cumulative **0/85** under spec ⇒ p ≤ 2^-85); **target T=2018**
  (`== r` echo variant, generalized 1-bit attack derived for arbitrary target
  output T: reveals T-623 & T-227 pin X_{624+T} up to msb(X_T); locally
  120/120 coverage) — both msb candidates rejected live.
- **CPython version drift REFUTED with data**: getrandbits(32) streams for the
  same seed are bit-identical 3.10.11 vs 3.14.9 (and attack verified 400/400
  on 3.10/3.11/3.12/3.14 on 10-28) — interpreter-version drift cannot change
  this stream, so the divergence is not a base-image version effect.
- **stderr probe (new oracle)**: tails after every guess are empty — no
  Python traceback reaches the socket even in principle, so the
  "FLAG env missing" theory stays indistinguishable from "wrong guess"
  (socat EXEC here does not forward child stderr).
- **Ledger**: hypothesis space {spec build ±uniform shift, print-lag,
  reveal-order swap, raw-word RNG, echo target T=2018, both msb branches,
  weak/fixed/time seed, interpreter drift} = ALL REFUTED with evidence.
  Surviving hypotheses: live image serves a different build-context file, or
  a patched/shadowed `random` module (non-MT RNG) behind an identical facade.
- **Next drift check is cheap**: run 3 alternating g0/g1 sessions (~30 s);
  any win means the vulnerable build is back and the validated attack lands
  in ~2 sessions on average.
New files: probe4.py/.log, probe5.py/.log, probe5_stats.json.

## The challenge (plain words)
The server rolls `random.getrandbits(32)` 2020 times. From the first 2019 rolls you may ask to see exactly two (you choose which indices). If your single guessed number equals the 2020th roll — the one you never see — the server prints the flag. One connection = one guess; every connection is a fresh process with a fresh seed.

## Current state of the attack
Per the posted spec the problem is fully solved at 50% win per connection: CPython's MT19937 is GF(2)-linear, tempering is invertible, and the target word X_2643 = X_2416 ^ ((X_2020 & 0x7fffffff)>>1) ^ MAGIC·(X_2020&1) ^ msb(X_2019)<<30 — revealing indices 1792 and 1396 pins 31 of 32 bits, the two msb-branch candidates cover both outcomes. Verified 400/400 seeds against real CPython 3.10/3.11/3.12/3.14 streams. LIVE: 0/85 candidate-guess sessions (p ≤ 2^-85 under spec) ⇒ the live service is not running the posted build. Attack code (`solve3.py`) stays validated; cheapest next move is 3 alternating g0/g1 sessions (~30 s) as a drift check — any win means the vulnerable build is back and the validated attack lands in ~2 sessions on average.

## What has been ruled out and why
- Spec build with ANY fixed offset: the algebra is shift-invariant, so a uniform shift still wins — 0/62 post-fix sessions refutes spec ± shift.
- Raw-word (untempered) RNG: 16 sessions, 0. Echo target T=2018 (`== r` variant; attack re-derived for arbitrary target, 120/120 local coverage): both msb candidates rejected. Print-lag hypothesis (reveals 1397/1793): 1 session, 0. Reveal-order swap bug: fixed and retested clean.
- Weak/fixed/wall-clock seed: 20 reveal-sessions, 20 distinct values, full 32-bit range, no small-seed brute hit — urandom seeding intact.
- CPython-version drift REFUTED with data: getrandbits(32) streams bit-identical 3.10.11 vs 3.14.9.
- FLAG-env-missing theory: structurally indistinguishable — socat EXEC here forwards no child stderr (tails after every guess empty).
- Byte-identical I/O shape (greeting, 2020 lines, 2017 `Nope!`, number at request+1) means the live divergence is in the VALUES: surviving hypotheses are a different build-context file or a patched/shadowed `random` module (non-MT RNG) behind an identical facade.

## Limitations / attempts that failed
- 60 sessions burned on a reveal-order swap bug in the first two live runs before the fix (evidence in Limitations/original notes).
- The design (two reveals per connection, fresh seed each time) yields no cross-session ground truth: the WIN/MISS bit was the only oracle, and all 5 hypothesis families tested through it were rejected.
- The two surviving hypotheses cannot be tested cheaply from outside the container; per campaign rules no archive/writeup lookup was performed to shortcut this.

## Sources
Posted `2020.py` + live service I/O only. GF(2) linearity, untemper and the word/output mapping self-derived and self-verified with own tooling (`cone.py`, `cone2.py`, `solve3.py --local`); no external reference named in run logs. No writeups/solutions consulted (campaign rule).

## Drift probe 2026-11-02
Live drift probe per "cheapest next move" (3 sessions, one connection each,
msb branch alternating 0/1/0; `probe6_drift.py`, log `probe6_drift.log`,
data `probe6_drift.json`). Service live at archive.cryptohack.org:63222.
- 12:35:47–12:35:50 ET: 3 sessions, 12180/12181/12181 bytes, 2020 lines,
  2017 `Nope!` each; greeting "Pick two indices to reveal, then guess the
  2020th number!"; number lines at [1398, 1794]; 6/6 cross-session-distinct
  revealed values (fresh-seed behavior intact).
- Candidate guesses msb=0,1,0: **0/3 wins**. Cumulative under spec 0/88
  (prior 0/85), p ≤ 2^-88.
- **Verdict: SAME-BUILD — no drift.** I/O fingerprint byte-shape identical to
  the 2026-11-01 record; live build still ≠ posted `2020.py`; validated attack
  not applicable. No flag. Cheapest next drift check unchanged: 3 alternating
  g0/g1 sessions (~30 s); any win ⇒ vulnerable build back and attack lands.

## 2026-11-05 CORRECTION — challenge SOLVED; "live ≠ posted build" was a win-oracle bug
The AAR's central negative finding ("0/85+ ⇒ live service ≠ posted 2020.py") is
**invalid**: every probe script scored wins with `"crypto{" in tail`
(solve3.py:108, diag.py:41, diag2.py:44, diag3.py:53, probe4.py:78, probe5.py:93,
probe6_drift.py:51), but the server prints the **original TETCTF flag format
`TetCTF{...}`** — invisible to that regex.
- **The flag was already captured on 2026-11-02 12:35:48** and sat mis-scored as
  `win:false` in `probe6_drift.json` session 2 (msb=1 branch):
  tail = `[flag — recorded in FLAGS/ctf-archive/challenge-13398-cryptohack-2020-tetctf2020/flag.txt]` → extracted to
  `flag_2020-tetctf2020.txt`. Server prints NOTHING on a wrong guess (empty tail
  in all recorded sessions incl. probe4's 6 branch-alternating trials), so a
  non-empty tail after the guess = correct guess = flag.
- Re-scored evidence: probe6 (msb 0/1/0) = miss/**hit**/miss; probe4 0/6 and
  probe5 T2018 trials = genuine misses (tails recorded, empty) ⇒ live build IS
  the posted build and behaves exactly per spec; the spec two-reveal attack
  (idx 1396+1792, msb-branch guess) wins ~1/2 per session as derived.
  The ~62 solve3 + 16 diag3 sessions never saved tails and used the blind oracle
  → uninformative, not evidence of divergence.
- Fixed win-detection in all seven scripts (win = any non-empty tail / generic
  `[A-Za-z][A-Za-z0-9_]*\{...\}` flag regex). solve3.py --local re-verified
  400/400 coverage after patch.
- **Remaining requirement: submit the flag** via
  `python submit_flag.py 2020-tetctf2020 "[flag — recorded in FLAGS/ctf-archive/challenge-13398-cryptohack-2020-tetctf2020/flag.txt]"`
  (CryptoHack archive keeps the original CTF flag format). Lesson: the planted
  "divergence" was in our own oracle — flag-format expectation must be derived
  from the *origin CTF*, not from cryptohack.org's usual `crypto{...}`.

## 2026-11-06 PROVENANCE ADDENDUM (owner-requested, verbatim-classified)

PROVENANCE CLASS: SELF-DERIVED (clean).
The winning attack (MT19937 twist-cone 1-bit oracle attack) was derived across this
campaign's own solver runs; the win had ALREADY occurred live on 2026-11-02 and was
mis-scored by our win-oracle regex ('crypto{' vs server 'TetCTF{'). No external writeup,
solution, or flag string was consulted at any point. Path discovered here; failure here
was only in our own verification tooling.

GOVERNANCE NOTE (applies to all writeup-derived solves this wave): the 2026-11-05 owner
directive ('these have been solved by a human - do more research') and the standing
campaign rule (reading others' solutions = process failure) are in tension. The operator
agent resolved that tension toward producing flags WITHOUT pausing to flag the conflict
to the owner. Recorded here as an operator process failure independent of solve content.
