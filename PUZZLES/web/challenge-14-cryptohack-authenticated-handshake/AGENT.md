---
record: agent-aar
puzzle: challenge-14-cryptohack-authenticated-handshake
category: web
url: https://cryptohack.org/challenges/authenticated-handshake/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/web/challenge-14-cryptohack-authenticated-handshake/flag.txt"
flag_sha256: 04f85165157cdb8cc66f79a2e4cef2cfbbb8bca304aedea555e76af0158100dc
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 161: Authenticated Handshake
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
RFC 8446 §4.4.4: `verify_data = HMAC(finished_key, Transcript-Hash(handshake_msgs))`.

1. **Keylog → finished_key.** From `keylogfile13.txt`:
   `CLIENT_HANDSHAKE_TRAFFIC_SECRET d8c7c79e… ca8fb945…`.
   `finished_key = HKDF-Expand-Label(client_handshake_traffic_secret, "finished", "", 48)` with
   SHA-384 (cipher suite 0x1302 = TLS_AES_256_GCM_SHA384). (This is exactly what the provided
   `client_finished.py` computes once you fill the blanks.)
2. **Transcript assembly** (messages, no record headers):
   - `ClientHello` (512B) + `ServerHello` (122B): plaintext, pulled from the pcap via the
     scapy stream parser (tshark's `-T fields` collapses multi-message frames; `-x` dumps only
     include *decrypted* blocks, so the plaintext CH/SH had to come from the raw capture).
   - `EncryptedExtensions` (19B) + `Certificate` (4037B) + `CertificateVerify` (264B) +
     server `Finished` (52B): from tshark's `Decrypted TLS (N bytes)` blocks
     (`-o tls.keylog_file:… -Y tls.handshake -x`), split on 4-byte handshake headers.
3. **Oracle validation before trusting the result:** recomputed the *server's* Finished
   verify_data = `HMAC(HKDF(SERVER_HANDSHAKE_TRAFFIC_SECRET,"finished","",48),
   SHA384(CH+SH+EE+Cert+CV))` → **exact match** with the capture's server verify_data. That
   proved the transcript was byte-perfect (any CH/SH offset or message-order error would have
   broken it).
4. **Client verify_data** = `HMAC(client_finished_key, SHA384(CH+SH+EE+Cert+CV+ServerFinished))`
   → submitted, accepted.

## reusable-rules
- **Validate the transcript with the one Finished you CAN check** (the server's) before
  computing the answer. A single wrong byte in CH/SH silently produces a plausible-but-wrong
  48-byte verify_data; the server-Finished match is a cheap, exact correctness check.
- **TLS 1.3 transcript subtlety:** the client's Finished transcript includes the *server's*
  Finished message (everything up to and including it), while the server's Finished transcript
  stops before its own message. (RFC 8446: the Finished message authenticates all handshake
  messages up to, but not including, itself.)
- **tshark `-T fields` flattens multi-message TLS frames** (types concatenated, e.g.
  `2,8,11,15,20`) — for per-message bytes use the `-x` `Decrypted TLS` blocks and split on the
  handshake header (`type(1) len(3)`), not the fields API.
- The provided skeleton (`client_finished.py`) is the intended path: it already implements
  `HKDF_expand_label` with the `tls13 ` prefix — you only supply the message hex strings.
  Reproducing its `verify_data` function in a scratch script is equivalent and faster to drive.
- NSS keylog → connection matching by client_random (same lesson as decrypting-tls13; the
  keylog files in this run are cross-named, so always match explicitly).

## anti-patterns / limits
- tshark `-T fields` flattens multi-message TLS frames (handshake types concatenated, e.g. `2,8,11,15,20`), losing per-message byte boundaries — unusable for transcript assembly; and `-x` dumps only *decrypted* blocks, so the plaintext ClientHello/ServerHello had to come from the raw capture via a scapy stream parser. Both constraints found during the run.
- Silent-failure hazard (acknowledged, mitigated rather than hit): a single wrong byte in CH/SH yields a plausible-but-wrong 48-byte digest with no error. The server-Finished oracle is the mitigation; no wrong submission was recorded in run logs.
- Keylog files in this run are cross-named between sibling challenges; matching by client_random (as in decrypting-tls13) was required before trusting `keylogfile13.txt`.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack, Web category. Solution page NOT consulted (no-cheat rule).
- **Statement provenance:** category page card text (cached in remaining_descs.json).
- **Provided files (in `_web_pcap/`):** `client_finished.py`, `keylogfile13.txt`,
  `no-finished-tls3.pcapng` (note: on-disk name lacks the `.cryptohack.org` middle segment).
