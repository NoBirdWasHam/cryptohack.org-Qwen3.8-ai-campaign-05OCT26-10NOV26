---
record: agent-aar
puzzle: challenge-154-cryptohack-tls-handshake
category: web
url: https://cryptohack.org/challenges/tls-handshake/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/web/challenge-10-cryptohack-tls-handshake/flag.txt"
flag_sha256: 23350c9ffd9cc7f7efccbc35a85a3de8e362e4dfa452ab3ff709436b8c25b926
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 154: TLS Handshake
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
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

## reusable-rules
- **ServerHello field layout:** `type(1) len(3) version(2) random(32) session_id(1+len) …` —
  the random starts at offset 6 of the handshake body, not 4 (the version bytes are easy to
  include by mistake).
- This capture has **8-byte non-TLS prefixes** and **6-byte zero segments** that corrupt naive
  record-walk stream assembly; filter `pl==b'\x00'*len(pl) or len(pl)<5`.
- A wrong-but-plausible flag returning delta 0 is the standard signal: re-derive the exact bytes,
  don't resubmit variations.
- Superseded workflow: all subsequent TLS work in this run used tshark instead (see
  `wireshark-tshark` skill) — hand-parsing is only needed when the capture has no tool support.

## anti-patterns / limits
- First submission was WRONG (off-by-2: the slice started at offset 4 and swallowed part of the version field) -> score delta 0; corrected and resubmitted.
- Naive stream assembly failed on this capture: 8-byte non-TLS prefixes and 6-byte all-zero segments corrupt a record-walk that doesn't filter them; required `pl == b'\x00'*len(pl)` / short-payload filtering.
- Workflow limitation: hand-parsing was superseded by tshark for all later TLS challenges in this run.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack, Web category. Solution page NOT consulted (no-cheat rule).
- **Statement provenance:** category page card text (cached in remaining_descs.json).
