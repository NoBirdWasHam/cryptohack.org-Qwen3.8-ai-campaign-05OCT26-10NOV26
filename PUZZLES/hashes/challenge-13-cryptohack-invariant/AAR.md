# AAR — CryptoHack "invariant" (250 pts, hashes, socket 13393)

**Flag:** `[flag value withheld — real-flag strings live only under FLAGS/]` (server said "Congratulations!", submitted via `submit_flag.py`, ok:true / 200; score_delta 0 = already credited).

## The vulnerability
The custom 64-bit block cipher `MyCipher` (16 nibbles, 31 rounds) has a **16-bit invariant subspace**:

V = {states whose 16 nibbles all lie in {6, 7}} — closed under E_K for **every** key.

Why each round preserves V:
1. **Subkey XOR:** subkeys are extracted as single bits (`(RK >> (16j+i)) & 1`), so each nibble is XORed with 0 or 1 → 6↔7, stays in V.
2. **S-box:** `SB` contains the 2-cycle (6 7): SB[6]=7, SB[7]=6. Permutation `SR` just moves positions.
3. **Linear layer:** X[c] = XOR of four nibbles from {6,7}. Since 6=0b0110, 7=0b0111, the XOR of four such values is just the parity of the number of 7s, i.e. X[c] ∈ {0,1}; XORing that bit back into a {6,7} nibble keeps it in V.

So E_K maps V→V bijectively: the cipher restricted to V is only a 16-bit permutation, for any key. (Classic invariant-subspace attack, textbook material — no third-party CryptoHack writeups consulted.)

## The attack
Hash is Davies–Meyer with a self-derived key: h0=0, h_i = E_K(h_{i-1} ⊕ m_i) ⊕ m_i, K = sha512(full message).

- Pick **m1 ∈ V**: h1 = E_K(m1) ⊕ m1 has all nibbles in {0,1} (XOR of two {6,7} values).
- Pick **m2 ∈ V**: x = h1 ⊕ m2 ∈ V, so E_K(x) ∈ V. If E_K(x) = m2 then h2 = 0.
- K depends on m2, so **brute-force all 2^16 candidates m2 ∈ V**, recomputing K = sha512(m1‖m2) each time. E_K(x) is ~uniform on V (2^16 states) → hit probability 2^-16 per trial, ≈1 expected hit per m1.

Found a hit on the first random m1 (seed 0xC0FFEE). Preimage: `77766676667766677767767767676667` (16 bytes). Work factor ≈ 2^16 cipher evals vs 2^64 generic preimage.

## Key numbers
- |V| = 2^16 states; brute force = 2^16 encryptions (~1–2 min pure Python).
- Digest verified locally to `0000000000000000` before sending; server returned the flag on first hash query.

## Learning points
- Single-bit subkeys + an S-box fixed point/2-cycle on a low-bit coset ⇒ invariant subspace; "roll your own" ciphers leak exactly this.
- In DM, if E_K preserves a subspace V and you feed blocks from V, the chaining value collapses to a tiny set ({0,1}-nibbles after one block) — preimage becomes a small search.
- Message-derived key K=sha512(msg) does NOT save the hash here: brute-forcing the message block re-rolls K for free.

## Limitations / honest notes
- A prior session did the math, wrote `probe.py`/`solve.py` and produced `preimage.txt`, but never verified or submitted (no flag file existed). This session's work: local re-verification of the preimage (digest = 00·8 ✓), live submission, flag capture, submission to the site.
- First `submit_flag.py` run died on a transient TLS ConnectionReset (WinError 10054) to cryptohack.org; retry loop succeeded on attempt 1 of 3.
- score_delta = 0 on all submissions with a correct flag → already credited (brief says this is fine).
- Did not independently re-run the 2^16 brute force this session (preimage verified end-to-end instead); no third-party solutions viewed.

## Vulnerability (plain words)
Three design accidents stack into a back door: round keys XOR only a single bit into each nibble, the S-box swaps 6↔7, and the linear layer XORs four {6,7}-nibbles into just a parity bit {0,1}. Result: the set V of states whose 16 nibbles are all 6 or 7 (only 2^16 of 16^16 states) maps into itself for EVERY key. A 64-bit cipher secretly contains a 16-bit permutation.

## How the answer follows
1. Davies–Meyer hash h_i = E_K(h_{i−1} ⊕ m_i) ⊕ m_i, K = sha512(full message), target digest 0.
2. Choose m1 ∈ V ⇒ h1 = E_K(m1) ⊕ m1 has all nibbles in {0,1} (XOR of two {6,7} values).
3. Choose m2 ∈ V ⇒ x = h1 ⊕ m2 ∈ V ⇒ E_K(x) ∈ V; whenever E_K(x) = m2 we get h2 = 0.
4. K re-rolls with each tried m2, so brute-force all 2^16 candidates m2 ∈ V: hit probability 2^-16 per trial ⇒ ≈1 expected hit per m1; first random m1 (seed 0xC0FFEE) gave the preimage `77766676667766677767767767676667`.
5. Digest verified locally == 0000000000000000 ⇒ server flag `[flag value withheld — real-flag strings live only under FLAGS/]`, submitted ok:true. Work ≈ 2^16 cipher evals vs 2^64 generic.

## Limitations / attempts that failed
- This session verified and submitted rather than re-running the 2^16 search (preimage.txt end-to-end verified instead); first submit died on a transient TLS ConnectionReset (WinError 10054), retry succeeded.
- score_delta 0 = already credited (expected). No other failed paths recorded in run logs.

## Sources
Provided cipher source only. Invariant-subspace attack named as textbook material in the original AAR ("no third-party CryptoHack writeups consulted"); specific text not cited in run logs. Math self-derived by the prior session; verified/submitted by the follow-up session.
