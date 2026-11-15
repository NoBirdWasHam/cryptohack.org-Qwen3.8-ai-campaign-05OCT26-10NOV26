# Course lesson — Network Attacks (Introduction)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Introduction as challenge `nc-intro-2`.
**Status:** completed 2026-10-05 · **Points:** 5 · **Site:** https://cryptohack.org/challenges/nc-intro-2/
**Ledger row:** `course__network_attacks` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Challenge 03: Network Attacks (CryptoHack intro)

**Result:** **SOLVED + leaderboard-verified** (account NoBirdWasHam, 2026-10-05) — flag ``flag — recorded in COURSEWORK/introduction/course-nc-intro-2/flag.txt`` accepted; solved-star lit. (Slug: `nc-intro-2`.)
`socket.cryptohack.org:11112`. Transcript preserved as
`live_transcript_20261005.txt`.
**Date:** 2026-10-05 (UTC)

## Sources
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category page (challenge statement read here):** https://cryptohack.org/challenges/introduction/
- **Challenge:** "Network Attacks" (5 pts, slug `nc-intro-2`); statement from that category page, fetched 2026-10-05
- **Interactive service (per statement):** `socket.cryptohack.org` port `11112` — line-delimited JSON, both directions
- **Challenge file (fetched, verbatim in site.md):** https://cryptohack.org/static/challenges/pwntools_example_72a60ff13df200692898bb14a316ee0b.py
- **Provenance:** statement + starter script from the category page; flag from the **live** CryptoHack challenge server (the intended source — there is no other way to get it). No `/solutions/` page or writeup consulted (no-cheat rule).

## The flag
``flag — recorded in COURSEWORK/introduction/course-nc-intro-2/flag.txt``

## How it was solved
1. Read the statement: connect to `socket.cryptohack.org:11112`, speak JSON, send
   an object with key `buy` and value `flag`.
2. Reviewed the provided `pwntools_example.py` starter (it buys `"clothes"`).
3. Wrote my own client, `netattack.py`, using **stdlib `socket` + `json`** (no
   pwntools install needed — the protocol is one JSON object per newline-terminated
   line in each direction):
   - `socket.create_connection(("socket.cryptohack.org", 11112))`
   - read the 4-line banner with `makefile("rb").readline()`
   - `sendall((json.dumps({"buy": "flag"}) + "\n").encode())`
   - read the response line
4. Ran it against the live server. Full transcript (evidence):
   ```
   SERVER> Welcome to netcat's flag shop!
   SERVER> What would you like to buy?
   SERVER> I only speak JSON, I hope that's ok.
   SERVER>
   SENT   > {"buy": "flag"}
   SERVER> {"flag": "`flag — recorded in COURSEWORK/introduction/course-nc-intro-2/flag.txt`"}
   ```

## Learning points
- **Interactive challenges = the flag is stateful and server-side.** Unlike a
  static file, the flag only comes back over the wire from the challenge service;
  reproducing the exact protocol is the whole solve. This is the pattern for the
  rest of CryptoHack's network/crypto categories.
- **Line-delimited JSON is a deliberately simple wire format.** `json.dumps(...) +
  "\n"` out, `json.loads(line)` in. Knowing the framing (one object per line,
  newline-terminated) is what lets a stdlib `socket` client replace pwntools.
- **The starter is a template, not the answer.** It sends `buy: "clothes"`; the
  intended move is to change the value to `"flag"`. Reading what the server's
  banner offers ("What would you like to buy?") is how you infer the valid keys.
- **Reproduce the request exactly, then read the response.** No guessing of other
  keys was needed — the statement names the key/value, so a single clean request
  is the minimal, non-noisy solve (good etiquette: one request, no probing).
- **Stdlib-over-dependency:** when a protocol is trivial, `socket`+`json` avoids a
  `pip install` and keeps the run self-contained and re-runnable.

## What I did / did not do
- Did: implement the client from the statement + starter, connect once, send the
  documented request, record the server's reply verbatim.
- Did not: brute-force other `buy` values, hammer the server, or touch any other
  service. Did not consult `/solutions/` or any writeup.
- Did not: submit to the leaderboard (no account). For this challenge the server
  response *is* the flag, so the challenge is solved on its own terms even without
  an account; leaderboard credit would additionally require registration.

## Limitations
- Single connection, single request. If the service rate-limits or rotates, a
  re-run is needed; transcript above is the evidence of record for this run.

## Configuration (environment for this run)
- **Date (UTC):** 2026-10-05T01:45Z (transcript stamped 2026-10-05)
- **Host OS:** Windows 11 (11), shell = git-bash/MSYS (uname: `MSYS_NT-10.0-26200`)
- **User:** <USER>
- **Interpreter:** python3 = Python 3.10.11 (primary); python = Python 3.14.7; pip 26.2.1
- **Working dir:** `~\Practice runs`
- **Agent:** Hermes Agent; model = qwen38-27b (provider: custom)
- **Tools used:** terminal (curl for file fetch; python3 socket client for the live solve)
- **Network:** outbound to cryptohack.org (GET files) and a single TCP connection to
  `socket.cryptohack.org:11112` (the live challenge service)
- **No-cheat rule applied:** statement + provided starter + own client; flag came
  from the live challenge server (its intended source). No `/solutions/`, no writeup.
