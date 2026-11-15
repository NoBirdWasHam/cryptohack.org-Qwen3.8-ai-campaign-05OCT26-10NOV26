# AAR — Long Story Short (long_story_short, 60 pts, Hashes)

## Result
SOLVED 2026-10-16. Flag: `[flag — recorded in FLAGS/hashes/challenge-9-cryptohack-long_story_short/flag.txt]`
Submitted via user API (submit_flag.py) during the hashes-list session; accepted.

## Attack
PBKDF2-HMAC-SHA256 vault (socket 13434, salt `bluerock-vault-2026`, 200000 iterations). The
passphrase is 128 bytes — LONGER than the SHA-256 HMAC block size (64 bytes). Per RFC 2104,
an HMAC key longer than the block size is first replaced by `H(key)` — here `H = SHA-256`.
So inside every HMAC call the effective key is `SHA-256(passphrase)`, which is EXACTLY the
fingerprint the server publishes. Sending `passphrase_hex = fingerprint` (32 bytes) makes the
server derive the identical PBKDF2 key and the vault opens. The key can also be computed
locally to verify the reasoning before connecting.

## Verification
- `solve.py` connects to socket.cryptohack.org:13434, sends the fingerprint as passphrase,
  and the server returns the flag.
- Server-accepted flag string archived in `flag.txt`.

## Lessons
- An HMAC key longer than the block size is silently hashed — if that hash is published
  (as a "fingerprint"), it IS the effective HMAC key.

## Evidence
- `13434.py` (provided server), `solve.py`, `flag.txt`

## Vulnerability (plain words)
The vault checks a 128-byte passphrase with HMAC-SHA256 (inside PBKDF2). HMAC silently replaces any key longer than the 64-byte block size by its own hash — so the effective key inside every HMAC call is SHA-256(passphrase), and the server publishes exactly that value as a "fingerprint". The vault publishes the very thing it authenticates with.

## How the answer follows
1. RFC 2104 key-shortening rule ⇒ HMAC(key = passphrase) ≡ HMAC(key = SHA-256(passphrase)) whenever len > 64.
2. The published fingerprint IS SHA-256(passphrase); sending it (32 bytes, hex) makes the server derive the identical PBKDF2-HMAC-SHA256 key (salt `bluerock-vault-2026`, 200000 iters) ⇒ vault opens ⇒ server returns `[flag — recorded in FLAGS/hashes/challenge-9-cryptohack-long_story_short/flag.txt]`.
3. The same computation was reproduced locally to confirm the reasoning before connecting; server-accepted flag archived in `flag.txt`.

## Limitations / attempts that failed
- Single-shot solve; no failed attempts recorded in run logs.

## Sources
Provided server source `13434.py` + live socket 13434. Standard referenced: RFC 2104 (HMAC key-length rule, cited in the original AAR). No writeups/solutions consulted.
