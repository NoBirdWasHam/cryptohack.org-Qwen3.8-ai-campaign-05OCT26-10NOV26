---
record: agent-aar
puzzle: challenge-110-cryptohack-lets_decrypt_2
category: rsa
url: https://cryptohack.org/challenges/lets_decrypt_2/
status: solved
date: 2026-10-23
flag_ref: "FLAGS/rsa/challenge-110-cryptohack-lets_decrypt_2/flag.txt (absent: FLAG-PLACEHOLDER-REMOVED: only a masked placeholder existed;…)"
flag_sha256: null — flag withheld (note in FLAGS/INDEX.jsonl)
skills: []
human_twin: AAR.md
---

# AGENT — 110-cryptohack-lets_decrypt_2: Let's Decrypt Again (CryptoHack, 175 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
The server verifies `pow(SIGNATURE, e, n) == PKCS1v15-digest(msg)` with **attacker-chosen
`n` (set_pubkey, before the random suffix is generated) and attacker-chosen `e` (per
claim, AFTER the suffix is revealed)**. The check is exact integer equality, so the
attacker just needs `SIGNATURE^e mod n` to land on a digest of their choosing. The
server's own `N, E, D` are irrelevant — the attacker's `(e, n)` replaces the real pubkey.

## reusable-rules
- Attacker-chosen modulus + exponent ⇒ move the DLP into a group you designed: a prime-power
  modulus gives a cyclic smooth-order group; membership in `<g>` is one `pow`, PH gives `e`.
- Order of operations matters: `e` is chosen after the nonce, `n` before — so `n` must be
  nonce-independent (a pure prime power) while `e` carries the nonce dependence.
- Fingerprint the padding format from the live oracle (`SIG^E mod N` reveals the digest)
  when the encoding module isn't shipped.

## anti-patterns / limits
- Relies on `ord_n(SIGNATURE)` being a large fraction of the group order (small index ⇒
  membership brute-force succeeds); for a random SIGNATURE the index distribution makes
  failure probability negligible, but it is not a proof.
- If SIGNATURE were divisible by every small prime in the picker list, a larger smooth-ordered
  p would be needed — not implemented.

## artifacts [OBSERVED]
- code: 13394.py, live.py, probe.py, solve.py
- data/logs: flag_lets_decrypt_2.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Server source provided: `13394.py` (this folder). NOT consulted: /solutions/, writeups (no-cheat rule).
