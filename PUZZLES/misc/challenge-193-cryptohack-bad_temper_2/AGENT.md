---
record: agent-aar
puzzle: challenge-193-cryptohack-bad_temper_2
category: misc
url: https://cryptohack.org/challenges/bad_temper_2/
status: solved
date: 2026-10-23
flag_ref: "FLAGS/misc/challenge-193-cryptohack-bad_temper_2/flag.txt"
flag_sha256: 6116609428aa70fda8306f942bd1e417b4327570db66a348f88aaa18b4acf7d0
skills: [ctf-mt19937-cracking]
human_twin: AAR.md
---

# AGENT — bad_temper_2 — AAR (CryptoHack, 150 pts, misc)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack" [OBSERVED text; evidence tag applies to its source, not each claim]
1. **Collect 624 consecutive tempered words** (78 `get_seed` calls). Since `left==0`
   after seeding, these are `temper(twist(S0))` where `S0` = state right after seeding.
2. **Untwist** (part-1 technique, `ctf-mt19937-cracking` skill) → `S0`. The usual
   low-31-bits-of-word-0 ambiguity is moot: seeding forces `S0[0]=0x80000000`.
3. **Invert CPython's `init_by_array` analytically** (no z3 needed):
   - loop1: `mt[i] = (mt[i] ^ ((mt[i-1]^(mt[i-1]>>30))*1664525)) + key[j] + j`
   - loop2: `mt[i] = (mt[i] ^ ((mt[i-1]^(mt[i-1]>>30))*1566083941)) - i`
   - loop2 touches each index once, in order **2..623 then 1** (`i` is *not* reset
     after loop1 — the critical quirk). Undo it backwards: `L1[i]=(F[i]+i)^T2(F[i-1])`
     for i=623..3; `L1[1]=(F[1]+1)^T2(F[623])`; `L1[2]=(F[2]+2)^T2(L1[1])`.
   - loop1 first pass writes each index i=2..623 exactly once, from the *old*
     `S0[i]=init_genrand(19650218)[i]` and the *new* `L1[i-1]`:
     `K[(i-1)%keylen] = L1[i] - (S0[i] ^ T1(L1[i-1])) - ((i-1)%keylen)` — direct,
     and every word is over-determined (~26 agreeing equations each).
4. **Undo the `Lib/random.py` bytes→int layer**: `Random.seed(bytes)` first computes
   `X = int.from_bytes(secret + sha512(secret).digest(), 'big')` and splits X into 24
   little-endian 32-bit words = the init_by_array key. So `K[23..16]` (big-endian)
   = secret, `K[15..0]` = sha512 tail → a free integrity check that passed.
5. Verify model reproduces all 624 observed words + a 79th `get_seed` block, then
   submit `{"option":"secret","secret":<hex>}`.

## reusable-rules
- CPython's `init_by_array` is **not** one-way: both mixing loops are triangular
  (each step mixes with the just-written neighbour), so the seeding is analytically
  invertible from the state alone. The usual "use z3" approach (SECCON 2022 writeups)
  is overkill.
- `random.Random.seed(bytes)` ≠ raw bytes as key: the Python wrapper hashes
  (`bytes + sha512(bytes)` → big int → LE words) before the C layer. The sha512
  tail doubles as a checksum of the recovered secret.
- Off-by-one hell: loop2 inherits `i=2` from loop1's end (order 2..623,1). Forward
  models that "reset i=1" silently mismatch; the inverse must mirror the exact order.
- raw.githubusercontent/jsDelivr/GitHub API were all blocked on this host; the real
  browser tool fetched `raw.githubusercontent.com` fine — good fallback for sources.

## anti-patterns / limits
- First two forward-model guesses (original mt19937ar `mt[(i+623)%624]` variant;
  and a mis-parenthesized variant) both failed against `getstate()` — kept only
  after reading the actual `_randommodule.c` + `Lib/random.py`.
- Inversion assumes `keyused==24` exactly (fails with prob ~2^-32 if the secret
  starts with 4 zero bytes; the sha512 self-check would catch it, not silently err).
- Assumes server CPython ≥3.11 seeding semantics (identical since 3.2-era for this
  path); the in-solver 79th-block check would flag any version drift before submit.

## artifacts [OBSERVED]
- code: 13438.py, probe1.py, solve.py, test_offline.py
- data/logs: flag_bad_temper_2.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
CPython source files `_randommodule.c` and `Lib/random.py` — fetched via the real browser after raw.githubusercontent/jsDelivr/GitHub API were blocked on this host. CPython source is the seeded-generator *specification*, not a solution writeup; untwist step follows the `ctf-mt19937-cracking` skill. No third-party writeups (incl. the SECCON-2022 z3 approach referenced dismissively in notes) consulted.
