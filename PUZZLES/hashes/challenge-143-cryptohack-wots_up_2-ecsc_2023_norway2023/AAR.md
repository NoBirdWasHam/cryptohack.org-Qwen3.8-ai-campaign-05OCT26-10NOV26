# AAR — WOTS Up 2 (wots_up_2-ecsc_2023_norway2023, 90 pts, Hashes)

## Result
SOLVED 2026-10-16. Flag: `[flag — recorded in FLAGS/hashes/challenge-143-cryptohack-wots_up_2-ecsc_2023_norway2023/flag.txt]`
Submitted via user API (submit_flag.py) during the hashes-list session; accepted (present in
the live solved list; synced into progress.json on 2026-10-17 verification).

## Attack
WOTS-256 forgery from **20 past transaction signatures** of the same key (the "fix" made the
32 chain starts independent, but the safe now holds 20 signatures). For chain position i
(byte i of the SHA-256 of each signed message), signature j gives the chain point
`H^(255-b_j[i])(priv[i])` on the 256-link chain toward `pub[i]`. Let `B_i = max_j b_j[i]`;
the closest known point to the private key is at exponent `e_i = 255 - B_i`. Any needed
point with `b2[i] <= B_i` is reached by forward hashing only. With the provided data,
`b2[i] <= B_i` for all 32 positions, so the target signature ("pub[0] sent 999999 WOTScoins
to me") is forged by forward hashing. The AES-CBC key comes from the first byte of each
forged element (per chal.py).

## Verification
- `solve.py` runs end-to-end from `data_provided.json`: forges the target signature and
  decrypts the flag.
- Server-accepted flag string archived in `flag.txt`.

## Lessons
- Multiple signatures of the same WOTS key are NOT safe to store: the max-hash-byte per
  position can expose every chain start. One signature is already dangerous (WOTS Up);
  twenty make forgery trivial when the target hash bytes stay below the observed maxima.

## Evidence
- `chal_provided.py`, `data_provided.json` (provided)
- `solve.py` (solver, docstring documents the attack), `flag.txt`

## Vulnerability (plain words)
The "fix" from WOTS Up made the 32 chain starts independent — but the safe now leaks 20 past signatures under the same key. WOTS keys are one-time: with 20 signatures per chain position, the signature that hashed the LARGEST byte sits closest to the private key, and if that closest point still lies ahead of where the target message needs to be, forgery needs only forward hashing.

## How the answer follows
1. For chain i, signature j exposes H^(255−b_j[i])(priv[i]); set B_i = max_j b_j[i] ⇒ the closest-to-priv known point is at exponent e_i = 255 − B_i.
2. Provided data satisfies b2[i] ≤ B_i for all 32 positions of the target hash ("pub[0] sent 999999 WOTScoins to me") ⇒ forge every target element by forward hashing only.
3. AES-CBC key = first byte of each forged element (per chal.py) ⇒ decrypt ⇒ `[flag — recorded in FLAGS/hashes/challenge-143-cryptohack-wots_up_2-ecsc_2023_norway2023/flag.txt]`; accepted, present in live solved list.

## Limitations / attempts that failed
- Single-shot solve; no failed attempts recorded in run logs. The b2 ≤ B coverage held on the provided data; the partial-backwards case was never needed.

## Sources
Provided files only: `chal_provided.py`, `data_provided.json`. Self-derived; no writeups/solutions consulted; no external reference cited in run logs.
