# Course lesson — Forbidden Fruit (Symmetric Ciphers)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Symmetric Ciphers as challenge `forbidden_fruit`.
**Status:** completed 2026-10-06 · **Points:** 150 · **Site:** https://cryptohack.org/challenges/forbidden_fruit/
**Ledger row:** `course__forbidden_fruit` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Forbidden Fruit (GCM fixed-IV forgery)

## 1. Result

**SOLVED** — flag `crypto{https://github.com/attr-encrypted/encryptor/pull/22}`,
submitted to the CryptoHack leaderboard and verified (solved-star lit) on **2026-10-06 (UTC)**.

## 2. Source

- Statement + provided source: `https://aes.cryptohack.org/forbidden_fruit/` (fetched 2026-10-06, verbatim in `site.md`)
- Category card: `https://cryptohack.org/challenges/aes/`
- Live service: `https://aes.cryptohack.org/forbidden_fruit/` (GET `/encrypt/<hex>/`, `/decrypt/...`)
- Reference link in the statement (inner workings + this exact attack): `https://toadstyle.org/cryptopals/63.txt` — **read as a learning reference only**; the attack below was derived and implemented independently against the live service, with every relation re-verified against a local pycryptodome GCM before touching the service.
- **NOT consulted:** the `/solutions/` and `/solves/` pages, the 8 published solutions, and no search-engine writeups.

## 3. The flag and its verification

- Flag (hex-decoded from the service response): `crypto{https://github.com/attr-encrypted/encryptor/pull/22}`
- Verified three ways:
  1. **Local forge** against pycryptodome GCM with a known key: `decrypt_and_verify` accepted the forged `(C*, tag*)` and returned `b"give me the flag"` — proves the pipeline is mathematically correct, not just live-luck.
  2. **Live**: `decrypt(IV, C*, tag*, AAD)` accepted the tag (no "Invalid authentication tag") and returned the flag.
  3. **Leaderboard**: after `POST /submit/forbidden_fruit/`, the `#check-forbidden_fruit` solved-star on `/challenges/aes/` went `display:none → display:block`. (The submit response body is identical for correct/wrong flags; the star is the ground truth.)

## 4. How it was solved (reproducible)

Setup (from source): `encrypt(P)` = AES-128-GCM with **fixed** 96-bit IV and AAD = `b"CryptoHack"`;
`J0 = IV‖0³¹‖1`; `C = CTR_{J0+1}(P)`; `tag = GHASH_H(A,C) ⊕ E_K(J0)`.

GF(2^128) implementation (`gm`), validated to reproduce pycryptodome tags exactly (see pitfall in §5):
element = big-endian 16-byte int; `gm(x,y)`: scan **x MSB-first**, and at each step right-shift
`y`, XORing `0xE1<<120` **iff the shifted-out LSB was set** (NIST 800-38D bit convention:
`x_0` = MSB, `y_127` = LSB). Multiplicative identity in this representation is `1<<127`.

1. **Keystream block 0:** `C0 = encrypt(0^16) → ciphertext`. Since `C = P ⊕ KS`, `C0` is the first 16 keystream bytes. Any 16-byte plaintext can be forged by XORing with `C0`.
2. **Recover S = H²:** send `P_a = 0^16` (tag `t_a`) and `P_b = 0x11·16` (tag `t_b`).
   Same (KEY, IV) ⇒ same counter blocks, so the tag difference isolates the C-difference in GHASH:
   `t_a ⊕ t_b = (C_a ⊕ C_b) · H² = d · H²` (A and L blocks contribute equally and cancel).
   Hence `S = (t_a ⊕ t_b) · d^{-1} = H²`, with `d = 0x11·16` (the ciphertext difference, also the keystream-XOR of the two inputs).
3. **Recover H:** `H = S^{2^127}` — 127 repeated squarings (`gm(r,r)`). In GF(2^128) the Frobenius
   map `x → x²` is a bijection (the field has exactly one square root of every element), so this is exact, no search.
