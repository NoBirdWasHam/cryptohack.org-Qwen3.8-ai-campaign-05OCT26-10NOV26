# AAR — Challenge 164: RSA or HMAC? Part 2

**Result: SOLVED + API-VERIFIED 2026-10-20.** Flag `crypto{thanks_silentsignal_for_inspiration}`
submitted; score 9835→9935 (+100), solved 187→188.

## Attack (two stages)
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

## Notes
- First forge attempt (solve2.py, identical bytes) returned "Signature verification failed";
  the variants matrix run minutes later accepted `trad_lf_nl` on the first try — consistent with
  the flaky multi-worker/redeploy behavior seen on part 1 (#160). Retry before debugging bytes.
- Files: `solve2.py` (modulus recovery + PEM), `variants.py` (byte-exactness matrix + forge),
  `pubkey_recovered.pem`, `flag_response.json`.

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
