# Course lesson — RSA Signatures (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `rsa_starter_6`.
**Status:** completed 2026-10-06 · **Points:** 25 · **Site:** https://cryptohack.org/challenges/rsa_starter_6/
**Ledger row:** `course__rsa_signatures` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — RSA Signatures (challenge-54)

## 1. Result
**SOLVED** — signature `S` (614-digit integer, in `sig.txt`), submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `rsa_starter_6`)
- Provided file: `private.key` from `https://cryptohack.org/static/challenges/private_0a1880d1fffce9403686130a1f932b10.key` (plain-text `N = ...` / `d = ...`, 2047-bit modulus)
- **NOT consulted:** solutions/writeups.

## 3. Answer + verification
- `S = bytes_to_long(SHA256(b"`flag — recorded in COURSEWORK/rsa/course-rsa_starter_6/flag.txt`"))^d mod N`.
- Self-check: `S^e mod N == bytes_to_long(SHA256(msg))` with e=65537 ✓ (the verifier's exact check).
- Verified by the leaderboard star.

## 4. How it was solved
1. Parse `private.key` — it's NOT PEM; it's plain `N = ...` / `d = ...` lines (`RSA.import_key` fails on it — parse manually).
2. `H = hashlib.sha256(b"`flag — recorded in COURSEWORK/rsa/course-rsa_starter_6/flag.txt`").digest()`.
3. `S = pow(bytes_to_long(H), d, N)`.
4. Verify `pow(S, e, N) == bytes_to_long(H)`.

## 5. Learning points
- RSA "signing" = encrypting the hash with the **private key** (`S = H^d mod N`); verification = `S^e mod N == H`. Sign and encrypt are the same math, different key.
- Always hash before signing (raw-message RSA is malleable and breaks for multi-block messages).
- Provided key files aren't always standard formats — read the file before assuming PEM.

## 6. What I did / did not do
Did: parse the key, sign, verify against the statement's check, submit, verify star. Did not: consult solutions.

## 7. Limitations
Answer-challenge (the signature integer is the answer).

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 (pycryptodome) · Workdir: `...\challenge-54-cryptohack-rsa-signatures\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/` (submit/verify), static key file fetch

## Vulnerability (plain words)

No vulnerability -- this is the signing step: RSA signing is the same trapdoor permutation with
the keys swapped. `S = H^d mod N` where H = int(SHA-256(message)); anyone with the PUBLIC key
computes `S^e mod N = H^(ed) = H` (the e*d = 1 + k*phi relation from #52), so only a holder of d
can produce an S that round-trips under e -- that is what makes S a signature rather than a
random number. Hashing the message first is what fits any-length messages under one 2047-bit
modulus and kills raw RSA's multiplicative malleability (S1*S2 verifies for concatenated "signed"
messages).

## How the answer follows

The provided key file is NOT PEM: plain `N = ...` / `d = ...` lines (AAR section 4; pycryptodome
`RSA.import_key` fails on it -- parse manually). `H = SHA256(b"`flag — recorded in COURSEWORK/rsa/course-rsa_starter_6/flag.txt`")` as
a big-endian integer; `S = pow(H, d, N)` -- the 614-digit integer archived in `sig.txt`; the
self-check `pow(S, 65537, N) == H` is exactly the verifier's equation (AAR section 3); submitted
and star-verified.

## Limitations / attempts that failed

- Recorded stumble: `RSA.import_key` on the provided key failed (text `N = ...`/`d = ...`, not
  PEM); fixed by manual parsing (AAR sections 4-5).
- Answer challenge (the signature integer IS the answer); no run_log.txt in the folder; no other
  failed attempts recorded in run logs.
- Scope note (addition, not a correction): this is textbook "hash then private-exponent" signing,
  not RSASSA-PKCS1-v1_5 or PSS padding -- fine for the exercise, never for production.

## Sources

- Statement card `rsa_starter_6` on `https://cryptohack.org/challenges/rsa/` (`site.md`);
  provided key `https://cryptohack.org/static/challenges/private_0a1880d1fffce9403686130a1f932b10.key`
  (archived as `private.key`); answer archived as `sig.txt`.
- Self-derived per logs; NOT consulted: solutions/writeups (AAR section 2).
- Upgrade note: recomputed at upgrade time from the archived `private.key` + stdlib SHA-256 --
  the recomputed S matches the archived `sig.txt` exactly and `S^e mod N == H` holds
  (comprehension check, not a new solve).

