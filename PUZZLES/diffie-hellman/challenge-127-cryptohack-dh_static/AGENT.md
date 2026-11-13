---
record: agent-aar
puzzle: challenge-127-cryptohack-dh_static
category: diffie-hellman
url: https://cryptohack.org/challenges/dh_static/
status: solved
date: 16 Oct 2026
flag_ref: "FLAGS/diffie-hellman/challenge-127-cryptohack-dh_static/flag.txt"
flag_sha256: b04515e1d33d5bda2c6333753f7fca2acbce9f3f7226afd66f9f672f0a6eec18
skills: []
human_twin: AAR.md
---

# AGENT — dh_static (100 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
1. Probed the protocol (3 probe scripts): phase 1 prints an intercepted DH
   conversation (fresh A per connection) + flag ciphertext; phase 2 asks me to
   send Bob `{p, g, A}`, and Bob returns `{"B": g^b mod p}` plus a fixed
   message under `SHA1(str(A^b mod p))[:16]`. **Bob uses my p and g.**
2. Verified the "static" part: Bob's B in the intercepted conversation is the
   SAME 1536-bit constant across every connection (6+ observations).
   `B_static = 0x8d79b693...94ebfa8ef0`.
3. Dead ends explored (documented for honesty):
   - `A=1` → shared = 1 → decrypts only the fixed chit-chat message, not the flag.
   - `A=P−1` with QNR g → shared = (−1)^b ∈ {1, P−1} → same fixed message.
   - Replaying Alice's A as my A → still only the fixed message.
   - P is a SAFE prime (P−1 = 2q, q 1535-bit prime; sympy), so no
     order-lifting via small subgroups.
   - BSGS for a small constant b < 2^46 (2^20 baby table, 67M giant steps,
     `bsgs_b.log`): **no hit** — b is not small.
4. The actual attack (the one-line insight): Bob's phase-2 reply field "B" is
   **(my g)^b mod p**. Choose `g = A` (Alice's public value from the
   intercepted conversation). Then Bob returns `A^b mod P` — the very shared
   secret the flag was encrypted under — in the clear. The static key is what
   makes phase-2's `A^b` equal the intercepted conversation's `A^b` (a fresh
   per-session b would give a different secret).
5. key = SHA1(str(A^b))[:16] → AES-128-CBC decrypt of the intercepted
   `{iv, encrypted}` → flag.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Probed protocol with 4 minimal connections; ran one BSGS offline (b < 2^46).
- Did not hammer the server; each attempt was one clean connection.
- Did not consult any writeup; the attack emerged from protocol analysis.

## artifacts [OBSERVED]
- code: explore_A1.py, solve.py
- data/logs: bsgs_b.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/diffie-hellman/ (slug `dh_static`)
- Service: `socket.cryptohack.org:13373` (protocol in site.md)
- **NOT consulted:** /solutions/, /solves/, any external writeups. (No web search
  needed either — the attack follows from the protocol once you realize Bob
  returns (your g)^b.)
