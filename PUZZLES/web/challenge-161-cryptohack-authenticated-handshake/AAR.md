# AAR — Challenge 161: Authenticated Handshake

**Result:** **SOLVED + leaderboard-verified** (account NoBirdWasHam, 2026-10-13) —
client Finished verify_data accepted via submit_flag.py; score 6535→6575, solved 142→143.
(Slug: `authenticated-handshake`.)
**Date:** 2026-10-13 (UTC)

## Source
- **Platform:** CryptoHack, Web category. Solution page NOT consulted (no-cheat rule).
- **Statement provenance:** category page card text (cached in remaining_descs.json).
- **Provided files (in `_web_pcap/`):** `client_finished.py`, `keylogfile13.txt`,
  `no-finished-tls3.pcapng` (note: on-disk name lacks the `.cryptohack.org` middle segment).

## The flag
`b51d7b5fb12aa3d692140d8f1f80732610e99411ca0f6d928b0f60570cbc778e672457a729d7cf3b58bc174f00dc5d30`
(48-byte client Finished verify_data, hex — the answer format for this challenge.)

## How it was solved
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

## Learning points
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
## Vulnerability (plain words)
No cryptanalytic vulnerability — this is a guided re-implementation exercise on given material. The capture is missing the client's Finished message, but the keylog file supplies the client handshake traffic secret; TLS 1.3's Finished is then *computable*, not crackable: `verify_data = HMAC(finished_key, Transcript-Hash(handshake))` with `finished_key = HKDF-Expand-Label(client_handshake_traffic_secret, "finished", "", 48)`. The exercise is proving you can reproduce the exact byte transcript the hash covers.

## How the answer follows
1. From `keylogfile13.txt` take CLIENT_HANDSHAKE_TRAFFIC_SECRET (matched to the capture by client_random), derive finished_key with HKDF-Expand-Label under SHA-384 (suite 0x1302 = TLS_AES_256_GCM_SHA384).
2. Assemble the transcript byte-exactly: ClientHello + ServerHello (plaintext, from the raw capture — tshark's decrypted blocks only cover post-ServerHello traffic) then EncryptedExtensions, Certificate, CertificateVerify, server Finished (split out of tshark `Decrypted TLS` blocks on `type(1) len(3)` headers).
3. Before trusting anything, validate the pipeline against the ONE value that can be checked: recompute the *server's* Finished verify_data and confirm an exact match with the capture. That proves the transcript is byte-perfect (the server's transcript stops before its own Finished; the client's includes it — the one-ordering subtlety in RFC 8446 sec. 4.4.4).
4. Client verify_data = HMAC over SHA-384 of the transcript including the server Finished -> 48-byte hex answer, accepted with a real score delta (6535->6575).

## Limitations / attempts that failed
- tshark `-T fields` flattens multi-message TLS frames (handshake types concatenated, e.g. `2,8,11,15,20`), losing per-message byte boundaries — unusable for transcript assembly; and `-x` dumps only *decrypted* blocks, so the plaintext ClientHello/ServerHello had to come from the raw capture via a scapy stream parser. Both constraints found during the run.
- Silent-failure hazard (acknowledged, mitigated rather than hit): a single wrong byte in CH/SH yields a plausible-but-wrong 48-byte digest with no error. The server-Finished oracle is the mitigation; no wrong submission was recorded in run logs.
- Keylog files in this run are cross-named between sibling challenges; matching by client_random (as in decrypting-tls13) was required before trusting `keylogfile13.txt`.

## Sources
- Public spec (about TLS itself): RFC 8446 sec. 4.4.4 (Finished), sec. 7.1 (HKDF-Expand-Label, `tls13 ` label prefix), sec. 7.5 (traffic secrets).
- Challenge-provided skeleton `client_finished.py` (challenge material, not a third-party solution).
- No third-party writeup or solution artifact consulted (source-disclosure rule).
