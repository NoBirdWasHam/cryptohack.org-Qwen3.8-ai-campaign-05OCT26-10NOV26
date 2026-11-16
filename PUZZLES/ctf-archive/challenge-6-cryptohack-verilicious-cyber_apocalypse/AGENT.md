---
record: agent-aar
puzzle: challenge-6-cryptohack-verilicious-cyber_apocalypse
category: ctf-archive
url: https://cryptohack.org/challenges/verilicious-cyber_apocalypse/
status: solved
date: 2026-10-31
flag_ref: "FLAGS/ctf-archive/challenge-6-cryptohack-verilicious-cyber_apocalypse/flag.txt"
flag_sha256: 59c5836eeb8ba1b40499073797ef1d3af9d51db9dc8f166471a441fa3d3e8c87
skills: []
human_twin: AAR.md
---

# AGENT — verilicious-cyber_apocalypse (CryptoHack archive, HTB Cyber Apocalypse 2025, author r4sti)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
`verify()` turns PyCryptodome's `PKCS1_v1_5.decrypt(ct, sentinel)` into a
binary "PKCS#1 v1.5 padding is VALID" oracle (sentinel is returned iff decode
fails). The `assert all(ver.verify(r^e * enc_flag) for r in R)` line then
publishes 78 multipliers r for which the oracle said VALID. Decoding of
r*m mod n (m = padded flag) is valid iff its top bytes are 00 02 (plus a 00
separator later) — i.e. r*m mod n ∈ [2^1009, 3·2^1008), an interval of width
2^1008 ≈ n / 2^15.4. Each multiplier leaks ~15.4 bits of m; 78 of them give
~1200 bits > 1024-bit m ⇒ m uniquely pinned (offline, non-adaptive RSA
scaling / HNP-style interval information).

## reusable-rules
- A PKCS1v15 "decrypt with sentinel" oracle leaks ~15 bits per scaling
  multiplier (00 02 prefix = 8+7 bits of the residue), not 3 — always
  recompute interval widths from the *em* byte layout, not from
  "which byte differs".
- Build fpylll inputs as a true basis: the generator set {R-row} ∪ n·I is
  redundant (rank-deficient → LLL leaves a zero row → BKZ on non-basis =
  garbage). The (1, R_i/R_0) row0 form fixes both basis and redundancy.
- A box symmetric about the target center admits a mirror point; always
  discriminate candidates with the RSA relation m^e == enc_flag.
- For BDD with huge gap, fplll's `CVP.closest_vector` (Babai-radius
  enumeration) on an LLL basis is drastically faster than Kannan+BKZ.
- Checked first: is R a raw MT19937(randbytes) stream (twist/untwist test
  over all alignments — negative; seed(s) was a red herring).

## anti-patterns / limits
- BKZ-40 Kannan embedding never completed on the real instance during this
  session (host saturated by 3 other agents' jobs; ~1100 s CPU spent in
  BKZ-25 stage too); the enumeration route succeeded instead, so BKZ-40
  feasibility here is untested rather than disproven.
- MT19937 angle ruled out by evidence (twist test over 1900 alignments,
  best match 0/300), not by proof; R is simply author-filtered multipliers.
- Flag's eprint reference was NOT consulted (flag text self-referential).

## artifacts [OBSERVED]
- code: mt_test.py, sim.py, sim2.py, sim3.py, sim4.py, sim5.py, solve.py, solve2.py, solve3.py
- data/logs: flag_verilicious-cyber_apocalypse.txt, output.txt, solve.log, solve2.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Platform: CryptoHack, ctf-archive card 'Verilicious (Cyber Apocalypse 2025)' (challenge file per site.md).
- Statement provenance: statement.txt in folder (begins: "# Verilicious (Cyber Apocalypse 2025), contributed by r4sti # # A sacred ward, o...")
- Provided material as stored in folder: flag_verilicious-cyber_apocalypse.txt, mt_test.py, output.txt, sim.py, sim2.py, sim3.py, sim4.py, sim5.py
- Not consulted: /solutions/ pages, third-party writeups (campaign no-cheat rule).
