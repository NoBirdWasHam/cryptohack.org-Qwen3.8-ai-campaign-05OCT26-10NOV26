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
`67c6bf8ffd3364f8e5f3226e073409b331a2a555809f0d917d4324743c95c95c` — the ServerHello random,
extracted by hand-parsing TLS records from the TCP payloads (this build of scapy has no TLS
layer). Verified accepted via submit_flag.py (2026-10-13).
