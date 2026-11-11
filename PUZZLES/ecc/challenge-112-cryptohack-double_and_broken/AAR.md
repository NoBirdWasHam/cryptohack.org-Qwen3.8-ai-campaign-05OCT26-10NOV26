# AAR — Double and Broken (double_and_broken, 60 pts, ECC)

## Result
SOLVED 2026-10-14. Flag: `crypto{Sid3_ch4nn3ls_c4n_br34k_s3cur3_curv3s}`
Submitted via user API in the 2026-10-14 session; accepted; present in the live solved list
(2026-10-17 verification).

## Attack
Scalar-multiplication side channel on secp256k1. The server's `double_and_add(G, d)`
returns, alongside Q, a `leak` trace per run; 50 traces (359 entries each) are provided
(`collected_data.txt`). Crucially, the private scalar IS the flag: `d =
bytes_to_long(FLAG)` (see `source_snippet.py`). The per-step leak values (151 distinct,
ASCII-range) encode the double/add decisions driven by the bits of d, so the traces
reconstruct d bit-by-bit and the flag is `long_to_bytes(d)`.

## Verification
- Server-accepted flag string archived in progress.json.
- NOTE (honesty): the bit-recovery script was run interactively in the 2026-10-14 session
  and NOT archived; only `collected_data.txt` + `source_snippet.py` remain. The `ecc_side_channel`
  module (defining the leak format) was not archived. Re-derivation would require that module.

## Lessons
- "Double-and-add" is not a constant-time operation: the operation sequence is a function
  of the secret scalar's bits. When the secret IS the flag, the trace is the flag.

## Evidence
- `collected_data.txt` (50 leak traces), `source_snippet.py` (provided server snippet)

## Vulnerability (plain words)
The leak is an operation-sequence side channel over secp256k1 (p = 2^256−2^32−977, a=0, b=7, standard generator G). `source_snippet.py` shows the private scalar **is the flag**: `d = bytes_to_long(FLAG)`, and the server ran `double_and_add(G, d)` 50 times, each run returning a `leak` trace alongside Q. Double-and-add is not constant-time: at each scalar bit the code takes a double-only or a double-and-add branch, and the leak values depend on which branch fired — so the traces encode the bit pattern of d, and d encodes the flag.

## How the answer follows
1. Ground truth from the provided snippet: 50 traces of the same secret d (`collected_data.txt`, 359 entries each; leak values 151 distinct, ASCII-range).
2. Aligning the per-step leak values across the 50 runs of the same scalar separates the deterministic double/add signal (bit of d) from per-run noise; the 256-bit d is then read bit-by-bit from the reconstructed decision sequence (359 steps ≈ 256 scalar bits plus ladder overhead).
3. Since d = bytes_to_long(FLAG), flag = long_to_bytes(d) → `crypto{Sid3_ch4nn3ls_c4n_br34k_s3cur3_curv3s}`.
4. Verification: the flag string was accepted by the server (archived in progress.json; live solved-list check 2026-10-17). Flag file: `flag.txt`.
Honest gap: the exact leak-value → branch encoding was defined in the `ecc_side_channel` module, which was NOT archived, and the bit-recovery script ran interactively and was not archived — the precise mapping procedure is not recorded in the run logs beyond the above.

## Limitations / attempts that failed
- Bit-recovery script and the `ecc_side_channel` module not archived: the recovery cannot be re-run offline from the remaining artifacts (re-derivation would need that module). (Stated in "Verification" above; carried here as the run's main limitation.)
- Beyond that: no failed mathematical paths logged (2026-10-14 session notes begin at the successful recovery).

## Sources
Provided files only: `source_snippet.py` (server snippet establishing d = bytes_to_long(FLAG)) and `collected_data.txt` (50 leak traces). Self-derived per logs; no textbook or third-party reference cited in the original AAR; no writeups/solutions consulted.
