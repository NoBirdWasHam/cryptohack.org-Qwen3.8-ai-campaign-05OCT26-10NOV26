---
record: agent-aar
puzzle: challenge-132-cryptohack-oracular_spectacular
category: aes
url: https://cryptohack.org/challenges/oracular_spectacular/
status: solved
date: 2026-10-24
flag_ref: "FLAGS/aes/challenge-25-cryptohack-oracular_spectacular/flag.txt"
flag_sha256: eee0f7e647cc3a75c49492c549a354220e2259ed155309285ffd6ff7aefa6d11
skills: []
human_twin: AAR.md
---

# AGENT — <!-- UPDATED by solver session 2026-10-24 (replaces backfill_docs.py stub) -->
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability / oracle model" [OBSERVED text; evidence tag applies to its source, not each claim]
- `message = urandom(16).hex()` → 32 ASCII hex chars = exactly 2 AES-CBC blocks,
  **encrypted without padding** (the real plaintext has no valid padding).
- `unpad` option: decrypts an attacker-chosen `iv||ct` and returns
  `{"result": good XOR (rng.random() > 0.4)}` — the oracle **lies with probability 0.6**
  (P(True|valid)=0.4, P(True|invalid)=0.6). Verified live: 200 known-invalid probes gave
  frac_true ≈ 0.635/0.535.
- Budget: 12 000 unpad queries per connection; `check` returns the flag iff the full
  32-char message is guessed (wrong guess just ends the session → reconnect).

## reusable-rules
- A lying oracle is just a noisy channel: repeat each test and let an LLR walk separate
  good from bad; the hex charset cuts candidates 256→16, which is the whole budget story.
- CBC padding-oracle byte control comes from XORing the **previous** block — XORing the
  block being decrypted scrambles it (avalanche). (Caught by local stub testing; the
  wrong variant showed frac_true≈0.6 for the *true* candidate.)
- `message` is the hex **string** itself — don't double-encode when calling `check`.
- Greedy best-arm policies have heavy tails under small gaps (0.4 vs 0.6); prefer
  adaptive budgets over fixed per-arm caps.
- The old `probe_flip_log.txt` (frac_true=1.0000) was a counting bug: it counted
  responses containing `"result"`, not `True` results. Live rate is 0.6 for invalid.

## anti-patterns / limits
- Per-attempt failure ~14% by design (Monte-Carlo); remedy is reconnect+retry, not a
  better per-byte rule. One local attempt failed post-tuning, as expected.
- Strategy is Monte-Carlo-tuned, not provably optimal; the capacity bound leaves ~2.7x
  headroom for a smarter scheme.
- Live flip rate measured 0.535–0.635 over 400 probes — consistent with 0.6 within
  sampling noise; the strategy tolerates small deviations.

## artifacts [OBSERVED]
- code: 13423.py, client.py, dbg1.py, probe3.py, probe_flip.py, probe_flip2.py, solve.py
- data/logs: flag_oracular_spectacular.txt, live_log.txt, probe_flip_log.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Challenge:** "Oracular Spectacular" (150 pts, slug `oracular_spectacular`), AES category
- **Server source:** `13423.py` (provided), listener `socket.cryptohack.org:13423`
- **NOT consulted:** `/solutions/`, third-party writeups (no-cheat rule). No external
  references used; strategy tuned via offline Monte-Carlo simulation only.
