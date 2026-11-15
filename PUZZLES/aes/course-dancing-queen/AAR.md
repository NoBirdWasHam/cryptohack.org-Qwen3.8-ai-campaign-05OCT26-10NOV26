# Course lesson — Dancing Queen (Symmetric Ciphers)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Symmetric Ciphers as challenge `dancing-queen`.
**Status:** completed 2026-10-06 · **Points:** 120 · **Site:** https://cryptohack.org/challenges/dancing-queen/
**Ledger row:** `course__dancing_queen` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Challenge 44: Dancing Queen (CryptoHack Symmetric Ciphers / AES)

**Result:** SOLVED — flag ``flag — recorded in FLAGS/aes/course-dancing-queen/flag.txt`` submitted and verified
(solved-star lit on https://cryptohack.org/challenges/aes/).
**Date:** 2026-10-05 (UTC)

## Source
- Platform: CryptoHack (https://cryptohack.org/)
- Statement page: https://cryptohack.org/challenges/aes/ (card "Dancing Queen", slug `dancing-queen`, 120 pts)
- Verbatim statement: "I don't trust other developers so I made my own ChaCha20 implementation.
  In this way, I am sure you will never be able to read my flag!" Challenge files: `chacha20.py`, `output.txt`.
- Provided files (in-scope):
  - `https://cryptohack.org/static/challenges/chacha20_c76e2a43164af8b6ecb0e145415ab931.py` → `chacha20.py`
  - `https://cryptohack.org/static/challenges/output_108f5c189506fcb4309410776af3117d.txt` → `output.txt`
- Interactive service: **none** (fully offline; no socket/HTTP).
- Not consulted: /challenges/dancing-queen/solutions/ (8 solutions exist), /solves/, any writeup.

## The flag
``flag — recorded in FLAGS/aes/course-dancing-queen/flag.txt`` — verified by the solved-star on the category page.
The flag text itself names the attack ("Mixing rounds are invertible").

## How it was solved
1. **Read the provided `chacha20.py`.** The custom ChaCha20's `encrypt` does
   `c += xor(m[i:i+64], words_to_bytes(self._state))` after 10 rounds of the block function —
   the **keystream is the full 64-byte MODIFIED state**, not standard ChaCha20's
   `(modified + initial) mod 2^32` over the last 12 words (48 bytes).
2. **State layout** (`_setup_state`): words 0-3 = constants, 4-11 = 32-byte key, 12 = counter,
   13-15 = 12-byte IV. `encrypt()` resets `self._counter = 1` on every call.
3. **`output.txt`:** `iv1`, `iv2`, `msg_enc` (80 bytes, known 80-byte message from the file),
   `flag_enc` (37 bytes). Same key for both; different IVs.
4. **Invert the block:** the ChaCha20 block function is a **bijection**, so the modified state
   inverts to the initial state. `msg_enc[0:64] = msg[0:64] XOR modified_state0`
   (msg[0:64] known) → `modified_state0` → apply 10 rounds of the **inverted** quarter-round
   (reverse round order, inverse ops: rotate-right then un-xor then subtract) → `initial_state0`.
5. **Recovered key** (initial-state words 4-11): `39fd1410fef6485bf3068ea0fb3a8ff6385b4483bc1f321cea4f15cc1c43496c`.
   Self-checks all passed: words 0-3 = ChaCha constants, word 12 = counter 1, words 13-15 = iv1;
   forward block(counter=1) reproduces msg_enc[0:64] and forward block(counter=2) reproduces msg_enc[64:].
6. **Flag keystream:** build initial state (constants, recovered key, counter 1, iv2), run the
   buggy block, `keystream = words_to_bytes(modified)`, `flag = flag_enc XOR keystream[:37]`.
7. **Submit & verify** via in-page fetch POST `/submit/dancing-queen/`; star lit.

## Learning points
- **"My own implementation" is the vulnerability class.** A hand-rolled stream cipher that emits
  the raw modified state instead of `modified+initial` leaks the state directly.
- **The ChaCha20 block is a bijection** (all ops — 32-bit add, xor, rotate — are invertible), so
  any observed modified state inverts to the initial state. This is the "mixing rounds are
  invertible" idea: the ARX (add-rotate-xor) core is reversible round-by-round.
- **Inverting a block cipher = running the inverse rounds in reverse order** with inverse ops
  (rotate-right for rotate-left; subtract for add; xor is self-inverse). Standard technique,
  same as AES key schedule inversion / codebook building.
- **Known plaintext + full modified state = key.** Once the key is out, every other (key, iv, counter)
  keystream is trivially computable.
- **Reproduce-don't-trust:** the forward self-check (re-encrypt the known message with the
  recovered key and compare) is what makes key recovery airtight — a single wrong inverse op
  fails the assert immediately.

## What I did / did not do
- Did: read only the statement + provided files; derived the bug from the source; built the
  inverse block; self-checked the recovered key against the known message; submitted and verified.
- Did not: consult solutions/solves/writeups; no third-party flag; no interactive service existed.

## Limitations
- None for this challenge. The recovered key is the challenge's key (deterministic from the
  provided files); the flag is the challenge's flag.

## Configuration (environment for this run)
- **Date (UTC):** 2026-10-05
- **Host OS:** Windows 11 (11), shell = git-bash/MSYS
- **User:** <USER>
- **Interpreter:** python3 = Python 3.10.11
- **Libraries:** stdlib only (int.from_bytes, bitwise ops) — no pycryptodome needed
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-44-cryptohack-dancing-queen`
- **Artifacts:** chacha20.py, output.txt, solve.py, solve_log.txt, flag.txt
- **Agent:** Hermes Agent; model = qwen38-27b (provider: custom)
- **Network contacts:** cryptohack.org (statement/files/submit), no interactive service.
- **No-cheat rule applied:** challenge statement + provided files only.

## Sources
- Case (a) — provided materials only: statement/course page, server source and provided
  files (see `## Source` above). `/solutions/` pages and third-party writeups NOT consulted,
  per the run logs. No textbook/paper/RFC cited.

