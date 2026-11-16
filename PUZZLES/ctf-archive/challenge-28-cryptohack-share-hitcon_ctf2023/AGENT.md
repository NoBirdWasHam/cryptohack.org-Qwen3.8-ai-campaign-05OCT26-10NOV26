---
record: agent-aar
puzzle: challenge-28-cryptohack-share-hitcon_ctf2023
category: ctf-archive
url: https://cryptohack.org/challenges/share-hitcon_ctf2023/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-28-cryptohack-share-hitcon_ctf2023/flag.txt"
flag_sha256: 644d4537e6e2129754372e9d95bc69e55b2fa94e3fe354ccfd5193497bdc3203
skills: []
human_twin: AAR.md
---

# AGENT — share-hitcon_ctf2023 (CryptoHack ctf-archive) — SOLVED
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
The server builds its Shamir polynomial with PyCryptodome's `getRandomRange(0, p-1)`, which actually draws from **[0, p-2]** — so a random coefficient a_1..a_{n-1} can *never* equal p−1 mod p. Every share set therefore carries a tiny fingerprint (~1/p per coefficient). Ask many small primes for it, and a negligible range bug accumulates into the 256-bit secret.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- v1 (solve.py): [flag — recorded in FLAGS/post-quantum/challenge-9-cryptohack-lwe-intro/flag.txt] per candidate — O(p⁴), unusable.
- Two "wrong secret" red herrings were pure protocol traps while the math was already right: (a) signal.alarm(30) is total wall time per connection, so input must be sent in sync with reads; (b) the server reads p *and* n before comparing, so exit must be `4\n4\n<secret>\n` — a single `4\n` swallows the secret line as n.
- Environment: Windows `python` (3.14) lacks PyCryptodome → use python3 3.10 (Crypto 3.24); a stray local listener needed Stop-Process.

## artifacts [OBSERVED]
- code: _local_server.py, _server_local.py, solve.py, solve2.py
- data/logs: _live2.log, _live3.log, _live4.log, _local.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided server.py + live listener; the PyCryptodome getRandomRange off-by-one semantics were confirmed against the local replica. Flag came from the live service (`_live4.log`) after our own derivation. No external writeups or solutions pages consulted; Shamir interpolation/Lagrange algebra is textbook.
