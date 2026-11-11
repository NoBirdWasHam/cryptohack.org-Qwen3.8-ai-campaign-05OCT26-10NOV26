# Authentification 2 (Breizh CTF) — site notes

- Card: category ctf-archive, `data-challenge="authentification_2-breizh_ctf"`, 79 solves.
- Statement + hint: see statement.txt (gcm.py implementation error).
- Listener: `archive.cryptohack.org 59670` — plain HTTP Flask app (not JSON socket).
- Files (downloaded from live cryptohack.org `/static/challenges/`, hashes from card links):
  - authentification-2_532cbd2637be5e52034477b5059dc89b.zip -> authentification-2/ (app.py, crypto.py, gcm/)
  - template_authentification_4f2dc17a405786f94ecd03f7768eab0a.py

## Vulnerability (from provided source only)
gcm/gcm.py `encrypt()`/`decrypt()` call `gctr(J0, P)` instead of NIST's
`gctr(inc32(J0), P)`: the first data keystream block equals `E(J0)` — the very
block that masks the GHASH value into the tag (`T = S ⊕ E(J0)`).

Consequence with one known-plaintext token (we choose the username):
- `E(J0) = C[0:16] ⊕ P[0:16]`
- `S_obs = T ⊕ E(J0)` (exact GHASH output of our own ciphertext)
- `S = Σ Xᵢ·H^(m+1−i)` is a GF(2)-linear map of the unknown H (Frobenius
  squaring + multiplication by public constants ⇒ linearized polynomial
  `a·H⁸ + b·H⁴ + c·H² + d·H`). Recover H by 128×128 GF(2) linear algebra
  (one token; if the map is singular, brute the 2^k coset live).
- Forge `{"username": "admin", "role": "super_admin"}` using the known
  keystream prefix (long username ⇒ many known keystream blocks),
  `T' = GHASH_H(C') ⊕ E(J0)`. `verif_token` only checks role + tag ⇒ flag.
