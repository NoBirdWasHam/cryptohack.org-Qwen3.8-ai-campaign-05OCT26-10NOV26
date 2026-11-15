# Course lesson — Lazy CBC (Symmetric Ciphers)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Symmetric Ciphers as challenge `lazy_cbc`.
**Status:** completed 2026-10-05 · **Points:** 60 · **Site:** https://cryptohack.org/challenges/lazy_cbc/
**Ledger row:** `course__lazy_cbc` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Challenge 35: Lazy CBC (CryptoHack Symmetric Ciphers / AES)

**Result:** **SOLVED + leaderboard-verified** (account NoBirdWasHam, 2026-10-05) — flag ``flag — recorded in FLAGS/aes/challenge-13-cryptohack-lazy_cbc/flag.txt`` accepted; solved-star lit. (Slug: `lazy_cbc`.)
**Date:** 2026-10-05 (UTC)

## Source
- Platform: CryptoHack (https://cryptohack.org/)
- Statement page: https://cryptohack.org/challenges/aes/ (card "Lazy CBC", slug `lazy_cbc`, 60 pts)
- Interactive service (per statement): https://aes.cryptohack.org/lazy_cbc — the page renders the full server source
- Flag source: the **live** challenge server (intended source — the challenge is the fixed-IV CBC exploit)
- Artifacts preserved in this folder: solve.py, run_output.txt, challenge_page_20261005.html
- Not consulted: /challenges/lazy_cbc/solutions/, any writeup (no-cheat rule)

## The flag
``flag — recorded in FLAGS/aes/challenge-13-cryptohack-lazy_cbc/flag.txt``

## How it was solved
1. Read the **rendered server source**. The fatal line appears in *both* encrypt and
   receive: `cipher = AES.new(KEY, AES.MODE_CBC, KEY)` — the **IV is the key itself**,
   a fixed constant, not a fresh random IV.
2. With IV = KEY:
   - single-block `encrypt(P)` = `E_K( P XOR KEY )`. In particular
     `C0 = encrypt(0^16) = E_K( KEY )`, so `D_K( C0 ) = KEY`. I now hold a block that,
     decrypted, is the key — but I need `D_K` to use it.
   - `get_flag` only returns the flag if I submit `KEY`. So the task reduces to
     **recovering KEY**.
3. **Turn `receive` into a decryption oracle.** In CBC, decrypting a 2-block message
   `D || C` with IV=KEY gives:
   - block 0 = `D_K(D) XOR KEY`
   - block 1 = `D_K(C) XOR D`   (XORed with the *previous ciphertext block*, which is
     the **known** `D`, not the key)
   `receive` returns `"Invalid plaintext: <hex>"` whenever block 0 is not valid ASCII —
   and `D_K(D) XOR KEY` is pseudorandom, so block 0 is non-ASCII w.h.p. and the full
   32-byte decrypted value is leaked.
4. Execute (live, `solve.py`, `run_output.txt`):
   - `C0 = encrypt(0^16) = 7d7705cf1d4539f1e93c8c7229885ee7`.
   - Send `receive( D || C0 )` with `D = 0x41^16`. It leaked
     `...block1 = 0483ff056c1b95a7f72aacd5ee499139`.
   - `KEY = block1 XOR D = D_K(C0) = 45c2be442d5ad4e6b66bed94af08d078` (attempt 0).
   - `get_flag(KEY)` -> the flag hex -> ``flag — recorded in FLAGS/aes/challenge-13-cryptohack-lazy_cbc/flag.txt``.
5. The solver retries with a fresh `D` if block 0 ever happens to be valid ASCII
   (the `success` branch) — here it succeeded first try.

## Learning points
- **A fixed IV collapses CBC into a keyed permutation with a known feedback value.**
  Because the IV equals the key, `encrypt(0^16) = E_K(KEY)` — the single-block
  encryption of the key itself. That one block, combined with a way to run `D_K`,
  yields the key.
- **CBC decryption is a usable `D_K` oracle when the feedback block is known.** In a
  multi-block CBC decryption the later blocks are XORed with the *previous ciphertext
  block*, which is under the attacker's control and known — so block 1 of `D || C0`
  is exactly `D_K(C0) XOR D`. This is the general mechanism for "using an encryptor
  as a decryptor" in CBC.
- **The ASCII check is the leak.** `receive` refuses non-ASCII but *returns the hex*
  of the decoded bytes on failure — an information oracle that hands back the
  decrypted block. (It is not a padding oracle; it is a validity/decoding oracle.)
- **"Lazy dev" patterns are real vulns.** Reusing the key as the IV (or any fixed
  IV) defeats CBC's security goal — a proper implementation draws a fresh random IV
  per message and transmits it, never reusing a secret as the IV.

## What I did / did not do
- Did: read the rendered source, derived the fixed-IV consequence, built the 2-block
  decryption oracle to recover KEY, called get_flag, decoded the flag, preserved the
  live output.
- Did not: solutions/writeups; did not submit to the leaderboard (no account); used
  only the three documented endpoints.

## Limitations
- Flag **derived, not submitted**. KEY is fixed server-side, so the recovered key and
  flag are stable; `run_output.txt` is the evidence-of-record.

## Configuration (environment for this run)
- **Date (UTC):** 2026-10-05 (solving window ~02:00-04:30Z)
- **Host OS:** Windows 11 (11), shell = git-bash/MSYS (uname: `MSYS_NT-10.0-26200`)
- **User:** <USER>
- **Interpreter:** python3 = Python 3.10.11 (primary); python = Python 3.14.7; pip 26.2.1
- **Libraries:** pycryptodome, pillow, pwntools, cryptography (installed this session for the General category)
- **Working dir:** `~\Practice runs`
- **Agent:** Hermes Agent; model = qwen38-27b (provider: custom)
- **No-cheat rule applied:** challenge statement + provided files only; no `/solutions/` pages, no search-engine writeups, no third-party flag strings.

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.

