# Decrypting TLS 1.2 (decrypting-tls12)
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category:** Web (https://cryptohack.org/challenges/web/)
- **Name / points:** Decrypting TLS 1.2 / 30 pts
- **Slug:** `decrypting-tls12` (folder `challenge-158-cryptohack-decrypting-tls12`)
- **Status:** SOLVED 2026-10-13

## Statement (abridged from category page scrape, full text in remaining_descs.json)
TLS 1.2 RSA key exchange walkthrough. Attached PCAP `tls2.cryptohack.org.pcapng` of a TLS 1.2
connection to tls2.cryptohack.org. The connection used **TLS_RSA_WITH_AES_256_GCM_SHA384**
(AES256-GCM-SHA384 in OpenSSL format), RSA for key exchange. You've "hacked" the server and
obtained the certificate's RSA private key. Use it to decrypt the TLS connection and find the
flag in the **HTTP/2** stream. The statement points to Wireshark's "TLS Decrypt" dialogue.

## Provided files
- `tls2.cryptohack.org.pcapng` — the capture
- `privkey.pem` — the server RSA private key (2048-bit, PKCS#8 `PRIVATE KEY` header)

## Answer
`crypto{weaknesses_of_non_ephemeral_key_exchange}` — verified accepted via submit_flag.py
(2026-10-13, score 6470→6500, 140→141).
