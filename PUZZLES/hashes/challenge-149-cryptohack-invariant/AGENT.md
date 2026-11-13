---
record: agent-aar
puzzle: challenge-149-cryptohack-invariant
category: hashes
url: https://cryptohack.org/challenges/invariant/
status: solved
date: 2026-10-23
flag_ref: "FLAGS/challenge-149-cryptohack-invariant/challenge-149-cryptohack-invariant/flag.txt"
flag_sha256: 73727b977e058cc91cb01684efe25616398b3296f5cbb14c593e059bca936379
skills: []
human_twin: AAR.md
---

# AGENT — CryptoHack "invariant" (250 pts, hashes, socket 13393)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
The custom 64-bit block cipher `MyCipher` (16 nibbles, 31 rounds) has a **16-bit invariant subspace**:

V = {states whose 16 nibbles all lie in {6, 7}} — closed under E_K for **every** key.

Why each round preserves V:
1. **Subkey XOR:** subkeys are extracted as single bits (`(RK >> (16j+i)) & 1`), so each nibble is XORed with 0 or 1 → 6↔7, stays in V.
2. **S-box:** `SB` contains the 2-cycle (6 7): SB[6]=7, SB[7]=6. Permutation `SR` just moves positions.
3. **Linear layer:** X[c] = XOR of four nibbles from {6,7}. Since 6=0b0110, 7=0b0111, the XOR of four such values is just the parity of the number of 7s, i.e. X[c] ∈ {0,1}; XORing that bit back into a {6,7} nibble keeps it in V.

So E_K maps V→V bijectively: the cipher restricted to V is only a 16-bit permutation, for any key. (Classic invariant-subspace attack, textbook material — no third-party CryptoHack writeups consulted.)

## reusable-rules
- Single-bit subkeys + an S-box fixed point/2-cycle on a low-bit coset ⇒ invariant subspace; "roll your own" ciphers leak exactly this.
- In DM, if E_K preserves a subspace V and you feed blocks from V, the chaining value collapses to a tiny set ({0,1}-nibbles after one block) — preimage becomes a small search.
- Message-derived key K=sha512(msg) does NOT save the hash here: brute-forcing the message block re-rolls K for free.

## anti-patterns / limits
- A prior session did the math, wrote `probe.py`/`solve.py` and produced `preimage.txt`, but never verified or submitted (no flag file existed). This session's work: local re-verification of the preimage (digest = 00·8 ✓), live submission, flag capture, submission to the site.
- First `submit_flag.py` run died on a transient TLS ConnectionReset (WinError 10054) to cryptohack.org; retry loop succeeded on attempt 1 of 3.
- score_delta = 0 on all submissions with a correct flag → already credited (brief says this is fine).
- Did not independently re-run the 2^16 brute force this session (preimage verified end-to-end instead); no third-party solutions viewed.

## artifacts [OBSERVED]
- code: probe.py, solve.py
- data/logs: flag_invariant.txt, preimage.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided cipher source only. Invariant-subspace attack named as textbook material in the original AAR ("no third-party CryptoHack writeups consulted"); specific text not cited in run logs. Math self-derived by the prior session; verified/submitted by the follow-up session.
