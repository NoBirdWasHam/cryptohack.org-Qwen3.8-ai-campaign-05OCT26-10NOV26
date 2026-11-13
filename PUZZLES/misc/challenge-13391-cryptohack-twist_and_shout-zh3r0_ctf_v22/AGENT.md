---
record: agent-aar
puzzle: challenge-13391-cryptohack-twist_and_shout-zh3r0_ctf_v22
category: misc
url: https://cryptohack.org/challenges/twist_and_shout-zh3r0_ctf_v22/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-13391-cryptohack-twist_and_shout-zh3r0_ctf_v22/flag.txt"
flag_sha256: 9ff1a3020bf9fdda4a2611e887b58759495c3436d6d3051b3db692b67a5248cd
skills: [ctf-mt19937-cracking]
human_twin: AAR.md
---

# AGENT — Twist and Shout (Zh3r0 CTF V2), twist_and_shout-zh3r0_ctf_v22
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack" [OBSERVED text; evidence tag applies to its source, not each claim]
1. Read 624 words from `archive.cryptohack.org:46347`.
2. `untemper` each word → post-twist array N (pos=624 at setstate means the first output
   triggers the twist, so outputs 0..623 are temper(N[0..623]) of the post-twist array).
3. Untwist N once with the **in-place CPython twist** inverse (skill
   `ctf-mt19937-cracking`) → original state words O[0..623].
4. Pack O big-endian → 2496-byte state; regex `zh3r0\{.*\}` finds the flag in the clear.

Information loss: the twist destroys only **low 31 bits of O[0]** (bytes 0–3 of the state).
Flag start offset is uniform, so P(flag touches bytes 0–3) ≈ (len+3)/2496 ≈ 1.5%; the solver
simply reconnects in that case (fresh padding per connection). Not hit in practice on try 1.

## reusable-rules
- Full-state `setstate` + one full output period = untwist is all you need; verify the
  in-place twist model against live CPython, not the canonical out-of-place formula.
- Randomly-positioned secret inside the leaked state turns the 31-bit word-0 hole into a
  ~1.5% retry, not an attack step.

## anti-patterns / limits
- If the flag overlapped word 0 we would have needed ~31-bit brute force (charset-reduced)
  instead of reconnecting; reconnect path was sufficient and untested for brute fallback.

No third-party writeups/solutions consulted. References: skill ctf-mt19937-cracking
(bad_temper untwist derivation).

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_twist_and_shout-zh3r0_ctf_v22.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Live listener output (sole flag provenance); skill `ctf-mt19937-cracking` (untwist/untamper derivation, incl. bad_temper). Original AAR: no third-party writeups/solutions consulted; description.yml used only as a post-hoc artifact cross-check (location cited above).
