---
record: agent-aar
puzzle: challenge-17-cryptohack-digestive
category: ecc
url: https://cryptohack.org/challenges/digestive/
status: solved
date: 2026-10-14
flag_ref: "FLAGS/ecc/challenge-17-cryptohack-digestive/flag.txt"
flag_sha256: 9f79d93ba0caf7c182ce1ab33ae91049da4253b421eefe5e11de1a650b511506
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 113: Digestive (60 pts, ECC)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
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

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
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

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Sources: challenge-provided materials only; self-derived per run logs.
