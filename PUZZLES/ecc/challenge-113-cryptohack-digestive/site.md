# Digestive (digestive)
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category:** Elliptic Curve Crypto (https://cryptohack.org/challenges/ecc/)
- **Name / points:** Digestive / 60 pts
- **Slug:** `digestive` (folder `challenge-113-cryptohack-digestive`)
- **Interactive service:** web.cryptohack.org (endpoints: `/digestive/sign/<username>/`, `/digestive/verify/<msg>/<sig>/`)
- **Status:** SOLVED 2026-10-14 — flag `[flag — recorded in FLAGS/ecc/challenge-113-cryptohack-digestive/flag.txt]`, submitted via user API (+60, 159 solved)

## Statement (verbatim, from category page scrape)
---
--> Should ECDSA be avoided for better digestive health? Play at https://web.cryptohack.org/digestive -->
---

## One-line solution
py-ecdsa truncates the "digest" to the first 24 bytes on NIST192p, so every signature from
`/sign/` is on the fixed prefix `{"admin": false, "userna`; re-send any such signature on
`{"admin": false, "username": "x", "admin": true}` (same 24-byte prefix; duplicate JSON key,
last wins) to `/verify/`. See `AAR.md`.
