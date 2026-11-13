# AAR — CryptoHack Megalomaniac 3 (challenge-166, socket 13410)

**Flag:** `[flag value withheld — real-flag strings live only under FLAGS/]`
(submitted, +120, solved 229)

## The vuln
Same login oracle as mega1/2, but: unlimited logins, the server **hands out `(n, e, p)`**
("recovered share_key"), and the flag lives in a file encrypted with a random `node_key`
whose only protected form is `node_key_enc = AES_master(node_key)`. Knowing p gives the
full RSA key (q = n/p, d = e⁻¹ mod λ, u = p⁻¹ mod q — PyCryptodome conventions), so the
RSA side is free; the wall is the unknown AES master key.

## The attack (1 query, ~1.3s live)
Every block of the private-key blob is now **known plaintext** under AES_master — except
`X = D_master(node_key_enc)`. Submit `share_key_enc` = legit blob ciphertext with
**ciphertext block 39 replaced by `node_key_enc`** (block 39 is interior to the `u`
field; length prefixes and padding block untouched → parse + unpad succeed).
The server decrypts block 39 to X and runs CRT with genuine `p,q,d` but
`u_g = u + (X − orig)·2^64` (orig = known u-bytes 104–119).

With `SID_enc = M^e mod n` (M = 2^1024+12345): `mp = M mod p`, `mq = M mod q`,
`t = (mq−mp) mod q` are all computable, and the returned `SID = (h·p + mp) >> 128` with
`h = t·u_g mod q`. Since `h·p = m_top·2^128 + m_low − mp` and `2^128 < p`, h is pinned to
≤ 2 candidates; for each, `u_g = h·t⁻¹ mod q` (± k·q resolved by the constraint
`(u_g − u) ≡ 0 mod 2^64`, |u_g−u| < 2^192) → `X = orig + (u_g−u)/2^64` = **node_key**.
Then `file_enc` → AES-ECB(node_key) → unpad → flag.

## Key numbers
- u-field bit-shift for block 39: 2^64 (u ends at blob byte 648, block ends at 640).
- Candidate h set: {⌊(m_top·2^128 − mp)/p⌋, +1} — interval width 2^128/p < 1.

## Learning points
- When part of the key is leaked, the "hard" secret moves to the next layer (here the
  AES master key); the parse-tolerant CRT oracle then acts as a **leak channel**: put the
  unknown ciphertext block into a field whose corruption keeps the parse valid, and
  invert the algebra.
- PyCryptodome conventions matter: `RSA.u = inv(p, q)` (not inv(q,p)) and
  `d = inv(e, lcm(p−1,q−1))` — wrong conventions silently produce a mismatched blob
  (first offline run failed exactly this way).
- Truncation of 16 low bytes still leaves enough precision because p ≫ 2^128.

## Limitations
- Relies on `t ≠ 0 mod q` (holds w.h.p.) and d being 256 bytes (assert catches shifts;
  retry gets a fresh instance).
- Did not attempt the generic padding-oracle route (unnecessary once p is given).

## Files
- `solve_mega3.py` (live solver), `test_offline_mega3.py` (2/2 offline vs local 13410.py),
  `flag_mega3.txt`, `13410.py`, `dbg20.py` (convention debug).
## Vulnerability (plain words)
Same parse-tolerant login oracle as mega2 — but here the server GIVES AWAY p, so the RSA layer is free (q = n/p, d = e^-1 mod lambda, u = p^-1 mod q). The real secret moves up a layer: the flag file is under `node_key_enc = AES_master(node_key)` and the master key is unknown. The vulnerability is that the oracle, once parsing succeeds, will decrypt ANY ciphertext block you place into a field whose corruption keeps the parse valid — turning it into an unintended single-block AES-DECRYPTION ORACLE for the unknown blob. Missing integrity (not just missing confidentiality) on the key blob is what the flag text mocks.

## How the answer follows
1. Known-plaintext shift: with p handed out, every field of the private-key blob is known plaintext under AES_master EXCEPT `X = D_master(node_key_enc)`.
2. Swap-in: submit the legit blob ciphertext with ciphertext block 39 REPLACED by `node_key_enc`. Block 39 is interior to u (2^64 bit-shift), and the parse (lengths + padding block) still succeeds, so the server CRTs with genuine p,q,d but `u_g = u + (X - orig)*2^64` (orig = the known u-bytes 104-119).
3. Invert the CRT algebra: with `SID_enc = M^e mod n` (M = 2^1024+12345) all intermediates mp = M mod p, mq = M mod q, t = (mq-mp) mod q are computable; the returned `SID = (h*p + mp) >> 128` with `h = t*u_g mod q`. Because p >> 2^128, h is pinned to at most 2 candidates; each gives `u_g = h*t^-1 mod q`, and the alignment constraint `(u_g - u) = 0 mod 2^64` with |u_g-u| < 2^192 resolves the k*q ambiguity. Then `X = orig + (u_g-u)/2^64` — X is the node_key.
4. AES-ECB(node_key) on the flag file, unpad -> `[flag value withheld — real-flag strings live only under FLAGS/]` accepted, +120. One query, ~1.3s.

## Limitations / attempts that failed
(Original record retained above; restated.)
- PyCryptodome convention bug cost the first offline run: `RSA.u = inv(p,q)` (not inv(q,p)) and `d = inv(e, lcm(p-1,q-1))`; a wrong convention silently produces a mismatched blob (dbg20.py is the archaeology).
- Correctness depends on `t != 0 mod q` (fails w.p. ~2^-1024) and on d being exactly 256 bytes — the solver asserts the layout and retries a fresh instance on a shift.
- Generic padding-oracle route deliberately NOT attempted (obsolete once p is given). 2/2 offline validation vs local 13410.py before live; no failed live submission recorded.

## Sources
- PyCryptodome documentation (library conventions for rsa.u / lcm-based d) — tool reference, allowed.
- Conceptual lineage (public math): Bellcore-style CRT fault attacks; ECB block-swapping as a decryption oracle — standard textbook material, not challenge writeups.
- No third-party writeup or solution artifact for this challenge consulted.
