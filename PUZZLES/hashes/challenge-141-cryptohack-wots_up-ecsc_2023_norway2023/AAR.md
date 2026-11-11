# AAR — WOTS Up (wots_up-ecsc_2023_norway2023, 75 pts, Hashes)

## Result
SOLVED 2026-10-16. Flag: `ECSC{h4sh1n6_ch41n_r34ct1on_ff_}`
Submitted via user API (submit_flag.py) during the hashes-list session; accepted (present in the live solved list; synced into progress.json on 2026-10-17 verification).

## Attack
WOTS-256 (SHA-256) signature forgery via a **seeded private-key chain**. In `__init__`
(`chal_provided.py`), the 32 private-key chain starts are successive hashes of ONE seed:
`priv[i] = H^(i+1)(seed)`. So every element `sig1[i] = H^(255-b1[i])(priv[i])` of the given
signature sits at chain position `p1[i] = 256 + i - b1[i]` on a SINGLE chain from the seed,
where `b1 = SHA-256("WOTS Up???")`. Any chain element at position >= min(p1) is reachable by
plain forward hashing from the known sig1 elements. The target message "Sign for flag" has
bytes `b2`; the provided data satisfies `b2[i] <= B_i` at all 32 positions (B_i from the
known elements), so the whole target signature is forged by forward hashing only — no
collision search. The AES-CBC key for the vault is built from the first byte of each forged
signature element (per chal.py), decrypting the flag.

## Verification
- `solve.py` runs end-to-end from the provided `data_provided.json`: forges signature2,
  derives the AES key, decrypts the flag.
- Server-accepted flag string archived in `flag.txt`.

## Lessons
- WOTS keys are only as safe as their chain starts: if the starts are derived from one seed,
  one signature exposes the whole key schedule.
- "Safe to sign" vs "flag" messages: check whether the needed chain positions are ahead of
  known positions BEFORE assuming a collision search is needed.

## Evidence
- `chal_provided.py`, `data_provided.json` (provided)
- `solve.py` (solver, docstring documents the attack), `flag.txt`

## Vulnerability (plain words)
WOTS chains only stay private if the 32 chain starts are independent random values. Here `__init__` derives them as successive hashes of ONE seed: priv[i] = H^(i+1)(seed). One signature then exposes points that all sit on hash-paths traceable forward from that single seed-structure — the whole key schedule collapses to information already handed over.

## How the answer follows
1. Each given signature element sig1[i] = H^(255−b1[i])(priv[i]) sits at chain position p1[i] = 256 + i − b1[i] from the seed (b1 = SHA-256("WOTS Up???")).
2. Every chain element at position ≥ min(p1) is reachable by forward hashing only — no inversion, no collision search.
3. The provided data satisfies b2[i] ≤ B_i at all 32 positions (b2 = SHA-256("Sign for flag")), so the target signature is fully forged by forward hashing.
4. AES-CBC key = first byte of each forged element (per chal.py) ⇒ decrypt vault ⇒ `ECSC{h4sh1n6_ch41n_r34ct1on_ff_}`; accepted, present in live solved list.

## Limitations / attempts that failed
- Single-shot solve; no failed attempts recorded in run logs. The forward-reachability check b2 ≤ B held everywhere on the provided data — the harder "some positions behind" case (needing collision search) never occurred and was never implemented.

## Sources
Provided files only: `chal_provided.py`, `data_provided.json`. Self-derived from provided code; no writeups/solutions consulted; no external reference cited in run logs.
