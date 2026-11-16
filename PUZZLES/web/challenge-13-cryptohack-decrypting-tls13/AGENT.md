---
record: agent-aar
puzzle: challenge-13-cryptohack-decrypting-tls13
category: web
url: https://cryptohack.org/challenges/decrypting-tls13/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/web/challenge-13-cryptohack-decrypting-tls13/flag.txt"
flag_sha256: 0d1babb9015b422c0da3eb21953753486c55bb0fba1b52388377e2efa03cc34a
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 159: Decrypting TLS 1.3
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
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

## reusable-rules
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

## anti-patterns / limits
- Documented trap (verified by client_random matching, not by a failed submission): decrypting with the WRONG keylog file yields zero decrypted records and NO error from tshark — a silent empty result. Whether keylogfile13 was physically tried first is not recorded in run logs.
- The provided `client_finished.py` belongs to the sibling `no-finished-tls3.pcapng` sub-challenge and was not needed for this flag (identified, then set aside).
- tshark RSA-key UAT preferred relative paths while `tls.keylog_file` accepted absolute Windows paths — an interface inconsistency noted during the run.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack, Web category. Solution page NOT consulted (no-cheat rule).
- **Statement provenance:** category page card text (cached in remaining_descs.json).
- **Provided files (in `_web_pcap/`):** `tls3.cryptohack.org.pcapng`, `keylogfile12.txt`,
  `keylogfile13.txt`, `no-finished-tls3.pcapng`, `client_finished.py`.
