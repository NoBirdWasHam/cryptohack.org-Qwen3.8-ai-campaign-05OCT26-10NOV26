# AAR — 1n_jection (Zh3r0 CTF V2), CryptoHack archive slug 1n_jection-zh3r0_ctf_v22021

**Solved: yes.** Flag: `zh3r0{wh0_th0ugh7_b1j3c710n5_fr0m_n^k_t0_n_c0uld_b3_s00000_c0000000l!}`

## What the challenge actually was
Despite the "injection" name (vaccine joke per the statement), there is no service and no
injection: `challenge.py` just prints `nk2n(flag)` for a hidden flag and a printed constant.
`nk2n` packs an integer list into one integer via a **binary tree of Cantor pairings**:
- `l==1` → element; `l==2` → `π(i,j) = ((i+j)(i+j+1))/2 + j`;
- else split into `ceil(l/2)` / `floor(l/2)` halves, recurse, pair the two results.

## Attack
Pure inversion — no oracle, no lattice:
1. Cantor unpairing: `w = (isqrt(8z+1)-1)//2`, `j = z - w(w+1)/2`, `i = w-j`.
2. Tree shape depends only on the flag length `L` (halving rule is deterministic), so
   unroll the pairing tree for each candidate `L` and test that every leaf lands in
   printable ASCII. `L=70` is the unique fully-printable decode.
3. Flag format was `zh3r0{...}`, not `crypto{...}` — first pass filtering on the
   `crypto{` prefix found nothing; loosening to "all printable + braces" hit immediately.

Verified `rec(nk2n(msg),L)==msg` round-trip for all L in 1..129 with random bytes before
trusting the inversion.

## Key numbers
- N = 247-digit integer (comment in challenge.py); flag length 70 bytes.

## Submission
- `submit_flag.py 1n_jection-zh3r0_ctf_v22021` → ok:true, HTTP 200; solved 248→249;
  score_delta 0 as expected for a 0-pt archive entry; credit = solved-list growth.

## Learning points
- Card name ≠ challenge type; read the provided source before designing an attack.
- Cantor pairing is invertible in integers (floor-sqrt trick); a pairing tree only needs
  the top-level length to fix its shape — brute-force length, verify charset.
- CTF flag prefix varies by source CTF (Zh3r0 archive → `zh3r0{`); don't hard-code `crypto{`.

## Limitations
- None material. Length brute force was capped at 200 (flag was 70); uniqueness of the
  printable decode was observed (single hit) but not proven.

No third-party writeups consulted. Reference for Cantor inversion: standard textbook
pairing-function inverse (e.g. HPS-adjacent set theory), no external tooling used.
