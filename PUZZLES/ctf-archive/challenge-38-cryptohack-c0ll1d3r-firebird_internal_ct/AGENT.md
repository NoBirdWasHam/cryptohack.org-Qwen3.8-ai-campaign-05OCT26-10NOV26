---
record: agent-aar
puzzle: challenge-38-cryptohack-c0ll1d3r-firebird_internal_ct
category: CTF Archive
url: https://cryptohack.org/challenges/c0ll1d3r-firebird_internal_ct/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-38-cryptohack-c0ll1d3r-firebird_internal_ct/flag.txt"
flag_sha256: bd829eaac098834d3d497ee1785463ab73bf27a54521dc25c489d440391d984f
skills: []
human_twin: AAR.md
---

# AGENT — C0ll1d3r (Firebird Internal CTF), CryptoHack ctf-archive, archive.cryptohack.org:9391
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
Not an MD5 collision: hash(m) = pow(g, int.from_bytes(b'SECUREHASH_'+m,'big'), p) with fresh random 256-bit g and 256-bit prime p per connection, 5 lowercase-only messages. Two breaks: (1) the oracle leaks the PARAMETERS -- same-length messages share the prefix exponent 2P*256^L, so any byte relation x1+x2=x3+x4 gives p | h1*h2 - h3*h4 as a computable ~2^512 integer, and two independent relations gcd to p (g recovered via a message whose exponent is coprime to p-1); (2) no discrete log is needed to collide: Fermat gives g^(p-1) = 1, so any lowercase X with int(b'SECUREHASH_'+X) congruent to the target mod p-1 collides -- writing bytes as 109+d_i, d_i in [-12,13], that is a small-digit modular knapsack sum d_i*256^i = T (mod p-1), a CVP.

## reusable-rules
- `CVP.closest_vector` enumeration EXPLODES here: the l2 ball of radius ~box-diagonal
  (12.5*sqrt(L)) holds ~2^80 lattice points while the cube holds 2^26-2^40. Ball-based
  CVP is the wrong tool; BKZ-40 + (randomized) Babai is right.
- Additive relations among exponents (equal sums) give p-divisible COMPUTABLE integers
  when exponents are too big for unreduced powers (the `h1^e2 - h2^e1` gcd trick is dead
  when a fixed prefix forces exponents >= 2^88).
- g recovery: pick a message whose exponent is coprime to p-1 (odd last byte); 'l','n'
  end in even bytes -> gcd(e,p-1)>=2.
- Site slugs can be truncated to 29 chars — trust the data-challenge attribute.

## anti-patterns / limits
- Babai success is probabilistic per connection (most succeed at L=64; one local p
  needed all L fallbacks). Mitigated by reconnect-retry + L in {64,66,62,68,60,70}.
- First live attempt took ~10 min wall-clock (L^2 bigint ops per Babai randomization);
  optimized post-solve to single-basis-vector shifts (solve.py carries the fast version;
  the flag was won by the pre-optimization run).
- No third-party writeups consulted; method = standard BKZ/Babai CVP (fpylll 0.6.4).

## artifacts [OBSERVED]
- code: server_local.py, solve.py, test_inproc.py, test_lattice.py, test_lattice2.py, test_precovery.py
- data/logs: flag_c0ll1d3r-firebird_internal_ct.txt, live_solve.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided chall.py + live listener + local harness running the real chall.py logic (server_local.py); own solve.py, test_lattice2.py, test_precovery.py, test_inproc.py + logs (live_solve.log, local_solve*.log). Method = standard BKZ/Babai CVP (fpylll 0.6.4); AAR states no third-party writeups consulted.
