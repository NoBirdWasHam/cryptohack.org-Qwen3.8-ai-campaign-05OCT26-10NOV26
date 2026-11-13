# AAR — a_joke_cipher-hkcert_ctf2021 (A Joke Cipher, HKCERT CTF 2021)

**Flag:** `[flag — recorded in FLAGS/ctf-archive/challenge-318-cryptohack-a_joke_cipher-hkcert_ctf2021/flag.txt]` — accepted (live solved count 251→252; reconcile.py shows it in "LIVE solved", Section B empty).

## The construction (derived from chall.py, no writeups consulted)
NagatyCryptosystem (per the Springer paper cited in a comment):
- `private_key = S_A` = sum of 1024 random 1024-bit ints (~2048 bits), `public_key y_A = S_A mod p`, p 1024-bit.
- `exchange(y_B): S_AB = (y_A·y_B)·y_B·S_A mod p` — Alice's shared key.
- `encrypt(m) = m · S_AB` — **unpadded integer multiplication**, no modulus.

## The break (trivial algebra, first principles)
`S_AB` is reduced **mod p**, and `y_A = S_A mod p`, so exponent-style commutativity collapses the secret:

    S_AB = (y_A · y_B² mod p) · S_A mod p = (y_A · y_B² mod p) · y_A mod p

— computable from public values alone. Then `flag = c // S_AB` (exact integer
division; `c = flag·S_AB` exactly, and the round-trip assert `S_AB·m == c`
passes, which is the verification before submission).

Secondary observation: even without reconstructing `S_AB`, `flag` (~432 bits) is far smaller than `S_AB` (>2^1023 w.h.p.), so `c = m·S_AB` is information-theoretically nearly leaky; the multiplication-only encryption is the second joke.

## Key numbers
p, y_A, y_B, c all 1024-bit (output.txt). Recovered plaintext: 54 printable ASCII bytes.

## Learning points
- Any "shared secret" formula `f(y_A,y_B)·S_A mod p` where f is public and multiplication is commutative is broken when the reduction happens mod p and `S_A` only ever appears mod p — the public key *is* the secret in the ring used.
- Always ask "what modulus is the final secret reduced under?" — matching it against how the private key enters decides the attack.
- Unpadded multiply encryption leaks via size even when the key were secure.

## Limitations
- Break (B) (key-free division bound argument) was sketched but not separately executed as an independent decryption (no candidate S_AB search); the primary algebraic reconstruction + exact round-trip `sk·m == c` was the verified path. No failures to report; solved in <10 tool calls, no alternatives tried and abandoned.

## Files
- `solve.py` (runnable, self-verifying), `chall.py`, `output.txt`, `statement.txt`, `flag_a_joke_cipher-hkcert_ctf2021.txt`, `_card_raw.html`

No third-party writeups or solution pages used. Reference cited in chall.py itself: Khaled A. Nagaty, NNA 2020 (Springer 10.1007/s42452-019-1928-8).

---

<!-- AAR batch #9 quality upgrade (2026-11-02): publication sections appended; everything above this marker byte-identical to the pre-append AAR (hash in aar_batch9_pre.sha). -->

## Vulnerability (plain words)
The "Nagaty cryptosystem" reduces the shared secret modulo p at every step, and the private key `S_A` only ever appears modulo p (`y_A = S_A mod p`). The shared-key formula `S_AB = (y_A*y_B)*y_B*S_A mod p` is therefore public-only arithmetic — the secret cancels out by commutativity of multiplication in the very ring where it lives. On top of that, encryption is a bare unpadded integer multiply `c = m * S_AB`, the second joke.

## How the answer follows
1. Reduce the formula: `S_AB = (y_A * y_B^2 mod p) * S_A mod p = (y_A * y_B^2 mod p) * y_A mod p` — computable from the public `output.txt` alone (p, y_A, y_B, c all 1024-bit).
2. Since `c = flag * S_AB` exactly (no padding, no modulus), `flag = c // S_AB` as exact integer division.
3. Verification before submission: round-trip assert `S_AB * m == c` passes; recovered plaintext is 54 printable ASCII bytes: `[flag — recorded in FLAGS/ctf-archive/challenge-318-cryptohack-a_joke_cipher-hkcert_ctf2021/flag.txt]` (accepted; live solved count 251 -> 252).
4. Independent sanity observation: even without S_AB, flag (~432 bits) << S_AB (> 2^1023 w.h.p.) means the unpadded multiply already leaks the plaintext by size.

## Limitations / attempts that failed
- The key-free size/interval attack (break B above) was sketched but not separately executed as an independent decryption; the algebraic reconstruction + exact round-trip was the verified path. No failures occurred (solved in < 10 tool calls, no alternatives tried and abandoned).

## Sources
- Derived from the provided `chall.py` and `output.txt`; no writeups or solution pages consulted. The scheme paper named *inside chall.py* is Khaled A. Nagaty, Neural Computing & Applications 2020 (Springer 10.1007/s42452-019-1928-8) — cited for provenance of the construction, not used as a solve source.
- Upgrade-time comprehension check (batch #9, 2026-11-02): re-derived the S_AB collapse and the exact-division step offline from `chall.py`/`solve.py`; no new submission, flag untouched.
