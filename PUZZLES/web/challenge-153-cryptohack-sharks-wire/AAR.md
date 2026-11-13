# AAR — Challenge 153: Sharks on the Wire

**Result:** **SOLVED + leaderboard-verified** (account NoBirdWasHam, 2026-10-13) — answer `15`
accepted via submit_flag.py. (Slug: `sharks-wire`.)
**Date:** 2026-10-13 (UTC)

## Source
- **Platform:** CryptoHack, Web category. Solution page NOT consulted (no-cheat rule).
- **Statement provenance:** category page card text (cached in remaining_descs.json).

## The flag
Recorded in `FLAGS/web/challenge-153-cryptohack-sharks-wire/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## How it was solved
1. Downloaded the challenge's `cryptohack.org.pcapng` (shared capture; also used by tls-handshake).
2. Parsed with scapy 2.8.0 (venv at `~\tools\crypto-ctf\venv`):
   `len([p for p in rdpcap(f) if IP in p and p[IP].dst == IP('178.62.74.206')])` → **15** of 51 IP packets.
3. Submitted `sharks-wire "15"` — accepted.

No writeup or external source consulted.

## Learning points
- The server IP (178.62.74.206) comes from the DNS A answer visible in the capture — read the
  challenge text, it names the destination explicitly.
- First challenge of the pcap series; establishes the "download file → parse with scapy → answer"
  loop used by the next several Web challenges.
- scapy in this build has **no TLS layer** (`from scapy.all import TLS` fails) — relevant to the
  follow-up challenges; later superseded by tshark (see `wireshark-tshark` skill).
## Vulnerability (plain words)
None — this is an observation-type challenge, not a crypto break. A capture of a real visit to cryptohack.org is handed to you and the question is simply how many packets went *to* the server. There is no secret to recover and no protocol weakness; the only skill tested is scoping the traffic correctly (which direction, which host) and counting.

## How the answer follows
1. The statement names the destination host; the DNS A answer inside the capture pins it to 178.62.74.206, so "packets sent to the server" becomes a well-defined filter rather than a guess.
2. The capture holds 51 IP packets; the filter `IP.dst == 178.62.74.206` leaves 15 — the client->server direction only. Counting both directions, or all traffic, gives different numbers, which is why the filter direction is the whole derivation.
3. Submitting `15` was accepted by the server, confirming the intended reading (client->server packet count).

## Limitations / attempts that failed
- No failed submission is recorded in run logs for this challenge.
- scapy 2.8.0 in the run venv exposes no TLS dissector (`from scapy.all import TLS` fails), so content-level reading of the streams was out of scope with that toolchain (tshark superseded it later — see `wireshark-tshark` skill).
- The per-packet breakdown of the 15 (handshake vs data) was not recorded; the count was validated only by server acceptance.

## Sources
- No third-party writeup or solution artifact consulted (source-disclosure rule).
- Tool reference only: Scapy packet-filter idioms (general tool documentation).
- Capture + statement from the CryptoHack Web category page (cached locally in site.md).
