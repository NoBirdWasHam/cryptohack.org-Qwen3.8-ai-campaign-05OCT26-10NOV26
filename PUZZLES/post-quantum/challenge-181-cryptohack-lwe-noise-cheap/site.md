# Noise Cheap (`lwe-noise-cheap`)

- **Points:** 90
- **Category:** post-quantum
- **Status:** SOLVED (submitted 2026-10-14 via submit_flag.py, live-verified: score 6915 -> 7005)
- **Solved:** 2026-10-14
- **URL:** https://cryptohack.org/challenges/post-quantum/lwe-noise-cheap/
- **Flag:** `crypto{LLL_is_also_very_useful!}`

## Statement
--> A core part of making LWE secure is having the noise terms be larger than what lattice reduction algorithms can handle. Connect at socket.cryptohack.org 13413. Challenge files: 13413.py (cached in `_pq/13413.py`).

## Server structure (13413.py)
- `n=64`, `p=257` (plaintext modulus), `q=1048583` (= 2^20+7, prime), `S = V.random_element()` over GF(q)^n (module-level: **shared across connections**).
- `encrypt(m)`: `A` random in GF(q)^n; `e = randint(-1,1)` **per sample (scalar!)**; `b = A*S + m + p*e` (mod q), b a scalar.
- Options: `encrypt` with a message in [0,p); `get_flag` with an index. FLAG is 32 chars (indices 0..31): `crypto{` + 24 secret + `}`.
