# Course lesson — Pad Thai (Symmetric Ciphers)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Symmetric Ciphers as challenge `pad_thai`.
**Status:** completed 2026-10-05 · **Points:** 80 · **Site:** https://cryptohack.org/challenges/pad_thai/
**Ledger row:** `course__pad_thai` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Challenge 42: Pad Thai (CryptoHack Symmetric Ciphers / AES)

**Result:** **SOLVED + leaderboard-verified** (account NoBirdWasHam, 2026-10-05) — flag ``flag — recorded in COURSEWORK/aes/course-pad_thai/flag.txt`` accepted; solved-star lit. (Slug: `pad_thai`.)
**Date:** 2026-10-05 (UTC)

## Source
- Platform: CryptoHack (https://cryptohack.org/)
- Statement page: https://cryptohack.org/challenges/aes/ (card "Pad Thai", slug `pad_thai`, 80 pts)
- Interactive service: `socket.cryptohack.org 13421` (JSON line protocol: `{"option": encrypt|unpad|check}`)
- **Provided file:** `13421.py` (server source) from
  `https://cryptohack.org/static/challenges/13421_2801f3744d21e8fbd0e7bfbef59f1fe2.py` — the primary source of the solution.
- Artifacts preserved: 13421.py, oracle_final.py (working solver), runF_output.txt, msg.txt, iv_ct.txt, result.json
- Not consulted: /challenges/pad_thai/solutions/, any writeup

## The flag
``flag — recorded in COURSEWORK/aes/course-pad_thai/flag.txt``

## How it was solved
1. Read the **provided `13421.py`**. The essentials:
   - `message = urandom(16).hex()` → **exactly 32 ASCII hex bytes** (charset `0-9a-f`), a multiple of 16, so the
     CBC ciphertext is exactly **2 blocks with NO PKCS7 padding block**.
   - `get_ct` returns `iv(16) || ct(32)`.
   - `check_padding` treats `ct[:16]` as the IV, decrypts the rest, and reports whether the result is
     valid PKCS7 — a textbook **padding oracle**.
   - `check` returns the flag iff the submitted message equals `self.message`.
2. **The single-block oracle.** Sending `F || CT_b` makes the server decrypt to
   `P_0 = D(CT_b) ^ F`. I choose `F` to force the last byte of `P_0` to a chosen padding value.
3. **Byte-by-byte recovery** (block `b`, position `p` from 15→0, target padding `v = 16-p`):
   for each candidate byte `g` in `0-9a-f`, set the forged previous block `F` with
   - `F[q] = D_b[q] ^ v` for `q > p` (already-recovered suffix, forces those decrypted bytes to `v`),
   - `F[p] = g ^ v` (so decrypted byte `p` is `v` **iff** `g == D_b[p]`),
   - `F[q] = 0` for `q < p`.
   The unique `g` the oracle accepts is `D_b[p]`. Because the message is hex, only 16 candidates per
   byte → ~16·32 ≈ **512 oracle queries** total.
4. **Execute** (live, `oracle_final.py`, `runF_output.txt`):
   - `D[1] = e208356e398928a8623a7d2d301d604c`, `D[0] = b4968b88d963cc8010e9e4b653159335`.
   - CBC unchaining: `P_b = D_b ^ (IV if b==0 else CT_{b-1})` →
     `MESSAGE = 46c9ca522f2c7192958656ecda894641` (32 hex chars).
   - `check` → `{"flag": "`flag — recorded in COURSEWORK/aes/course-pad_thai/flag.txt`"}`.
   The flag is returned **by the server's own check endpoint** — ground-truth proof the recovered
   message exactly matched `self.message`.
5. **Leaderboard verification (account NoBirdWasHam).** Logged in and submitted the flag via the
   challenge page form (`POST /submit/pad_thai/`). Result: **flag ACCEPTED** — the pad_thai solved-star
   lit up (`#check-pad_thai` now `display:block`) and the account score rose 15 → 95 points (+80 =
   pad_thai's value). This is independent confirmation, separate from the socket `check`.

## Learning points
- **The padding oracle is the canonical CBC vulnerability.** A 1-bit "valid padding?" oracle leaks
  the whole plaintext, byte by byte, without ever knowing the key. Each byte needs ~128 random
  tries (256 for a full byte, only ~16 here because the message is hex).
- **The CBC relation is the linchpin.** `P_b = D(CT_b) ^ C_{b-1}`. The oracle gives me
  `D(CT_b)`; the *previous ciphertext block* (which I already have from `get_ct`) supplies the
  XOR. Forging the IV / previous block is what lets me control the decrypted byte.
- **Knowing the plaintext's structure collapses the search.** The message being a hex string cut
  every byte's candidate set from 256 to 16, cutting the query count ~16×. (The all-padding edge
  case doesn't apply here: a 32-byte message is a clean multiple of 16, so there's no padding block.)
- **Reproduce, don't trust.** I recovered `D_b` for both blocks, applied the CBC XOR, and the
  server's `check` confirmed an exact match by returning the flag — the strongest possible
  verification for this challenge.

## What I did / did not do
- Did: read the provided 13421.py, built a correct single-block CBC padding oracle, recovered the
  32-byte message (hex charset), applied the CBC unchaining, and got the flag from the live `check`
  endpoint. Preserved the solver + recovered message + IV/CT.
- Did not: the solutions page/writeups; used only the documented JSON protocol on the documented
  socket. (An earlier parallel-connection attempt got rate-limited and was abandoned in favor of a
  clean serial oracle — recorded honestly.)

## Limitations
- None material. The message is `urandom(16).hex()`, so it differs each connection; the preserved
  `runF_output.txt` + `result.json` (the live flag response) are the evidence-of-record. The flag
  was also returned by the live server, so it is verified.

## Configuration (environment for this run)
- **Date (UTC):** 2026-10-05 (solving window ~02:00-07:30Z)
- **Host OS:** Windows 11 (11), shell = git-bash/MSYS (uname: `MSYS_NT-10.0-26200`)
- **User:** <USER>
- **Interpreter:** python3 = Python 3.10.11 (primary); python = Python 3.14.7; pip 26.2.1
- **Libraries:** pycryptodome (not needed — the attack is a pure padding oracle on the provided source)
- **Working dir:** `~\Practice runs`
- **Agent:** Hermes Agent; model = qwen38-27b (provider: custom)
- **No-cheat rule applied:** challenge statement + **provided files only** (13421.py is listed in the
  statement as a challenge file, so reading it is in-scope); no `/solutions/` pages, no writeups.
