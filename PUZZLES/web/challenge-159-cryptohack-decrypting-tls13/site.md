# Decrypting TLS 1.3 (decrypting-tls13)
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category:** Web (https://cryptohack.org/challenges/web/)
- **Name / points:** Decrypting TLS 1.3 / 35 pts
- **Slug:** `decrypting-tls13` (folder `challenge-159-cryptohack-decrypting-tls13`)
- **Status:** SOLVED 2026-10-13

## Statement (abridged)
TLS 1.3 uses Ephemeral Diffie-Hellman for forward secrecy (long-term RSA keys only
authenticate the handshake). To decrypt TLS 1.3 you need the DH parameters the client used,
exported via `SSLKEYLOGFILE`. Attached: `tls3.cryptohack.org.pcapng` + `keylogfile.txt`
(NSS key log format). Decrypt the traffic and find the flag in the HTTP/2 stream.
Resources: Wireshark TLS Decryption, NSS Key Log Format.

## Provided files
- `tls3.cryptohack.org.pcapng` — TLS 1.3 capture of a curl connection to tls3.cryptohack.org
- `keylogfile.txt` — NSS key log (the challenge's "keylogfile.txt"; the files on the server are
  misnamed — see AAR)

## Answer
`[flag — recorded in FLAGS/web/challenge-159-cryptohack-decrypting-tls13/flag.txt]` — in the HTTP/2 `DATA[1]` frame: `Flag: [flag — recorded in FLAGS/web/challenge-159-cryptohack-decrypting-tls13/flag.txt]`.
Verified accepted via submit_flag.py (2026-10-13, score 6500→6535, 141→142).
