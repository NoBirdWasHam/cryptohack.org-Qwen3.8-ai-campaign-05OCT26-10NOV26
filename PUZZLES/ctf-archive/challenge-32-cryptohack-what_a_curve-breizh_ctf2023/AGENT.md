---
record: agent-aar
puzzle: challenge-308-cryptohack-what_a_curve-breizh_ctf2023
category: ctf-archive
url: https://cryptohack.org/challenges/what_a_curve-breizh_ctf2023/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-32-cryptohack-what_a_curve-breizh_ctf2023/flag.txt"
flag_sha256: 7fca15bee517687164ce41edcd7278cc0afd8865bd8d56b589a8cb8ffb9b8d1e
skills: []
human_twin: AAR.md
---

# AGENT — What a Curve! (Breizh CTF 2023, CryptoHack archive)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
A genus-7 hyperelliptic "RNG" streams the 14 Mumford coordinates of Jacobian points as keystream, XORed with (flag + fixed 56-byte suffix). There is no discrete log to break: the message fits EXACTLY one 112-byte block, and the known suffix covers keystream bytes 56..111 = precisely the v-coordinates of D₁ = [2023]P₀, while the unknown flag covers precisely the u-coordinates. Reduced Mumford pairs obey f ≡ v² (mod u), i.e. u divides f − v². The server's XOR oracle (fresh RNG per query, SAME curve for the whole connection) donates as many reduced (u,v) pairs as needed to recover f by linear algebra — after which the flag's u is just one of a handful of degree-7 divisors of the known polynomial f − v².

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Attack requires the message (flag+suffix) to fit exactly one block (112 B) so the suffix lands on v and the flag on u. A longer flag (v-region partially masked by flag bytes) would break the alignment — untested fallback.
- If f − v² were non-squarefree (prob ≈ 1/p, didn't occur) `factor_monic` raises; a squarefree-decomposition fallback is not implemented.
- Candidate uniqueness rests on the printable-ASCII filter (7–21 candidates/conn); no structural filter enforcing "D₁ = [2023]·(a point)" was implemented — deemed unnecessary given 56 ASCII bytes and the identical flag on two independent connections.
- Parent brief's "rank-16 EC over Q" resume-state matched nothing on disk (rank16.py absent; folder 277 is a different challenge). Treated as stale metadata and re-derived everything from statement + live server.
- EdZ textbook reference used: von zur Gathen & Gerhard, Modern Computer Algebra (distinct-degree + equal-degree factorization); Mumford representation per standard hyperelliptic literature. No writeups consulted.

## artifacts [OBSERVED]
- code: attack.py, cantor2.py, chall.sage, frecov.py, jm97.py, probe1.py, session1.py, solve2.py, solve_live.py
- data/logs: flag_what_a_curve-breizh_ctf2023.txt, session1.json, solved1.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
chall.sage + the live oracle only. References named by the original AAR: von zur Gathen & Gerhard, Modern Computer Algebra (distinct-degree + equal-degree factorization); Mumford representation from standard hyperelliptic literature. No third-party writeups consulted; flag derived twice independently and submitted ok:true.
