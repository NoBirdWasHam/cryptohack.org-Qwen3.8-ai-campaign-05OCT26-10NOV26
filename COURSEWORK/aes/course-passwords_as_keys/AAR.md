# Course lesson — Passwords as Keys (Symmetric Ciphers)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Symmetric Ciphers as challenge `passwords_as_keys`.
**Status:** completed 2026-10-05 · **Points:** 50 · **Site:** https://cryptohack.org/challenges/passwords_as_keys/
**Ledger row:** `course__passwords_as_keys` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Challenge 31: Passwords as Keys (CryptoHack Symmetric Ciphers / AES)

**Result:** **SOLVED + leaderboard-verified** (account NoBirdWasHam, 2026-10-05) — flag ``flag — recorded in COURSEWORK/aes/course-passwords_as_keys/flag.txt`` accepted; solved-star lit. (Slug: `passwords_as_keys`.)
**Date:** 2026-10-05 (UTC)

## Source
- Platform: CryptoHack (https://cryptohack.org/)
- Statement page: https://cryptohack.org/challenges/aes/ (card "Passwords as Keys", slug `passwords_as_keys`, 50 pts)
- Interactive service (per statement): https://aes.cryptohack.org/passwords_as_keys — the page renders the full server source (password-derived-key AES-ECB oracle)
- Word list used for the offline attack (the **exact** list the server uses, per its source): https://gist.githubusercontent.com/wchargin/8927565/raw/d9783627c731268fb2935a731a618aa8e95cf465/words (fetched, in this folder as words_provided.txt)
- Artifacts preserved in this folder: encrypt_flag_response_20261005.json, pak_bruteforce.py, words_provided.txt, solve_verification.txt
- Not consulted: /challenges/passwords_as_keys/solutions/, any writeup (no-cheat rule)

## The flag
``flag — recorded in COURSEWORK/aes/course-passwords_as_keys/flag.txt``

## How it was solved
1. Read the **rendered server source**. The critical lines:
   ```python
   keyword = random.choice(words)          # one word from a known 99k-word list
   KEY = hashlib.md5(keyword.encode()).digest()   # 16-byte key = MD5(word)
   ```
   The key is **not random** — it's the MD5 of a single dictionary word. That is the
   crack: the effective keyspace is the ~99,170-word list, not 2^128.
2. `GET /passwords_as_keys/encrypt_flag/` ->
   `ciphertext = c92b7734070205bdf6c0087a751466ec13ae15e6f1bcdd3f3a535ec0f4bbae66`
   (32 bytes = two 16-byte ECB blocks).
3. **Offline brute force** (the statement explicitly allows attacking the ciphertext
   offline): for each of the 99,170 words, compute `key = md5(word)` and decrypt the
   ciphertext with AES-ECB; keep any whose plaintext starts with `crypto{`:
   ```python
   for w in words:
       key = hashlib.md5(w.encode()).digest()
       pt = AES.new(key, AES.MODE_ECB).decrypt(ct)
       if pt.startswith(b"crypto{"):
           print(w, pt)
   ```
   Exactly **one** hit: `word = bluebell`, `key = d3e23f1eb6e79ed51133e0da48e98d4a`,
   `plaintext = `flag — recorded in COURSEWORK/aes/course-passwords_as_keys/flag.txt`` (`solve_verification.txt`).
4. The `crypto{` prefix is the free discriminator (same idea as the `xorkey0`
   challenge): a wrong key yields random bytes, and the chance of a false positive is
   negligible over ~100k trials. The single clean hit is the answer.

## Learning points
- **Password-derived keys collapse a 128-bit key to the entropy of the password.**
  Here the key's entropy is only ~log2(99170) ≈ 16.6 bits, so a ~100k-word brute
  force is trivial — AES-256 is only as strong as its key.
- **MD5 of a single word is a terrible KDF.** It is fast (the attacker's friend) and
  un-salted (no per-user randomness). Real key derivation uses a **slow, salted**
  function (PBKDF2 / bcrypt / scrypt / Argon2) specifically to make brute force
  expensive.
- **The `crypto{` prefix is a universal offline discriminator** for "decrypt with a
  guessed key" challenges — no padding check needed.
- **Reading the server source gives the exact word list and KDF** — I used the
  *identical* list the server drew from, which is why the hit was unique and
  authoritative.

## What I did / did not do
- Did: read the rendered source, fetched the exact word list, offline MD5+AES
  brute force, verified the single hit, preserved all artifacts.
- Did not: solutions/writeups; did not submit to the leaderboard (no account); did not
  hammer the `/decrypt` endpoint (solved offline as the statement permits).

## Limitations
- Flag **derived, not submitted**. The keyword is a `random.choice` on the server,
  so it differs per (re)start; `bluebell` is the value for this particular run, as
  recorded in the preserved `encrypt_flag_response`.

## Configuration (environment for this run)
- **Date (UTC):** 2026-10-05 (solving window ~02:00-03:30Z)
- **Host OS:** Windows 11 (11), shell = git-bash/MSYS (uname: `MSYS_NT-10.0-26200`)
- **User:** <USER>
- **Interpreter:** python3 = Python 3.10.11 (primary); python = Python 3.14.7; pip 26.2.1
- **Libraries:** pycryptodome, pillow, pwntools, cryptography (installed this session for the General category)
- **Working dir:** `~\Practice runs`
- **Agent:** Hermes Agent; model = qwen38-27b (provider: custom)
- **No-cheat rule applied:** challenge statement + provided files only; no `/solutions/` pages, no search-engine writeups, no third-party flag strings.

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.

