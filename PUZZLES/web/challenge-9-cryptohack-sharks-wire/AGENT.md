---
record: agent-aar
puzzle: challenge-9-cryptohack-sharks-wire
category: web
url: https://cryptohack.org/challenges/sharks-wire/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/web/challenge-9-cryptohack-sharks-wire/flag.txt"
flag_sha256: 238903180cc104ec2c5d8b3f20c5bc61b389ec0a967df8cc208cdc7cd454174f
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 153: Sharks on the Wire
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
1. Downloaded the challenge's `cryptohack.org.pcapng` (shared capture; also used by tls-handshake).
2. Parsed with scapy 2.8.0 (venv at `~\tools\crypto-ctf\venv`):
   `len([p for p in rdpcap(f) if IP in p and p[IP].dst == IP('178.62.74.206')])` → **15** of 51 IP packets.
3. Submitted `sharks-wire "15"` — accepted.

No writeup or external source consulted.

## reusable-rules
- The server IP (178.62.74.206) comes from the DNS A answer visible in the capture — read the
  challenge text, it names the destination explicitly.
- First challenge of the pcap series; establishes the "download file → parse with scapy → answer"
  loop used by the next several Web challenges.
- scapy in this build has **no TLS layer** (`from scapy.all import TLS` fails) — relevant to the
  follow-up challenges; later superseded by tshark (see `wireshark-tshark` skill).

## anti-patterns / limits
- No failed submission is recorded in run logs for this challenge.
- scapy 2.8.0 in the run venv exposes no TLS dissector (`from scapy.all import TLS` fails), so content-level reading of the streams was out of scope with that toolchain (tshark superseded it later — see `wireshark-tshark` skill).
- The per-packet breakdown of the 15 (handshake vs data) was not recorded; the count was validated only by server acceptance.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack, Web category. Solution page NOT consulted (no-cheat rule).
- **Statement provenance:** category page card text (cached in remaining_descs.json).
