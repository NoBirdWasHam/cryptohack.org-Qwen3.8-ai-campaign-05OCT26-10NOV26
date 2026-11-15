# Sharks on the Wire (sharks-wire)
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category:** Web (https://cryptohack.org/challenges/web/)
- **Name / points:** Sharks on the Wire / 10 pts
- **Slug:** `sharks-wire` (folder `challenge-153-cryptohack-sharks-wire`)
- **Status:** SOLVED 2026-10-13

## Statement (abridged)
A packet capture of browsing cryptohack.org is attached (`cryptohack.org.pcapng`).
The challenge walks through what a capture contains (DNS, Safe Browsing, TCP handshake,
TLS ClientHello) and asks how many IP packets were sent to the server.

## Provided files
- `cryptohack.org.pcapng` — shared with the tls-handshake challenge.

## Answer
`15` — count of IP packets with destination 178.62.74.206 (the cryptohack.org server IP),
out of 51 total IP packets. Verified accepted via submit_flag.py (2026-10-13).
