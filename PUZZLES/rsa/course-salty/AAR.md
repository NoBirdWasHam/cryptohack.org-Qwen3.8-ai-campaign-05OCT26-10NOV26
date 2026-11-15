# Course lesson — Salty (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `salty`.
**Status:** completed 2026-10-06 · **Points:** 20 · **Site:** https://cryptohack.org/challenges/salty/
**Ledger row:** `course__salty` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Salty (challenge-60)

## 1. Result
**SOLVED** — flag ``flag — recorded in FLAGS/rsa/course-salty/flag.txt``, submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `salty`)
- Provided files: `salty_provided.py`, `salty_output.txt` (from the category-page file links)
- **NOT consulted:** solutions/writeups.

## 3. The flag + verification
- ``flag — recorded in FLAGS/rsa/course-salty/flag.txt``
- Verified: `e = 1` in the output, so `ct == pt` by definition (`pow(pt, 1, n) = pt mod n`, and the
  flag is far smaller than the 1024-bit n). The ciphertext integer IS the flag bytes. Star lit.

## 4. How it was solved
1. Provided source sets `e = 1`.
2. RSA encrypt `ct = pow(pt, 1, n) = pt` (identity map).
3. `long_to_bytes(ct)` = ``flag — recorded in FLAGS/rsa/course-salty/flag.txt``.

## 5. Learning points
- The public exponent `e` must be **coprime to φ(n)** and greater than 1 for encryption to be a
  bijection on the message space. `e = 1` makes encryption the identity — "smallest exponent should
  be fastest, right?" is the trap: it's not fast, it's *free*.
- Always sanity-check the *given* parameters (here `e=1` is a dead giveaway) before reaching for
  factorization.

## 6. What I did / did not do
Did: read the provided source + output, spotted e=1, converted ct→bytes, submitted, verified star.
Did not: consult solutions.

## 7. Limitations
None — the result is a direct consequence of e=1 (no ambiguity).

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 (pycryptodome) · Workdir: `...\challenge-60-cryptohack-salty\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/` (submit/verify), static file fetches


## Vulnerability (plain words)
The provided code encrypts with public exponent e = 1, so ct = pow(pt, 1, n) = pt: RSA becomes the
identity map and the ciphertext integer is already the plaintext.

## How the answer follows
1. `salty_provided.py` sets e = 1; `salty_output.txt` carries ct.
2. e = 1 ⇒ ct == pt; the flag (<< 2^1024) is unreduced, so long_to_bytes(ct) =
   ``flag — recorded in FLAGS/rsa/course-salty/flag.txt`` directly; star verified 2026-10-06.

## Limitations / attempts that failed
None recorded — e = 1 makes the result a direct, unambiguous consequence of the parameters. No
solutions/writeups consulted.

## Sources
Provided `salty_provided.py` + `salty_output.txt`; self-derived; no writeups.

