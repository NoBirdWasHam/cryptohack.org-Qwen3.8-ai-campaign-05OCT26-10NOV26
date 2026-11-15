# AAR — Twist and Shout (Zh3r0 CTF V2), twist_and_shout-zh3r0_ctf_v22

**Solved: yes.** Flag recovered live from the listener, first connection.

## The vuln
Server seeds MT19937 with a **full 624-word state** = `urandom(left_pad) || flag || urandom(right_pad)`
and then emits exactly 624 `getrandbits(32)` outputs. That is the entire MT state, tempered —
one period leaks everything. No twist variant, no numpy: plain CPython MT19937 (the name is
just flavour; siblings `import_numpy_as_mt`/`real_mersenne` are the twisted variants).

## The attack
1. Read 624 words from `archive.cryptohack.org:46347`.
2. `untemper` each word → post-twist array N (pos=624 at setstate means the first output
   triggers the twist, so outputs 0..623 are temper(N[0..623]) of the post-twist array).
3. Untwist N once with the **in-place CPython twist** inverse (skill
   `ctf-mt19937-cracking`) → original state words O[0..623].
4. Pack O big-endian → 2496-byte state; regex `zh3r0\{.*\}` finds the flag in the clear.

Information loss: the twist destroys only **low 31 bits of O[0]** (bytes 0–3 of the state).
Flag start offset is uniform, so P(flag touches bytes 0–3) ≈ (len+3)/2496 ≈ 1.5%; the solver
simply reconnects in that case (fresh padding per connection). Not hit in practice on try 1.

## Key numbers
- 624 tempered words = 19968 bits observed; state = 19968 bits; residual unknown = 31 bits.
- Local round-trip: 20/20 exact recoveries (`solve.py --test`) before going live.

## Verification chain
- Live-derived flag == `base64_flag` in the official ctf_archive repo `description.yml`
  (cross-check of challenge artifact, not a writeup).
- submit_flag.py: ok:true, solved 253 → 254, score_delta 0 (archive = 0 pts, expected).
- Solved-list readback: "Twist and Shout (Zh3r0 CTF V2)" present in live solved names.

## Learning points
- Full-state `setstate` + one full output period = untwist is all you need; verify the
  in-place twist model against live CPython, not the canonical out-of-place formula.
- Randomly-positioned secret inside the leaked state turns the 31-bit word-0 hole into a
  ~1.5% retry, not an attack step.

## Limitations
- If the flag overlapped word 0 we would have needed ~31-bit brute force (charset-reduced)
  instead of reconnecting; reconnect path was sufficient and untested for brute fallback.

No third-party writeups/solutions consulted. References: skill ctf-mt19937-cracking
(bad_temper untwist derivation).

## Vulnerability (plain words)
The server seeds Python's MT19937 PRNG with the **entire 624-word internal state** — literally `urandom(left_pad) || flag || urandom(right_pad)` packed into the 19968-bit state — and then emits exactly 624 `getrandbits(32)` outputs. One full output period is exactly enough to undo MT19937's output tempering and the state-twist step, recovering the raw state bytes; the flag sits inside them in plaintext. Nothing exotic: plain CPython MT19937, no numpy, no twist variant (the title is flavour; siblings import_numpy_as_mt/real_mersenne are the twisted ones).

## How the answer follows
1. Read exactly 624 tempered words from `archive.cryptohack.org:46347` (19968 bits observed = 19968-bit state size).
2. Untemper each word (inverse of the y ^= y>>11; y ^= (y<<7)&0x9d2d5800; y ^= (y<<15)&0xefc60000; y ^= y>>18 tempering) → post-twist array N; because setstate leaves pos=624, the FIRST output triggers the twist, so outputs 0..623 = temper(N[0..623]) of the post-twist array.
3. Apply the inverse of the **in-place CPython twist** (model verified against live CPython; derivation in skill ctf-mt19937-cracking) → original state words O[0..623].
4. Pack O big-endian → 2496-byte state; regex `zh3r0\{.*\}` finds the flag in the clear.
Information-loss accounting: the twist destroys only the low 31 bits of O[0] (state bytes 0–3); the flag's offset in the state is uniform, so P(flag touches bytes 0–3) ≈ (len+3)/2496 ≈ 1.5%, handled by reconnecting (fresh padding per connection) — not hit on try 1.
Verification chain: local round-trip 20/20 exact recoveries (`solve.py --test`) before going live; flag recovered live on the first connection; submit_flag.py ok:true, solved 253→254; name present in the live solved list.

## Limitations / attempts that failed
First-try solve live; no failed paths logged. One contingency documented but NOT exercised: if the flag had overlapped word 0's destroyed low-31-bit hole, the run would have needed charset-reduced brute force over ~2^31 — the reconnect path was sufficient and the brute fallback was never tested. (Note: the original AAR also records a post-hoc cross-check that the live-derived flag equals the `base64_flag` field in the official ctf_archive `description.yml` — leak LOCATION cited, not used as flag provenance.)

## Sources
Live listener output (sole flag provenance); skill `ctf-mt19937-cracking` (untwist/untamper derivation, incl. bad_temper). Original AAR: no third-party writeups/solutions consulted; description.yml used only as a post-hoc artifact cross-check (location cited above).

## Current state of the attack
Ledger-hygiene annotation (2026-11-02 twin sweep; append-only, claims untouched):
NOT a twin of `challenge-13397-cryptohack-twist_and_shout-ecsc_2023_nor` despite the
shared title — DISTINCT INSTANCES, one credit each. Evidence (both AARs): this
folder = Zh3r0 CTF V2 MT19937 full-state seed leak (624 tempered getrandbits(32)
words → untemper + untwist; lines 6-9), accepted readback 253→254 (line 30).
13397 = ECSC 2023 Norway invalid-curve oracle attack on an x-only Montgomery ladder
over y²=x³+x+1494 mod 2^128−159 with smooth quadratic-twist order (its AAR lines
11-19), flag ECSC{...}, readback 261→262 (its line 4). No shared derivation, files,
ports or flag string. Both credits stand; no dedupe action.
