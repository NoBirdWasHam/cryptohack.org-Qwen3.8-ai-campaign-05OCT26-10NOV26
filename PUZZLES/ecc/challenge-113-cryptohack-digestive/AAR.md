# AAR — Challenge 113: Digestive (60 pts, ECC)

**Date:** 2026-10-14 · **Status:** SOLVED (server-verified + user-API submitted) · **Flag:** `[flag — recorded in FLAGS/ecc/challenge-113-cryptohack-digestive/flag.txt]`
**Delta:** +60 (7345 → 7405, 158 → 159 solved) · **Method:** self-solve from statement + server behavior probing. No solutions page, no writeups consulted.

## Vulnerability

The server signs user-controlled JSON with py-ecdsa on **NIST192p**, using the raw message
as the "digest" (no real hash — the hashfunc is effectively identity on the bytes).
py-ecdsa's `sign()` defaults to `allow_truncate=True`, and its
`_truncate_and_convert_digest()` does:

```python
digest = digest[:curve.baselen]          # first 24 bytes for NIST192p
number = int.from_bytes(digest, 'big')
number >>= max(0, len(digest)*8 - order.bit_length())   # 192 - 192 = 0
```

**Consequence: an ECDSA signature over this curve depends only on the FIRST 24 BYTES of the
message.** `verify()` truncates the same way, so any message sharing those 24 bytes
verifies with the same signature.

The sign endpoint builds `{"admin": false, "username": "<lowercase>"}` — the username starts
at byte 30, so **every** message it signs has the identical first 24 bytes
`P = b'{"admin": false, "userna'`. Every signature obtainable is therefore a signature on
the single digest `A = int(P, 'big')`.

## Why the naive collision is impossible (and the actual trick)

For an admin-true message `M_goal` to verify, we need `int(M_goal[:24]) ≡ A (mod n)`.
Since `A < n` (first byte 0x7b < 0xff) and `A + n ≥ 2^192`, the **only** value in
`[0, 2^192)` congruent to `A` mod `n` is `A` itself — so `M_goal` must start with the
exact bytes `{"admin": false, "userna` (which contains `"false"`).

The escape: Python's `json.loads` keeps the **last** occurrence of a duplicate key. So the
message

```
{"admin": false, "username": "x", "admin": true}
```

starts with the exact 24-byte prefix `P` (digest A) **and** parses to `admin: true`
(duplicate `"admin"` key, last value wins).

## Exploit

1. `GET https://web.cryptohack.org/digestive/sign/a/` → `{"msg": ..., "signature": sig}`
   (sig is a signature on digest A; raw `r‖s`, 96 hex chars, sigencode_string default).
2. `M_goal = b'{"admin": false, "username": "x", "admin": true}'`
   (assert `M_goal[:24] == P` and `json.loads(M_goal)["admin"] is True`).
3. `GET /digestive/verify/<url-encoded M_goal>/<sig>` → server truncates to 24 bytes →
   digest A → ECDSA verify passes → `json.loads` → `admin` true → flag.

One request for the signature, one for the flag. Total runtime < 2 s.

## Verification of the model (evidence, not assumption)

- **Positive control:** sig from `username:"a"` sent to verify against
  `{"admin": false, "username": "b"}` (same first 24 bytes) →
  `{"error":"b is not an admin"}` — ECDSA passed, admin check reached. Truncation model confirmed.
- **Negative control:** constructed `M3` with `int(M3) ≡ int(M1) (mod n)` but different
  first 24 bytes (valid JSON, 680-variant search over JSON shapes for a safe 24-byte fill)
  → `{"error":"Signature verification failed"}`. Rules out full-message-mod-n (old py-ecdsa
  behavior) and pins the 24-byte truncation.
- **Flag returned by the server** on the verify endpoint, then **submitted via the user API**
  (`submit_flag.py digestive ...`): score delta +60 confirms it.

## Environment notes / pitfalls

- Server runs **newer py-ecdsa** (≥0.19): default `sigencode=sigencode_string` (raw r‖s, not
  DER) and `allow_truncate=True` — both differ from older versions. The raw 96-hex-char
  signature format was the first clue that truncation was in play.
- `curve.baselen` = 24 for NIST192p (order is 192 bits). The right-shift by
  `len*8 - bitlen(n)` is 0 here, so z = the 24-byte int exactly (no mod-n wrap).
- When constructing a byte-exact-prefix JSON with free 24 middle bytes, a random fill is
  ~3% likely to be valid JSON-string content (no `"`/`\`/control bytes); iterate over JSON
  shape variants (different keys/structure) until one lands. (Only needed for the negative
  control — the real exploit needs no random fill.)
- First pass (Oct 12) recorded the challenge as open; this AAR supersedes that backfilled
  placeholder.

## Artifacts

- `statement.txt` (original statement)
- Solve performed inline via `execute_code` (requests only; no script file needed — 2 HTTP
  calls). Key one-liner: `M_goal = b'{"admin": false, "username": "x", "admin": true}'`.

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
