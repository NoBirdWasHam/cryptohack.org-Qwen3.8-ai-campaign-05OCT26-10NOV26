# Authenticated Handshake (authenticated-handshake)
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category:** Web (https://cryptohack.org/challenges/web/)
- **Name / points:** Authenticated Handshake / 40 pts
- **Slug:** `authenticated-handshake` (folder `challenge-161-cryptohack-authenticated-handshake`)
- **Status:** SOLVED 2026-10-13

## Statement (abridged)
TLS 1.3 authentication in three messages: Certificate, CertificateVerify, Finished.
`verify_data = HMAC(finished_key, Transcript-Hash(Handshake Context, Certificate*,
CertificateVerify*))`. `finished_key` = HKDF-expand of the `CLIENT_HANDSHAKE_TRAFFIC_SECRET`
with label `"tls13 finished"`. The PCAP contains the connection **up to** the client's
ChangeCipherSpec — the client Finished is missing. Fill in `client_finished.py` to compute the
client Finished `verify_data` and submit it.

## Provided files
- `client_finished.py` — skeleton with `HKDF_expand`, `HKDF_expand_label`, `verify_data` helpers
- `keylogfile13.txt` — NSS key log (client_random `d8c7c79e…`, matches `no-finished-tls3.pcapng`)
- `no-finished-tls3.pcapng` — TLS 1.3 capture (TLS_AES_256_GCM_SHA384 / 0x1302)

## Answer
`[flag — recorded in FLAGS/web/challenge-14-cryptohack-authenticated-handshake/flag.txt]`
Verified accepted via submit_flag.py (2026-10-13, score 6535→6575, 142→143).
