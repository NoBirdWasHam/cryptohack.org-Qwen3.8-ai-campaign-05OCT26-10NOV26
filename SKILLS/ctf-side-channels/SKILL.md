---
name: ctf-side-channels
description: Use for CTF power/timing side-channel attacks.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, side-channel, spa, ecc]
    related_skills: [ctf-crypto-attacks, cryptohack-socket-challenges]
---

# CTF side channels — power/timing analysis recipes

## When to Use
CTF challenges leaking power traces, timings, or cache behaviour of an
implementation (ECC scalar mult SPA, RSA blinding checks, etc.). For pure
math/property crypto attacks see `ctf-crypto-attacks`; for the CryptoHack
transport/submission mechanics see `cryptohack-socket-challenges`.

## Recipe: SPA on unblinded double-and-add (CryptoHack `double_and_broken`, 2026-10-14)
Given N power traces of the SAME unblinded scalar `d` (here: 50 traces of
double_and_add(G, d) on secp256k1, `d = bytes_to_long(FLAG)`):

1. **Derive the key size from the FLAG format.** `crypto{` + 37 + `}` = 45 bytes;
   leading byte `'c'` (0x63) has top bit clear → `bit_length(d) = 8*45 - 1 = 359`.
   (If the leading byte were ≥ 0x80 it would be exactly 8*len.)
2. **Count samples vs bit length to pick the leak model:**
   - samples == bit_length ⇒ ONE SAMPLE PER BIT (sample s = double, +add iff bit s=1).
   - samples == bit_length + popcount ⇒ one sample per operation (needs segmentation).
   The count constraint kills whole classes of wrong models; use it first.
3. **Template by averaging:** same key across all traces ⇒ per-position mean is a
clean template `T[s] = baseline(s) + delta·bit_s`.
4. **Detrend before thresholding.** The baseline often drifts smoothly across the
   trace (data-dependent power). Fit a low-degree polynomial (deg 1–4, check the
   split is stable across degrees) and work on the residuals.
5. **Gap split:** in the sorted residuals, the LARGEST gap separates the two
   operation classes (double-only vs double+add). No threshold to tune. Here:
   159 low / 200 high, gap ≈ 33 units.
6. **Decode with the flag format as ground truth.** Test all combos of
   {MSB-first, LSB-first} × {sample order normal/reversed} × {high=1, high=0}:
   only the one whose `d.to_bytes(len,'big')` starts `crypto{`, ends `}`, and has
   printable interior is the key. Here: LSB-first (sample 0 = bit 0), high = 1.
7. **Independent checks (all must pass before submitting):**
   `bit_length(d) == #samples`, `popcount(d) == #add-samples`, `d·G` is on-curve,
   flag interior printable.

## Pitfalls
- **Don't assume the key is 256 bits** on a 256-bit curve — the scalar is a
   `bytes_to_long(FLAG)` string, whose size comes from the flag format, not the curve.
- **A raw power threshold fails when a baseline drift exists** — the two operation
   classes overlap in absolute value. Detrend first, then gap-split the residuals.
- **Guessing the class counts from a wrong bit-length** (e.g. expecting a 256+103
   split) leads down a dead end; re-derive the counts from the format every time.
- **The `ecc_side_channel` (or equivalent) module is private** — the leak format is
   not documented. Infer it from sample counts + structure; don't burn time hunting
   for the module source.
- With identical-key traces, per-position averaging is the whole game — you do not
   need template-attack machinery (training/profiling) when the key never changes.

## Canonical references (owner list 2026-11-02)

[R21] GLRT https://en.wikipedia.org/wiki/Generalized_likelihood_ratio_test + [R22] Fano https://en.wikipedia.org/wiki/Fano%27s_inequality — decision-rule theory now in crypto-stats-inference skill (cross-ref, keep this block one line).
