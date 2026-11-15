# AAR — Challenge 154: TLS Handshake

**Result:** **SOLVED + leaderboard-verified** (account NoBirdWasHam, 2026-10-13) —
ServerHello random accepted via submit_flag.py. (Slug: `tls-handshake`.)
**Date:** 2026-10-13 (UTC)

## Source
- **Platform:** CryptoHack, Web category. Solution page NOT consulted (no-cheat rule).
- **Statement provenance:** category page card text (cached in remaining_descs.json).

## The flag
Recorded in `FLAGS/web/challenge-10-cryptohack-tls-handshake/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## How it was solved
1. Same capture as sharks-wire: `cryptohack.org.pcapng`.
2. scapy in this build has **no TLS layer**, so TLS records were hand-parsed from TCP payloads:
   reassemble the client→server and server→client byte streams (skip non-TLS prefixes and
   6-byte zero segments), walk 5-byte record headers (content type 20-23), and split
   concatenated handshake messages inside content-type-22 records.
3. ServerHello = first type-22 record from the server stream with handshake type 2;
   its random is bytes [6:38] of the handshake message body (after type + 3-byte length + 2-byte
   version). → `67c6bf8f…`
4. **First attempt submitted a wrong extraction** (`bf8ffd…`, off by 2 bytes — included part of
   the version field) → delta 0. Corrected the offset, resubmitted → accepted.

No writeup or external source consulted.

## Learning points
- **ServerHello field layout:** `type(1) len(3) version(2) random(32) session_id(1+len) …` —
  the random starts at offset 6 of the handshake body, not 4 (the version bytes are easy to
  include by mistake).
- This capture has **8-byte non-TLS prefixes** and **6-byte zero segments** that corrupt naive
  record-walk stream assembly; filter `pl==b'\x00'*len(pl) or len(pl)<5`.
- A wrong-but-plausible flag returning delta 0 is the standard signal: re-derive the exact bytes,
  don't resubmit variations.
- Superseded workflow: all subsequent TLS work in this run used tshark instead (see
  `wireshark-tshark` skill) — hand-parsing is only needed when the capture has no tool support.
## Vulnerability (plain words)
None — observation-type. The TLS handshake is unauthenticated plaintext by design: anyone holding the capture can read the ServerHello fields (version, random, chosen suite). The ServerHello random is not a secret — it is echoed in the clear as handshake entropy. What the challenge actually tests is whether you can locate a field in the real byte layout of a messy capture, not whether you can break TLS.

## How the answer follows
1. The answer is a defined byte range: the ServerHello handshake body is `type(1)=2 | length(3) | version(2) | random(32) | ...`, so the random is exactly bytes [6:38] of the message body. The derivation is bookkeeping: find the first content-type-22 record on the server->client stream whose handshake type is 2, then slice 32 bytes from offset 6.
2. Hand-parsing was necessary because this scapy build has no TLS dissector: reassemble the TCP streams, walk 5-byte record headers (content types 20-23), and split concatenated handshake messages inside type-22 records.
3. Server acceptance pins the slice: the earlier off-by-2 extraction (`bf8ffd...`, version bytes included) was rejected with delta 0, and the corrected `67c6bf8f...` was accepted — i.e. acceptance itself verifies the offset derivation.

## Limitations / attempts that failed
- First submission was WRONG (off-by-2: the slice started at offset 4 and swallowed part of the version field) -> score delta 0; corrected and resubmitted.
- Naive stream assembly failed on this capture: 8-byte non-TLS prefixes and 6-byte all-zero segments corrupt a record-walk that doesn't filter them; required `pl == b'\x00'*len(pl)` / short-payload filtering.
- Workflow limitation: hand-parsing was superseded by tshark for all later TLS challenges in this run.

## Sources
- Format references (public specs about TLS itself, not about this challenge): RFC 5246 sec. 6.2 (record layer) and sec. 7.4.1.2 (ServerHello layout).
- No third-party writeup or solution artifact consulted (source-disclosure rule); Scapy tool docs only.
