# AAR — blind (ECSC 2023 Norway) — challenge-247

## Status: SOLVED
Flag: see flag_blind-ecsc_2023_norway2023.txt (derived, not copied from any repo).
Submission: ok:true / HTTP 200; account solved count 265 → 266 (archive challenge, score_delta 0).

## The scheme (from provided blind.sage)
Ed448 (worked as its birational Weierstrass image over the Goldilocks field p=2^448-2^224-1).
Y = -x·G. "Blind" Schnorr signing of a 128-bit message m:
- m1 = F1(m) ‖ (F2(F1(m)) ⊕ m)  (56-byte pseudorandom mask, F1/F2 = SHA256-based Expand)
- ω ← Z_p; r = x(ω·G) ⊕ m1; c = int(H(r)); z = (ω + c·x) mod p.
Output: Y, AES-CTR ciphertext of flag under bcrypt.kdf(k=m, "ICC_CHALLENGE", 16, 31337),
and 10000 sigs = **one real sign on m = _k** (the 16-byte AES key) + 9999 random
(r, z) pairs, shuffled.

## Attack
The masking only hides m *inside* the signature — verification still pins R:
R = z·G + c·Y = ω·G, so m1' = r ⊕ x(R) must equal the mask structure. For any m1'
candidate, m = F2(m1'[:40]) ⊕ m1'[40:56] is forced, and the 320-bit test
m1'[:40] == F1(m) holds w.p. 1 for the real sig and ≈2^-320 for random ones.
Scan all 10000 sigs → exactly one hit (index 7135) → _k = 078ca69012d65278484caaacc28ebe4f
→ bcrypt.kdf → AES-CTR(nonce=b"") decrypt → flag. Pure offline; no listener used.

## Key numbers
- 10000 sigs scanned, 1 match (as designed). Runtime ~1.3 ms/sig pure-Python Jacobian
  double-and-add, ~40 s total.

## Learning points
- "Message blinding" with a *keyed-by-message* mask is not blind: the signature
  equation is still verifiable once you invert the mask's own definition.
- Flag the design flaw vs my bugs by testing group axioms first: G on curve,
  ORDER·G = O, Edwards↔Weierstrass round-trip.

## Limitations / what failed
- First scan run: 0 hits. Root cause was MY typo: Ed448 d constant transcribed with
  2 extra hex digits (114 vs 112). Diagnosed by comparing A/B and to_w(G) against an
  independent pure-int computation; fixed, then solved. No crypto difficulty, no
  timeouts; archive file links (cryptohack.org/static/challenges/...) downloaded fine.

## Files
- solve.py (runnable: `python3 solve.py` in this folder, needs blind.sage/output.txt, bcrypt, gmpy2)
- statement.txt, site.md, blind.sage, output.txt, flag_blind-ecsc_2023_norway2023.txt

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
