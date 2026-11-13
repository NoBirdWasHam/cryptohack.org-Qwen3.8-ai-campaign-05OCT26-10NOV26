---
record: agent-aar
puzzle: challenge-325-cryptohack-d-phi-enc-hacktm_ctf2023
category: misc
url: https://cryptohack.org/challenges/d-phi-enc-hacktm_ctf2023/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-325-cryptohack-d-phi-enc-hacktm_ctf2023/flag.txt"
flag_sha256: 1090ef0d6a2063049955c9c7367a870e8c0eb7cfbb3176e46e28829f06fd301e
skills: []
human_twin: AAR.md
---

# AGENT — d-phi-enc (HackTM CTF 2023)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
RSA with e=3 leaks `enc_phi = phi^3 mod n` and `enc_d = d^3 mod n`. Since
`getStrongPrime(1024, e=3)` guarantees gcd(3, phi)=1, the cube map is a
bijection mod p and mod q (no nontrivial cube roots of unity in either
field). That makes phi the *unique* common root mod n of two small-degree
polynomials, which can be found without factoring first.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Nothing failed. Only note: initial `poly_mod` had an off-length indexing
  bug for deg(a)>deg(b) caught by padding fix before any live run.
- Generalization (the flag itself taunts this): for e=65537 the same trick
  needs a common-root gcd between x^e−enc_phi and (ex−...)... actually a
  degree-e gcd — still polynomial-time, but k ranges over 1..e−1 so you'd
  search ~65537 candidates; enc_d may not even be needed.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_d-phi-enc-hacktm_ctf2023.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
