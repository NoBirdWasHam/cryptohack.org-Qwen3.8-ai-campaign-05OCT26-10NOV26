# Site — Challenge 144: PriMeD5

- **Platform:** CryptoHack (socket service)
- **Category:** hashes / **100 pts** / slug `primed5` (folder `challenge-144-cryptohack-primed5`)
- **Service:** `socket.cryptohack.org:13392` (provided source `13392_provided.py`)
- **Status:** SOLVED + API-VERIFIED 2026-10-20 — `[flag — recorded in FLAGS/hashes/challenge-144-cryptohack-primed5/flag.txt]` (+100, 186→187)

## Server (from provided source)
RSA `pkcs1_15` over **MD5**. `sign`: only signs `isPrime(p)`, returns sig over `MD5(long_to_bytes(p))`.
`check`: verifies the signature on `MD5(long_to_bytes(p))` for ANY p (no primality re-check!), then
leaks `FLAG[:gcd(a,p)]`. `len(FLAG)=24`.

## Attack
MD5 collision pair (M1,M2) from md5fastcoll with: `p=int(M1)` prime (≤1024 bits), `p'=int(M2)`
having a divisor `a ≥ 24`. Sign p → verify with (p', sig, a): digest matches (collision), gcd(a,p')=a
⇒ `FLAG[:a]` = whole flag. Driver `search.py` (4 workers) + `exploit.py`.