4. **Sanity check before forging (the step that caught the bug):** send a third input `P_c = 0x77·16`; assert `t_0 ⊕ t_c == (C_0 ⊕ C_c) · H²` using the *recovered* H. (First runs failed here — see §5.)
5. **Recover E_K(J0):** `E_K(J0) = tag_a ⊕ GHASH_H(A, C_a)` — we now have H.
6. **Forge:** `P* = b"give me the flag"` (exactly 16 bytes), `C* = P* ⊕ C0`,
   `tag* = GHASH_H(A, C*) ⊕ E_K(J0)`, then `decrypt(IV, C*, tag*, "CryptoHack".hex())`.
   The server decrypts to the trigger string and returns the flag.

Total live requests: 4 encrypts + 1 decrypt (one clean run). Scripts: `final3.py` (solver, with
mandatory local self-test gate), `local_verify2.py` (local proof), `gmwhich.py` (GM-convention
validation), `stab.py`/`det2.py` (service determinism).

## 5. Learning points

- **Fixed-IV GCM = full keystream + tag-forge.** The IV is the whole story: reuse leaks the
  keystream (XOR of any two ciphertexts) and the GHASH key H via tag-linearity. The challenge
  itself points at cryptopals set 63 problem 6 — this is *that* attack.
- **The 1-block delta gives H², not H.** GHASH places A at H³, C at H², L at H¹. With A and L
  fixed, a 1-block ciphertext difference lands exactly on H². Two independent routes to H:
  (a) 2-block plaintext difference (differential of the H³·d₁ + H²·d₂ form) or
  (b) **square root** `H = (H²)^{2^127}`. Route (b) is one 127-squaring chain and needs no
  second multi-block request — cleaner, and it's what the final solver uses.
- **The bug that cost the most time: the field identity, not the multiply.** `gm` (multiply)
  was correct from the start — it reproduced pycryptodome tags. The field *inverse* helper was
  seeded with `r = 1` (integer one) instead of the multiplicative identity `1<<127` in this
  bit representation. Every "consistency check" (constant S across pairs, H²==S after sqrt)
  *passed* because they are invariant under the fixed scalar error — but any relation that
  must equal the *true* H (third-pair check, tag recompute, forge) failed. **Lesson: a
  "consistent" algebraic pipeline can be globally rescaled/wrong while every internal check
  passes; at least one check must be pinned to an independent ground truth (here: a local
  pycryptodome GCM with a known key) before trusting the pipeline.**
- **Validate the GF(2^128) multiply against a known-correct implementation, printing actual
  tag hex.** "It looks like NIST" is not verification. One test comparing computed vs
  pycryptodome tags for 16/32-byte messages (with the hex printed) settles the bit convention
  in seconds.
- **`decrypt` taking our nonce was the intended win condition** — we never needed to guess
  the server IV; we forged under the *fixed encrypt IV* and passed it straight back.
- **Process:** a mandatory self-test (local, pycryptodome-grounded) before any live run is
  worth its weight — every failed live attempt here was predicted by a local self-test
  failure; the one live success was predicted by a local self-test pass.

## 6. What I did / did not do

- Did: fetched the statement page and provided source verbatim; implemented GM/GHASH/inverse/
  sqrt from first principles; validated them against local pycryptodome; confirmed service
  determinism (same input ⇒ same IV/CT/tag, 4 repeats); solved with 4 encrypts + 1 decrypt;
  submitted and verified via the leaderboard star; saved transcript + all scripts.
- Did not: open any solution/writeup; reuse any published flag; hammer the service (one clean
  run, a handful of determinism probes); modify or fuzz the service beyond the stated routes.

## 7. Limitations

- H-recovery via the square root relies on the standard GCM GHASH (confirmed by the provided
  source using pycryptodome `AES.MODE_GCM`); if the service used a non-standard GHASH
  (e.g. reversed bit order in H), the same pipeline applies with the convention validated
  against pycryptodome (which is exactly how it was done here).
- The 0x11/0x22/0x77 delta constants are arbitrary; any nonzero 16-byte deltas work.
- No attempt was made to recover KEY or IV as values (not needed; the attack only needs
  H, E_K(J0), and the keystream block, all derivable from tags/ciphertexts).

## 8. Configuration

