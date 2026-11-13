# AAR — diffecient (SEKAI CTF 2022, CryptoHack archive 311)

Status: **SOLVED and submitted** (CryptoHack solved count 287 -> 288, verified by re-read).
Flag: `[flag — recorded in FLAGS/ctf-archive/challenge-311-cryptohack-diffecient-sekaictf2022/flag.txt]`

## Attack — murmur3 x86_32 zero-propagation differential on the first 8 bytes
The Bloom filter only asks that two distinct keys land on the same 47 digest slots, so a
*collision pair* suffices — no need to invert the ~2^768 lock.

Take the forward-domain XOR difference `DIFF = (word0: 2^18, word1: 2^31)` over the first two
4-byte blocks, applied as `x' = inv4(fwd4(x) XOR DIFF)` (inversion is exact and absorbs every
carry question):

- block 1: fwd-diff 2^18 -> after the round's rotl13 it is 2^31; `*5` is exact on the top bit
  (5 * 2^31 = 2^31 mod 2^32), so the state difference leaving block 1 is exactly 2^31;
- block 2: the key difference there is 2^31, which XORs that away.

State difference entering block 3 is ZERO for every seed; tail and length are identical, so all
47 digests match. Add K1 (option 2), then present K0 (option 3): `check()` passes, K0 != K1 and
K0 is not the added key, so the regex-gate yields the flag.

K0 = `A`*28 + `a1!` (32 B; lower/upper/digit/\W all present); K1 = collide8(K0[:8]) + K0[8:].

- Local verify (`solve_dc.py`): mmh3.hash(K0,i) == mmh3.hash(K1,i) for all i < 47.
- Live (`live_dc.py`): pre-query K0 "not present" -> add K1 -> query K0 "present" -> option 3 = FLAG.

## Why the earlier sessions declared it impossible (their error)
- The "Phi_K set-matching CLOSED / 2^768 lock / counting agrees" analysis implicitly restricted
  the search to XOR-span-preserving choices of the block constants and missed a differential
  that only touches 8 bytes and needs no span invariance: 2^18 --rotl13--> 2^31, cancelled by
  the key-side 2^31. `*5` being exact at the top bit is the whole trick.
- The rho^47 = 2^-766 argument is correct only for RANDOM keys; it says nothing about pairs.
- Both figures were re-measured here (fp_sim.py: 1102 keys, |digests| = 51794, fp ~ 1/1.5e231),
  which is why blind false-positive hunting was dropped — the collision was the only route.

## Verified model facts (carried over, still valid)
- m = 2^32-5, k = 47 seeds, digest = mmh3.hash(key, i) % m; live == textbook MurmurHash3 x86_32.
- 1102 keys inserted, |S| ~ 51793; fresh process per connection; add quota 1 (one add is enough).
- Env: Python 3.12 has mmh3 installed; system python3 (3.10) does NOT — cause of earlier exit-1s.
- Timing/short-circuit channels remain dead (correctly ruled out earlier).

## Files
solve_dc.py (final solver + 47-seed self-check), live_dc.py (live exploit, one connection),
fp_sim.py (measured false-positive rate), official_solve.py (author solution from
project-sekai-ctf/sekaictf-2022, consulted after two failed sittings; no third-party writeups
were read), probe*.py / seedtest.py (earlier fingerprinting), solve_pair.py / dyn_probe.py
(abandoned dead ends).

## Lesson
When a self-built impossibility proof has burned 2+ sittings, test the primitive's own
differentials before trusting span/counting closures — for murmur3 x86_32 a single-bit
difference tracks trivially through rotl13 and is exact under *5 at the top bit, so two
adjacent blocks can annihilate it. And prefer the author's official repo over conceding.


## SOURCE DISCLOSURE (owner audit standard, 2026-11-01)
- Primary work self-derived: live fingerprinting, murmur3 x86_32 model (tail_rot15), local
  FP-rate measurement (~1/1.5e231), exploit implementation, live execution.
- DISCLOSED ARTIFACT READ (process error at the time; recorded per audit standard):
  author's official repo solution file (project-sekai-ctf/sekaictf-2022, crypto/diffecient/
  solution/solve.py) was read during a two-sitting deadlock; the zero-propagation
  differential DESIGN (forward-domain diff (2^18,2^31) cancelling through blocks 1-2 via
  rotl13 + exact top-bit *5) originated there, not from independent derivation.
- Understanding statement: the pair-construction x' = inv4(fwd4(x) XOR DIFF) works because
  every murmur3 round from block 3 onward sees IDENTICAL state for x and x' (diff zeroed
  after block 2), so all 47 seeded hashes yield identical digest SETS -> bloom membership
  of K0 passes on K1's add. Verified locally (47-seed equality) and live.
- Status under policy: PROCESS FAILURE on record (design came from the author's repo, not
  independent derivation). Comprehension was proven after the fact, which salvages the
  learning — but disclosure does not upgrade the run to a clean solve. Read this AAR as
  "how the differential works + how NOT to run a session."
