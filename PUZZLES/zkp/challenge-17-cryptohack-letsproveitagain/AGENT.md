---
record: agent-aar
puzzle: challenge-17-cryptohack-letsproveitagain
category: zkp
url: https://cryptohack.org/challenges/letsproveitagain/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/zkp/challenge-17-cryptohack-letsproveitagain/flag.txt"
flag_sha256: e108a84ed71aad7dbe3da5016273489c29609c1d7c9e81abd6add9e28df9b26e
skills: []
human_twin: AAR.md
---

# AGENT — 238-cryptohack-letsproveitagain: Let's Prove It Again (CryptoHack, 175 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
Same Schnorr-over-flag setup as part 1 (`y = 2^FLAG mod p`, `r = (v - c·FLAG) mod (p-1)`), "fixed" by the intern in three ways that introduce a *better* flaw:
1. `v` is now drawn **once in `__init__` and reused in every proof** (previously re-randomized per proof).
2. `c = sha3_256(t^y^g^salt)` with `salt = R.randint(2, BITS)` — unknown to us, but only **~1023 possibilities** (2..1024).
3. `max_turns` cut 12 → 4.

The client-seed oracle from part 1 remains: `refresh` with our own seed makes two separate proofs use the **same prime p** (and the same fixed `v`).

## reusable-rules
- Reusing the nonce `v` across two Schnorr-style proofs with the same group is fatal: the system becomes linear in `(v, FLAG)` and the secret falls out by subtraction — the classic nonce-reuse ⇒ key-recovery pattern (cf. ECDSA k-reuse), here baked into the design.
- A "hiding" salt drawn from a tiny range (`randint(2, 1024)`) is no protection: brute-force the salt, not the secret.
- When a turn budget blocks the obvious refresh pattern, burn a throwaway proof to reset the turn-state machine (`your_turn`).

## anti-patterns / limits
- Solved on the first live attempt; no failed live approaches. Offline harness validated 3/3 before connecting. (The offline harness's FLAG-replacement string didn't match the placeholder, so locally it recovers the `????` placeholder — attack mechanics still fully exercised against the real server logic.)

## artifacts [OBSERVED]
- code: 13431.py, solve.py
- data/logs: flag_letsproveitagain.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Platform: CryptoHack, zkp category, slug `letsproveitagain`, socket.cryptohack.org:13431
- Worked from statement + provided `13431.py` only. **NOT consulted:** /solutions/, third-party writeups (no-cheat rule).