- **Date:** 2026-10-06 (UTC), solve completed ~11:22 UTC
- **Host OS / shell:** Windows 11 (MSYS_NT-10.0-26200), git-bash (MSYS 3.6.6)
- **User:** <USER>
- **Interpreter:** python3 = Python 3.10.11 (pycryptodome available)
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-47-cryptohack-forbidden-fruit\`
- **Agent / model:** Hermes Agent (Nous Research), model qwen38-27b, custom provider, desktop platform
- **Tools:** terminal (python3), browser (login + leaderboard verification via in-page sync XHR), web_extract (statement fetch)
- **Network contacts:** `https://aes.cryptohack.org/forbidden_fruit/` (4 GET /encrypt + 1 GET /decrypt), `https://cryptohack.org/challenges/aes/` (login/submit/verify), `https://aes.cryptohack.org/forbidden_fruit/` (statement fetch)
- **Key files:** `final3.py` (working solver), `local_verify2.py` (local proof), `gmwhich.py` (GM validation), `stab.py`/`det2.py` (determinism), `live_transcript_2026-10-06.txt`, `result.json`

## Vulnerability (plain words)

GCM run with a FIXED IV: every encryption reuses the same CTR keystream (counter stream starting
at `J0+1`, `J0 = IV||0^31||1`) and the same GHASH key `H = E_K(0^128)`. The first keystream block
is `encrypt(0^16)`, so any 16-byte plaintext is forgeable by XOR. The tag
`tag = GHASH_H(A, C) XOR E_K(J0)` is affine in the ciphertext for fixed AAD and lengths: two tag
queries on `0^16` and `0x11*16` give `t_a XOR t_b = d * H^2` in GF(2^128) (the A and L terms
cancel; the 1-block C difference sits on `H^2`), so `H^2 = (t_a XOR t_b) * d^-1`, and
`H = (H^2)^(2^127)` because the Frobenius map x -> x^2 is a bijection on GF(2^128) -- exact
square root, no search. Knowing H gives `E_K(J0) = tag XOR GHASH_H(A, C)`, hence a valid tag for
ANY ciphertext: full forgery.

## How the answer follows

One clean run of 4 encrypts + 1 decrypt (AAR section 4): (1) `encrypt(0^16)` yields keystream
block `C0`; (2-3) the `0^16`/`0x11*16` tag pair yields `H^2`, thence H by 127 squarings; (4) a
third pair `0x77*16` sanity-checks `t_0 XOR t_c == (C_0 XOR C_c) * H^2` under the recovered H;
(5) forge `P* = b"give me the flag"` -> `C* = P* XOR C0`, `tag* = GHASH_H(A, C*) XOR E_K(J0)`,
and `decrypt(IV, C*, tag*, AAD="CryptoHack")` returns the flag
`crypto{https://github.com/attr-encrypted/encryptor/pull/22}`. Verified three ways: local
pycryptodome accepts the forgery and returns the trigger string, the live service accepts it, and
the leaderboard star lit (AAR section 3).

## Limitations / attempts that failed

- Failed attempts (recorded): early runs failed the third-pair consistency check because the
  GF(2^128) inverse helper was seeded with integer `1` instead of the field identity `1<<127` in
  the big-endian bit representation. Every internal consistency check still PASSED (they are
  invariant under the fixed rescaling); the error was caught only by a check pinned to an
  independent ground truth, then settled by `gmwhich.py` validating the multiply against
  pycryptodome tags printed in hex.
- The attack never recovers KEY or IV as values -- only H, `E_K(J0)`, and keystream block 0
  suffice (AAR section 7). Delta constants 0x11/0x77 are arbitrary.
- A non-standard GHASH bit convention would change the representation, not the attack; the
  convention used was validated against pycryptodome (AAR section 7).

## Sources

- `https://aes.cryptohack.org/forbidden_fruit/` (statement + provided source, `site.md`); the
  statement's own reference link `https://toadstyle.org/cryptopals/63.txt` was read as a learning
  reference only -- the attack was derived and run independently against the live service (AAR
  section 2). NOT consulted: `/solutions/`, `/solves/`, writeups.
- NIST SP 800-38D GHASH bit convention (implemented and validated in the `gm` multiply); local
  pycryptodome GCM as ground truth.
- Scripts: `final3.py` (solver + mandatory local self-test gate), `local_verify2.py`,
  `gmwhich.py`, `stab.py`/`det2.py`, `live_transcript_2026-10-06.txt`, `result.json`.
- Upgrade note: restated from AAR sections 3-5 + scripts; service NOT re-run (offline unit).

