# AAR — Beatboxer (beatboxer, 150 pts, ECC course / AES)

## Result
SOLVED 2026-10-06 (first solve session, course track).
Flag: NOT archived (solved before the flag-archiving convention; the challenge is in the
live solved list as of the 2026-10-17 verification).

## Attack
AES-128-ECB with an AFFINE S-box `sbox[x] = 42*x^42 (mod 256)`, so the whole cipher is an
affine transform in the plaintext: `E_key(P) = M.P ^ E_key(0)`. The column matrix M (M and
Minv in `M_matrix.json`) is key-INDEPENDENT — each column is `E_key(e_j)` with e_j a unit
vector, and linearity of the affine sbox makes M independent of the key. With the ONE
allowed `encrypt_message` of a chosen 16-byte plaintext P_m: `D = E_key(0) = C_m ^ M.P_m`.
Then each flag block decrypts as `P_i = Minv.(C_i ^ D)`; strip PKCS7. One socket
connection: encrypt_flag -> C_flag; encrypt_message P_m -> D; invert all blocks.

## Verification
- `solve.py` (archived) runs the single-connection attack; `verify_affine.py` /
  `keyindep.py` / `find_M.py` are the derivation of M and the key-independence checks.
- Flag not archived (see Result).

## Evidence
- `13406_provided.py` (provided server), `M_matrix.json`, `solve.py`, `verify_affine.py`,
  `keyindep.py`, `find_M.py`, `run_log.txt`

## Vulnerability (plain words)

The S-box is `sbox[x] = 42*x^42 (mod 256)`, an AFFINE map over the XOR structure of the byte
(`s(x XOR y) = s(x) XOR s(y) XOR s(0)`). With every round affine in the block, the entire cipher
collapses to a single affine map over GF(2)^128: `E_K(P) = M.P XOR E_K(0)` with M a 128x128
GF(2) matrix. Linearity of the affine S-box makes M key-INDEPENDENT -- its columns are the images
of unit vectors, derived offline from the S-box definition and checked in `keyindep.py` /
`verify_affine.py` (`M_matrix.json` holds M and M^-1). Only the constant `D = E_K(0)` depends on
the key, and ONE chosen-plaintext query gives it: encrypt a known `P_m`, then
`D = C_m XOR M.P_m`. From there decryption is `P_i = M^-1.(C_i XOR D)`.

## How the answer follows

One socket connection: `encrypt_flag` -> `C_flag`; `encrypt_message` of the chosen `P_m` ->
`C_m`; compute `D = C_m XOR M.P_m`; each flag block decrypts as `P_i = M^-1.(C_i XOR D)`; strip
PKCS#7 (`solve.py`, archived). The flag bytes are NOT archived -- this was solved before the
flag-archiving convention; the SOLVED status stands on the live solved list, verified
2026-10-17 (AAR "Result"/"Verification"), and is not restated here as a value.

## Limitations / attempts that failed

- `flag.txt` missing by the AAR's own record (pre-convention solve); the flag value is not
  recorded in run logs either, so it is deliberately NOT written here.
- Diagnostic scripts (`diag.py`-`diag3.py`, `debugM.py`, `find_M.py`) show iteration on deriving
  and verifying M, but no failure narrative is recorded in run logs.
- Upgrade unit did not re-run the live service (offline editor); mechanism restated from the
  archived scripts and run_log.

## Sources

- Provided server source `13406_provided.py`; statement `site.md`; derivation artifacts
  `M_matrix.json`, `solve.py`, `verify_affine.py`, `keyindep.py`, `find_M.py`; `run_log.txt`.
- Self-derived per logs; no external writeups in evidence.
