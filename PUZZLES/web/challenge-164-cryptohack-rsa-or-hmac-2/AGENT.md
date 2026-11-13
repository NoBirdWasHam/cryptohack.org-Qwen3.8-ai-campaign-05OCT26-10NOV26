---
record: agent-aar
puzzle: challenge-164-cryptohack-rsa-or-hmac-2
category: web
url: https://cryptohack.org/challenges/rsa-or-hmac-2/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/web/challenge-164-cryptohack-rsa-or-hmac-2/flag.txt"
flag_sha256: 102b91c9797c31d90f2f47d8480786712c5817a369bc6f667343bc493f8f3a3a
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 164: RSA or HMAC? Part 2
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (two stages)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. **Recover the RSA public key from signatures** (no pubkey route this time).
   `create_session/<user>/` signs a *known* payload with RS256/PKCS1v15-SHA256, so the padded
   block `m` is fully reconstructible. Verification identity `s^e ≡ m (mod n)` ⇒ `s^e − m = k·n`.
   Three signatures (alice/bob/carol) → `n = gcd(S1,S2,S3)` (strip 2s) → 2048-bit modulus,
   verified `s^e mod n == m` for all three.
   - **Perf pitfall:** `s^65537` unmodded = 134-million-bit integer. CPython `pow`/`math.gcd`
     hang (>100 s, effectively minutes); **gmpy2** does each exp in 0.4 s and the full gcd chain
     in 34 s. Install `gmpy2` for any s^e−m modulus recovery.
2. **Data formatting:** the server's key file is `openssl rsa -RSAPublicKey_out` format —
   `-----BEGIN RSA PUBLIC KEY-----` (RSAPublicKey DER, *not* SPKI). Rebuilt canonical DER
   `SEQUENCE{INTEGER n, INTEGER e}`, base64 at 64 cols, LF endings, trailing newline after the
   footer — that exact byte string is the HMAC secret.
3. **Alg-confusion forge** (same as part 1): HS256 token `{"username":"admin","admin":true}`,
   HMAC key = PEM bytes → `authorise/` → flag.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: solve.py, solve2.py, variants.py
- data/logs: flag_response.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Sources: challenge-provided materials only; self-derived per run logs.
