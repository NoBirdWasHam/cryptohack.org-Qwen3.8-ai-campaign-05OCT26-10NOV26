---
record: agent-aar
puzzle: challenge-57-cryptohack-a_joke_cipher-hkcert_ctf2021
category: CTF Archive
url: https://cryptohack.org/challenges/a_joke_cipher-hkcert_ctf2021/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-57-cryptohack-a_joke_cipher-hkcert_ctf2021/flag.txt"
flag_sha256: ae38542a7e4eedaa0d81a501ed42af5aafabfc6e4a33ae2e8ac5a893d8e56a1d
skills: []
human_twin: AAR.md
---

# AGENT — a_joke_cipher-hkcert_ctf2021 (A Joke Cipher, HKCERT CTF 2021)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
The "Nagaty cryptosystem" reduces the shared secret modulo p at every step, and the private key `S_A` only ever appears modulo p (`y_A = S_A mod p`). The shared-key formula `S_AB = (y_A*y_B)*y_B*S_A mod p` is therefore public-only arithmetic — the secret cancels out by commutativity of multiplication in the very ring where it lives. On top of that, encryption is a bare unpadded integer multiply `c = m * S_AB`, the second joke.

## reusable-rules
- Any "shared secret" formula `f(y_A,y_B)·S_A mod p` where f is public and multiplication is commutative is broken when the reduction happens mod p and `S_A` only ever appears mod p — the public key *is* the secret in the ring used.
- Always ask "what modulus is the final secret reduced under?" — matching it against how the private key enters decides the attack.
- Unpadded multiply encryption leaks via size even when the key were secure.

## anti-patterns / limits
- Break (B) (key-free division bound argument) was sketched but not separately executed as an independent decryption (no candidate S_AB search); the primary algebraic reconstruction + exact round-trip `sk·m == c` was the verified path. No failures to report; solved in <10 tool calls, no alternatives tried and abandoned.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_a_joke_cipher-hkcert_ctf2021.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Derived from the provided `chall.py` and `output.txt`; no writeups or solution pages consulted. The scheme paper named *inside chall.py* is Khaled A. Nagaty, Neural Computing & Applications 2020 (Springer 10.1007/s42452-019-1928-8) — cited for provenance of the construction, not used as a solve source.
- Upgrade-time comprehension check (batch #9, 2026-11-02): re-derived the S_AB collapse and the exact-division step offline from `chall.py`/`solve.py`; no new submission, flag untouched.
