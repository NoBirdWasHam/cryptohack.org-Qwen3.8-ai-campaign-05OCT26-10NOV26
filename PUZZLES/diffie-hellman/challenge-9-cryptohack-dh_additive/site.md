# CryptoHack — dh_additive (70 pts)

- **Platform:** CryptoHack (cryptohack.org), category: Diffie-Hellman
- **Challenge name:** dh_additive
- **Slug:** `dh_additive`
- **Points:** 70
- **Folder:** challenge-124-cryptohack-dh_additive
- **Account:** NoBirdWasHam
- **Status:** SOLVED 2026-10-15 (flag submitted, score_delta +70)

## Verbatim statement

> Alice and Bob decided to do their DHKE in an additive group rather than a multiplicative group. What could go wrong? Use the script from "Deriving Symmetric Keys" to decrypt the flag once you've recovered the shared secret. Connect at socket.cryptohack.org 13380

## Service

- `socket.cryptohack.org` port **13380**
- Passive: on connect the server prints three lines (new per connection):
  - `Intercepted from Alice: {"p": "0x...", "g": "0x02", "A": "0x..."}`
  - `Intercepted from Bob: {"B": "0x..."}`
  - `Intercepted from Alice: {"iv": "...", "encrypted": "..."}`
- No input accepted; nothing to send.

## Files

None provided for this challenge (socket only). The decryption script referenced
("Deriving Symmetric Keys") is the `decrypt_provided.py` from
`challenge-75-cryptohack-dh-starter-5/` (key = SHA1(str(shared_secret))[:16], AES-128-CBC).
