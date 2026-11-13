# TLS Handshake (tls-handshake)
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category:** Web (https://cryptohack.org/challenges/web/)
- **Name / points:** TLS Handshake / 15 pts
- **Slug:** `tls-handshake` (folder `challenge-154-cryptohack-tls-handshake`)
- **Status:** SOLVED 2026-10-13

## Statement (abridged)
Uses the same capture as Sharks on the Wire. Asks for the **ServerHello random** from the
TLS handshake in the capture (the 32-byte random the server sends back).

## Provided files
- `cryptohack.org.pcapng` (shared with sharks-wire).

## Answer
`[flag — recorded in FLAGS/web/challenge-154-cryptohack-tls-handshake/flag.txt]` — the ServerHello random,
extracted by hand-parsing TLS records from the TCP payloads (this build of scapy has no TLS
layer). Verified accepted via submit_flag.py (2026-10-13).
