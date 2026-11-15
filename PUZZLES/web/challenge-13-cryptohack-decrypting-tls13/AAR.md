# AAR — Challenge 159: Decrypting TLS 1.3

**Result:** **SOLVED + leaderboard-verified** (account NoBirdWasHam, 2026-10-13) — flag
`[flag — recorded in FLAGS/web/challenge-13-cryptohack-decrypting-tls13/flag.txt]` accepted via submit_flag.py; score 6500→6535, solved 141→142.
(Slug: `decrypting-tls13`.)
**Date:** 2026-10-13 (UTC)

## Source
- **Platform:** CryptoHack, Web category. Solution page NOT consulted (no-cheat rule).
- **Statement provenance:** category page card text (cached in remaining_descs.json).
- **Provided files (in `_web_pcap/`):** `tls3.cryptohack.org.pcapng`, `keylogfile12.txt`,
  `keylogfile13.txt`, `no-finished-tls3.pcapng`, `client_finished.py`.

## The flag
Recorded in `FLAGS/web/challenge-13-cryptohack-decrypting-tls13/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## How it was solved
Intended path (and what worked, 3 commands):
1. **Match the keylog to the capture by client_random.** NSS keylog lines start with the
   client_random; tshark reads it directly:
   `tshark -r tls3.cryptohack.org.pcapng -Y "tls.handshake.type==1" -T fields -e tls.handshake.random`
   → `210cb7af9f5da56460d21cda98cda0ac82b979e15979482182e037cf42f663c6`
   → matches the lines in `keylogfile12.txt` (the file *named* like it belongs to the TLS 1.2
   challenge). `keylogfile13.txt` (client_random `d8c7c79e…`) belongs to
   `no-finished-tls3.pcapng` instead — the challenge files are misnamed/cross-loaded on the server.
2. Decrypted with tshark's keylog support:
   ```
   tshark -r tls3.cryptohack.org.pcapng \
     -o "tls.keylog_file:…\keylogfile12.txt" \
     -o 'tls.desegment_ssl_records:TRUE' -o 'tls.desegment_ssl_application_data:TRUE' \
     -Y http2 -x
   ```
3. Read the flag from the 43-byte `Decrypted TLS` block (HTTP/2 DATA frame, stream 1).

No writeup or external source consulted.

## Learning points
- **Always match NSS keylog → capture by the client_random column** before decrypting. A
  keylog from the *wrong connection* silently produces zero decrypted records (tshark shows no
  error). Here the files were cross-named, so the "obvious" `keylogfile13.txt` would have
  produced nothing for `tls3.cryptohack.org.pcapng`.
- The `client_finished.py` helper in the download set belongs to a *different* sub-challenge:
  `no-finished-tls3.pcapng` is a capture **missing the client's Finished**, and the script
  recomputes it (`HKDF_expand_label(client_handshake_traffic_secret, b"finished", …)` over the
  transcript) — a TLS 1.3 Finished-verification exercise. Not needed for this flag.
- TLS 1.3 keylog decryption in tshark: `-o tls.keylog_file:<path>` (absolute Windows paths work
  fine here, unlike the `uat:rsa_keys` UAT which preferred a relative path).
- The flag itself is the lesson: exporting `SSLKEYLOGFILE` for debugging hands an attacker the
  master secrets — the exact "forward secrecy" trade-off the statement sets up.

## Files
- `_h2_tls3.txt` — the decrypted `-x` dump used to extract the flag.
## Vulnerability (plain words)
Not a break of TLS 1.3 — an operator-error scenario. The challenge hands over a recorded session AND a `SSLKEYLOGFILE` debug export. TLS's forward-secrecy guarantees protect past traffic only against a later key leak; they do nothing against someone who holds this session's traffic secrets, which the keylog file is. With those secrets, decryption is just re-deriving the key schedule — no attack on the cipher, just possession of the keys.

## How the answer follows
1. NSS keylog lines are keyed by the connection's client_random, and the ClientHello is plaintext — so the correct keylog for a capture is found by a pure equality check, not trial and error: capture ClientHello random `210cb7af...` equals the lines in `keylogfile12.txt`. (The files are cross-named on the server; the "obvious" `keylogfile13.txt` belongs to the other capture.)
2. With the matching secrets, tshark re-derives the TLS 1.3 read keys and decrypts; the HTTP/2 DATA frame on stream 1 is plaintext `Flag: [flag — recorded in FLAGS/web/challenge-13-cryptohack-decrypting-tls13/flag.txt]`.
3. Flag accepted with a real score delta (6500->6535), so the decrypted bytes — not a guess — were submitted.

## Limitations / attempts that failed
- Documented trap (verified by client_random matching, not by a failed submission): decrypting with the WRONG keylog file yields zero decrypted records and NO error from tshark — a silent empty result. Whether keylogfile13 was physically tried first is not recorded in run logs.
- The provided `client_finished.py` belongs to the sibling `no-finished-tls3.pcapng` sub-challenge and was not needed for this flag (identified, then set aside).
- tshark RSA-key UAT preferred relative paths while `tls.keylog_file` accepted absolute Windows paths — an interface inconsistency noted during the run.

## Sources
- Provided challenge files: `tls3.cryptohack.org.pcapng`, `keylogfile12.txt`, `keylogfile13.txt`, `no-finished-tls3.pcapng`, `client_finished.py` (in `_web_pcap/`).
- Public specs (about TLS itself): RFC 8446 sec. 7.1/7.5 (key schedule), NSS keylog file format.
- No third-party writeup or solution artifact consulted (source-disclosure rule).
