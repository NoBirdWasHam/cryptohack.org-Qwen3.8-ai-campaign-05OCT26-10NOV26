# AAR — CryptoHack Megalomaniac 2 (challenge-165, socket 13409)

**Flag:** `crypto{W4s_th4t_rea11y_Any_hard3r??}` (submitted, +120, solved 226)

## The vuln
The login oracle (`send_challenge`) AES-ECB-decrypts an attacker-chosen `share_key_enc`
under Alice's real master key, parses the result as an RSA CRT key blob `(p,q,d,u)`, and
RSA-CRT-decrypts an attacker-chosen `SID_enc` with it — returning the plaintext **minus
its low 16 bytes**. Only 4 logins, so mega1's padding oracle (~1025 queries) is dead.

## The attack (1 login, ~3.5s live)
1. `SID_enc = M^e mod n` with `M = 2^1024+12345`, so the *correct* CRT output is exactly `M`.
2. Fault: XOR one byte of **ciphertext block 39** (bytes 624–639). AES-ECB decryption
   scrambles the whole plaintext block 39 — which lies entirely inside the `u` field, so
   the length prefixes and the padding block stay valid. The server parses `u' = u + δ`
   (δ unknown, |δ| < 2^192) with genuine `p,q,d`.
3. Since `m = M` and `m' = h'·p + mp`, the faulted output is **`m' = M + v·p` exactly**
   (`v = h'−h`, |v| < q — no `w·n` term; the mod-q reduction is absorbed in v).
4. Server returns `m_top = m' >> 128`, so `Yc = m_top·2^128 − M ≡ −m_low (mod p)` with
   `m_low < 2^128`: a near-multiple of p. **Coppersmith** (root of `x + Yc mod p | N`,
   X = 2^130, m = 6, dim-12 lattice, fpylll LLL + `sympy.factor` over ZZ to pull the
   linear factor out of the short polynomial) gives `r = m_low`, then
   `p = gcd(N, Yc + r)`.
5. `get_encrypted_flag` (free action, no step check) → AES-ECB key
   `SHA256(l2b(p) ‖ l2b(q))` → flag.

## Key numbers
- Blob: p(2+128) q(2+128) d(2+256) u(2+128) + pad = 656 B = 41 AES blocks; blocks 33–39
  are interior to u; block 40 holds the padding.
- Coppersmith: β = 1/2, d = 1, X = 2^130 > N^{β²/(2·1)} margin fine at m = 6 (0.7s/run).

## Learning points
- AES-ECB **decryption** of a tampered ciphertext block scrambles the *entire* plaintext
  block (bit-flip control exists only in the encryption direction). Fault granularity is
  one 16-byte block; pick a block whose field can absorb arbitrary garbage (u).
- A CRT fault on u perturbs the output by an exact multiple of p — truncation of the low
  128 bits then yields a Coppersmith instance `Y ≡ j·p − r`, r small. The unknown
  multiplier j makes enumeration pointless; the lattice handles it.
- `sympy.factor(P.as_expr(), domain=ZZ)` extracts the linear factor `(x−r)` from the
  short lattice polynomial; `nroots`/`gcd` routes fail on 5000-bit coefficients.

## Limitations
- First model (from earlier session) assumed a single-byte XOR on u's low byte and
  `m = M + f·p²·d − w·n` with enumeration over (f,d,w): **wrong** — ECB block scrambling
  breaks padding (verified: byte 645 tamper → error; dbg10/dbg11), and the w-term model
  was a mis-derivation. The correct relation `m' = M + v·p` needs no enumeration.
- If `d` were 255 bytes the layout shifts by one byte and block 39 would clip u's
  length prefix; solver retries offsets 630/624 on a new connection (not needed live).

## Files
- `solve_mega2_v2.py` (live solver), `cop3.py` (Coppersmith factor), `test_offline_v2.py`
  (2/2 offline vs local 13409.py via `harness.py`), `flag_mega2.txt`, dbg*/offline_mega2*
  (failed-model archaeology).
## Vulnerability (plain words)
The login oracle AES-ECB-decrypts an ATTACKER-CHOSEN blob under Alice's real master key and parses the result as an RSA CRT key `(p,q,d,u)` with integrity checks only on lengths and padding — never on the key's authenticity. Because ECB decryption of a tampered ciphertext block randomizes that entire plaintext block, one ciphertext-byte flip becomes a one-block fault injector into a chosen field of the private key. A faulted RSA-CRT computation leaks a multiple of p (classic Boneh-DeMillo-Lipton fault factoring); factoring N collapses the whole scheme. 4-login budget kills the padding-oracle route, so the fault path is the only door.

## How the answer follows
1. Fix the honest outcome so deviations are pure signal: `SID_enc = M^e mod n` with `M = 2^1024+12345` — the correct CRT output is exactly M, known to the attacker.
2. Fault inside `u`: XOR a byte of ciphertext block 39 — a block lying entirely within the 128-byte u field, so length prefixes and the padding block survive parsing while u is replaced by `u' = u + d` (unknown d, |d| < 2^192). Genuine p,q,d still used by the server.
3. Faulted CRT: since the residue mod p is untouched, the output is EXACTLY `m' = M + v*p` (`v = h'-h`, |v| < q; the mod-q reduction folds into v — no w*n term needed).
4. The oracle returns `m'` minus its low 128 bits, so `Yc = m_top*2^128 - M = -m_low (mod p)` — a near-multiple of p with an unknown huge multiplier v. Enumeration over v is hopeless; Coppersmith handles unknown-multiplier near-multiples: small root of `x + Yc mod p | N`, X = 2^130 > N^(beta^2/d) margin at m=6 (dim-12 lattice, fpylll LLL), then `p = gcd(N, Yc + r)`.
5. `get_encrypted_flag` is an unchecked free action; flag decrypts under AES-ECB key `SHA256(l2b(p) || l2b(q))` -> `crypto{W4s_th4t_rea11y_Any_hard3r??}` accepted, +120.

## Limitations / attempts that failed
(Original record retained above; restated for the manifest.)
- First model was WRONG: single-byte XOR on u's low byte plus `m = M + f*p^2*d - w*n` with enumeration over (f,d,w). Dead on two counts: ECB block scrambling breaks the padding block for low-byte tampers (verified live: byte-645 tamper -> error; dbg10/dbg11), and the w-term model was a mis-derivation once scrambling (not bit-flipping) is the fault granularity. The correct `m' = M + v*p` needs no enumeration.
- Layout fragility: if d were 255 bytes the blob shifts one byte and block 39 would clip u's length prefix; solver retries offsets 630/624 on a fresh connection (not needed live).
- Validation was offline (2/2 vs the local 13409.py server harness) before the single live login; no failed live submission recorded.

## Sources
- Public mathematics literature (about the MATH, per source-disclosure rules): Boneh-DeMillo-Lipton CRT fault attack; Coppersmith's small-roots method (as implemented per standard lattices references); HPS textbook available locally for Coppersmith background.
- `sympy.factor(domain=ZZ)` linear-factor extraction — library/tooling docs, not a challenge solution.
- No third-party writeup or solution artifact for this challenge consulted.
