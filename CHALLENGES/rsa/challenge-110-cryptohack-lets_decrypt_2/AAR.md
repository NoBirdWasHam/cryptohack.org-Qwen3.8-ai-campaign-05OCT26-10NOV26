# AAR — 110-cryptohack-lets_decrypt_2: Let's Decrypt Again (CryptoHack, 175 pts)

**Result:** SOLVED (2026-10-23, account NoBirdWasHam, score_delta +175, ok:true)
**Flag:** `crypto{let's_decrypt_w4s_t0o_ez_do_1t_ag41n}`

## Source
- Server source provided: `13394.py` (this folder). NOT consulted: /solutions/, writeups (no-cheat rule).

## The vulnerability
The server verifies `pow(SIGNATURE, e, n) == PKCS1v15-digest(msg)` with **attacker-chosen
`n` (set_pubkey, before the random suffix is generated) and attacker-chosen `e` (per
claim, AFTER the suffix is revealed)**. The check is exact integer equality, so the
attacker just needs `SIGNATURE^e mod n` to land on a digest of their choosing. The
server's own `N, E, D` are irrelevant — the attacker's `(e, n)` replaces the real pubkey.

## Key recon (no pkcs1.py was provided)
Verified the digest format against the live server by checking `SIGNATURE^E mod N`:
it is **SHA-1** (not SHA-256!) PKCS#1 v1.5: `00 01 FF^58 00 || SHA1-DigestInfo(15B) || SHA1(msg)`,
96 bytes. So digest = `A·2^160 + SHA1(msg)` with `A` fixed — only 160 bits of the target
are message-controlled, and the 64-hex-char suffix is inside the hash input.

## The attack
1. Pick `n = p^k` (odd prime `p ∤ SIGNATURE`, `p^k > 2^761`; live server needed p=7, k=272
   because SIGNATURE is divisible by 2 and 3). `n` composite → passes `isPrime` gate.
2. `(Z/p^k)*` is **cyclic of smooth order** `p^{k-1}(p-1)`. Compute `ord = ord_n(SIGNATURE)`.
3. After seeing the suffix, brute-force the regex padding (counter in `(.*)` / letters /
   random BTC payload) to get candidates `t = A·2^160 + SHA1(msg)` until
   `t^ord ≡ 1 (mod n)`, i.e. `t ∈ <SIGNATURE>` (~1–3 tries per gate).
4. Solve `e = log_{SIGNATURE}(t)` by **Pohlig–Hellman** (all prime factors ≤ 7).
5. `claim(index, msg, e)`: `pow(SIGNATURE, e, n) == digest(msg)` exactly and the regex gate
   passes on `msg[:-64]`. Repeat per gate with fresh `e` (e is per-claim; n shared).
   XOR the 3 shares → flag.

Runtime: ~2 s total, 5 SHA1 brute-force tries across all 3 gates.

## Why the obvious attacks fail
- `n = SIGNATURE − digest` (e=1): n must be fixed **before** the suffix is known → digest unknowable.
- `n = 2^768` 2-adic DLP (membership = local mod-4 condition): fails because live SIGNATURE is **even**.
- `n = 3^484`: fails because live SIGNATURE ≡ 0 mod 3 (non-invertible). Hence the generic small-p picker.
- Brute-forcing the suffix or a SHA1 preimage: 2^256 / 2^160 — infeasible; subgroup-membership
  brute-force over regex padding is the trick.

## Learning points
- Attacker-chosen modulus + exponent ⇒ move the DLP into a group you designed: a prime-power
  modulus gives a cyclic smooth-order group; membership in `<g>` is one `pow`, PH gives `e`.
- Order of operations matters: `e` is chosen after the nonce, `n` before — so `n` must be
  nonce-independent (a pure prime power) while `e` carries the nonce dependence.
- Fingerprint the padding format from the live oracle (`SIG^E mod N` reveals the digest)
  when the encoding module isn't shipped.

## Limitations
- Relies on `ord_n(SIGNATURE)` being a large fraction of the group order (small index ⇒
  membership brute-force succeeds); for a random SIGNATURE the index distribution makes
  failure probability negligible, but it is not a proof.
- If SIGNATURE were divisible by every small prime in the picker list, a larger smooth-ordered
  p would be needed — not implemented.

## Artifacts
- `solve.py` — attack + local server simulation (`python3 solve.py` runs the sim end-to-end)
- `live.py` — live exploit (connect, set_pubkey, 3 claims, XOR shares, writes flag file)
- `probe.py` — digest-format fingerprinting against the live server
- `flag_lets_decrypt_2.txt` — the flag

## Vulnerability (plain words)
The server verifies a claim as `pow(SIGNATURE, e, n) == PKCS1v15-digest(msg)` using an **attacker-chosen n** (set via set_pubkey, fixed before the random suffix exists) and an **attacker-chosen e** (chosen per claim, after the suffix is revealed). Because the check is exact integer equality, the attacker only needs to design a group in which `SIGNATURE^e` lands exactly on a digest value they can produce. The server's real `N, E, D` play no role in the check — the attacker's `(e, n)` replaces the real pubkey.

## How the answer follows
1. Fingerprint the digest on the live oracle: `SIGNATURE^E mod N` reveals **SHA-1** (not SHA-256) PKCS#1 v1.5, 96 bytes = `00 01 FF^58 00 || SHA1-DigestInfo(15B) || SHA1(msg)`, i.e. digest = `A·2^160 + SHA1(msg)` with A fixed — only 160 bits are message-controlled and the 64-hex suffix is inside the hash.
2. Pick `n = p^k` odd prime power with `p ∤ SIGNATURE` and `p^k > 2^761`; live server needed p=7, k=272 because SIGNATURE is divisible by 2 and 3. Composite ⇒ passes the `isPrime` gate. `(Z/7^272)*` is cyclic of smooth order `7^271·6`.
3. Compute `ord = ord_n(SIGNATURE)`. After the suffix appears, brute-force the regex-padding fields until candidate `t = A·2^160 + SHA1(msg)` satisfies `t^ord ≡ 1 mod n`, i.e. `t ∈ <SIGNATURE>` (~1–3 tries per gate; 5 SHA1 tries across all 3 gates).
4. Recover `e = log_{SIGNATURE}(t)` by Pohlig–Hellman (all prime factors of the order ≤ 7) and submit `claim(index, msg, e)` — equality holds by construction and the regex gate passes on `msg[:-64]`. Fresh `e` per gate (n shared). XOR the 3 shares → flag `crypto{let's_decrypt_w4s_t0o_ez_do_1t_ag41n}`. Total runtime ~2 s.

## Limitations / attempts that failed
- `n = SIGNATURE − digest` with e=1: n must be fixed **before** the suffix is known ⇒ digest unknowable. Dead.
- 2-adic DLP with `n = 2^768`: fails because the live SIGNATURE is **even**; `n = 3^484`: fails because SIGNATURE ≡ 0 mod 3 (non-invertible) ⇒ forced the generic small-p picker.
- Suffix brute force (2^256) or SHA-1 preimage (2^160): infeasible; subgroup-membership search over regex padding is the trick that replaces them.
- Soundness caveat: membership brute-force assumes `ord_n(SIGNATURE)` is a large fraction of the group order (small index); probabilistic, not a proof (detailed above under "Limitations").

## Sources
Provided server source `13394.py` + live probing (probe.py) only; no pkcs1.py was shipped, so the digest format was fingerprinted against the live server. No textbook cited in the original AAR — Pohlig–Hellman and the cyclicity of `(Z/p^k)*` applied self-derived per logs. No /solutions/, writeups, or third-party material consulted.
