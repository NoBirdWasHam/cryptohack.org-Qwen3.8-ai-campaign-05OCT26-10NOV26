# AAR — mixed_up (CryptoHack, hashes, 120 pts) — SOLVED

## RECONSTRUCTED AAR (post-hoc)
Reconstructed 2026-11-01 from surviving artifacts in this folder (solve.py, test_local.py, live_run.log, local_test.log, 13402.py, flag_mixed_up.txt) and the ledger (progress.json nn146, status solved, date 2026-10-21, notes "| API-verified"). This challenge predates the AAR-discipline rule; the HOW below is restated from the solver's own docstring and run logs, not from any external writeup.

## Flag
`[flag — recorded in FLAGS/hashes/challenge-12-cryptohack-mixed_up/flag.txt]` — provenance: printed by our live solve run against socket.cryptohack.org:13402 (live_run.log line 31) and stored in flag_mixed_up.txt; identical to the ledger flag field.

## Problem
Listener at socket.cryptohack.org 13402 (downloaded artifact 13402.py). Given `data` (hex, padded with urandom to flag length), the server computed per solve.py's recorded model: `mixed_and[j] = FLAG[j] & data[j]` (indices), `mixed_xor = (FLAG ^ data) ^ urandom` (values), `very_mixed[j] = mixed_xor[mixed_and[j] % L]`, and returned only `sha256(very_mixed)`. The random XOR makes direct recovery look impossible.

## Vulnerability / Attack
Recorded in solve.py's own docstring and confirmed by the mock server in test_local.py:
- The **AND** branch leaks FLAG bits *as indices*: if `data[j] = 2^b`, then `mixed_and[j] = FLAG[j] & 2^b` is either 0 or `2^b` — the index into the value pool reveals bit b of FLAG[j].
- **Length recovery:** send `data = 00*96` → all indices 0 → very_mixed = one random byte c repeated L times. Brute force all (c, m≤96) against the returned hash → L = 39, "probe byte c=235" (live_run.log line 1).
- **Bit recovery:** for each bit b (0..6) and each of 4 position-groups, send `data[j]=2^b` on the group, 0 elsewhere. Then very_mixed is byte x0 at positions where FLAG bit b is 0 and x1 where it is 1 (x0, x1 unknown random pool bytes). Brute force (x0, x1, subset) = ~2^(16+k) SHA-256 hashes (k = group size ≤ 10, Gray-code enumeration in `_brute`), unique match → 10-bit mask of the group's bit. 7 bits × 4 groups = 28 probes, each 2–4.5 s (live_run.log lines 2–29), 8-worker process pool.
- Assembled prefix/suffix verification passed (live_run.log line 30).

## Validation (before touching the real instance)
test_local.py mocks the exact server logic (AND / double-XOR-with-urandom / index-shuffle / SHA-256) with a known test flag; local_test.log ends `FLAG: crypto{test_flag_local_1234567890abcdefgh}` + `MATCH`.

## Learning points
- A hash over a *structured, low-entropy preimage* is a brute-force oracle, not a shield: the preimage space here was 256² × subsets, not 2²⁵⁶.
- AND leaks information through *indices/positions* while XOR leaks through *values*; randomizing one channel does not silence the other.

## Limitations / honest notes
- Original session transcript does not exist; reconstruction is from the solver script + its own logs only. The uniqueness argument for the (x0, x1, subset) brute force is asserted in solve.py's docstring ("unique match reveals the bits"); we did not re-derive uniqueness here.
- ledger notes carry no method text ("| API-verified"); dates: folder artifacts span Oct 12 (statement fetch) → Oct 22 (live run logs), ledger date 2026-10-21.

## Source disclosure
No third-party writeup consulted (reconstruction from our own artifacts only). No external math reference used.

## Files
solve.py (live attack), test_local.py + local_test.log (mock validation), live_run.log (live run incl. flag), 13402.py (challenge artifact), flag_mixed_up.txt.
