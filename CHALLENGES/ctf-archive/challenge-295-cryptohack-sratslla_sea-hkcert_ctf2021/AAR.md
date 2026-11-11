# AAR — sratslla_sea-hkcert_ctf2021 ("Sratslla SEA", HKCERT CTF 2021)

**Result: NOT solved.** 8 of 16 key bytes (w0,w1) recovered with certainty; remaining 8
reduced to an explicit 64-bit constraint system that was not solved within budget.
Server `archive.cryptohack.org:36161` live and responsive (flag ciphertext fetched twice).

## Challenge
Oracle holds random 16-byte key `k`; prints AES_k(flag) for a 64-byte flag (4 blocks, ECB-style, no IV).
128 queries: `[ark|sb|sr|mc] [data|secret]`. `secret` burns the option and encrypts the
corresponding 16-byte slice of `secret = k[0]*4 || k[1]*4 || ... || k[15]*4`; `data`
encrypts a chosen 16-byte block. Each stage re-instantiates AES and no-ops ONE component
(`_add_round_key` / `_sub_bytes` / `_shift_rows` / `_mix_columns`). Provided `aes.py` = bozhu
pure-python AES-128 (standard 10 rounds, standard key schedule, verified byte-for-byte on
schedule/rounds vs textbook AES; only external-patching hooks added — the flaw is the oracle,
not the S-box/schedule).

## What worked (verified)
1. **ark mode is keyless** (every ARK, incl. final, no-oped ⇒ public permutation).
   Inverting it locally on `ark secret` ciphertext yields slice 0 ⇒ **k0..k3 = 1b807af1**.
   Verified: ark enc identical under two random keys (probe.py).
2. **sb mode is GF(2)-affine** (SB off ⇒ rounds are SR∘MC∘XOR; linear part M is public,
   key only shifts a constant). `E(x)⊕E(0)` measured via `sb data 00*16`; M built from unit
   vectors, GF(2) 128×128 solve gives slice 1 ⇒ **k4..k7 = 13d3e047**. Affineness verified
   empirically (xor3-identity holds against E(0)).
3. Collected full probe set (7 queries): ark_sec, sb_zero, sb_sec, mc_zero, mc_sec,
   sr_zero, sr_sec + flag ciphertext (collect.json). All stage slices show the exact
   repeated-column structure predicted — server matches provided aes.py on ark path.

## What the remaining 64 bits depend on (analysis)
- **mc stage (MixColumns off):** byte-lane independent chains, but the key schedule couples
  everything: w6=w2⊕w5, w7=w3⊕w6 leak w2,w3 into every lane from round 2 on (RotWord rotates
  the leaked byte index each boundary ⇒ all of w2,w3 in every chain by round ~5).
- **sr stage (ShiftRows off):** 4 independent 32-bit units (key-schedule words w_i, w_{i+4}, …)
  but each unit's schedule still involves all of w2,w3.
- Empirically (probe.py): changing ANY of k8..k15 changes ALL 16 output bytes of both mc and
  sr stage ciphertexts ⇒ no per-byte peeling; system is 256 bit of equation on 64 bit unknowns.

## Failed paths (evidence)
- **z3 bit-blasted model** (sound: verified exact vs pure-python AES with key pinned —
  diag.py SAT, outputs identical). Search through 10 S-box layers over the free 64 bits is
  not tractable: full constraint set → `unknown` (timeout 240 s and 400 s runs);
  `mc_zero`-only → still `unknown` at 300 s (diag3). A quick "sat" in 6 s under
  `SolverFor('QF_BV')` with S-box arrays was an artifact (Selects uninterpreted ⇒ unsound
  model; candidate key fails every stage check — documented so nobody reuses it).
- Planned but out of budget: GF(2^8) F4/Groebner formulation of the σ-atom system
  (σ_r,m = S(affine in σ_{<r}, x, y)) — z3's ff tactic API not exposed in this build.

## Notes for a future attempt
- `mc data` inputs reach lane (i,j) masked by w_i[j] of the chain's **input position**; lanes
  whose input position lies in words 0/1 have KNOWN mask ⇒ their chain functions can be
  probed at fully chosen inputs (≤128 of 256 points). Combining 8 fully-controlled chains'
  partial tables + zero/sb-probes into a Groebner solve over GF(2^8) is the promising open path.
- 128 queries were NOT exhausted (7 used); session is single-key per connection; re-collect if stale.

## Files
- chall.py, aes.py (server-provided sources, copied from prior unit's download)
- probe.py (stage dependency/affineness tests), collect.py (live oracle session),
  solve12.py (ark-invert + GF(2) affine solve → k0..7), solve34.py/solve34b.py (z3 attempts),
  diag.py/diag2.py/diag3.py (model validation; unsound-QF_BV artifact), collect.json, partial.json
- Statement: category card `cat_ctfarch.html` (grep `sratslla`); archive port 36161.

No third-party solutions consulted (FLAG PROVENANCE respected; no flag obtained).


## How the partial recovery follows (attack mechanism)
1. `ark` mode no-ops every AddRoundKey (incl. the final one) ⇒ a public permutation; locally
   inverting the `ark secret` reply through the keyless round structure exposes schedule word w0
   ⇒ k0..k3 = 1b807af1.
2. `sb` mode no-ops SubBytes ⇒ every round is GF(2)-affine with a PUBLIC linear part (SR and MC are
   GF(2)-linear; the key only contributes a constant). Measuring E(x)⊕E(0) on unit vectors builds the
   128×128 matrix M; solving M·x = (sb secret ⊕ sb zero) over GF(2) gives w1 ⇒ k4..k7 = 13d3e047.
3. mc/sr stages: key-schedule coupling (w6 = w2⊕w5, w7 = w3⊕w6, RotWord drift) spreads every unknown
   byte into every output byte — probes confirm changing any of k8..k15 changes all 16 output bytes;
   the remaining 64 bits stayed unsolved in THIS session (z3 bit-blast timed out; the fast "sat" was
   an unsound QF_BV artifact, documented above).

Corpus note (batch #11, append-only; claims above untouched): this folder records the EARLY PARTIAL
attempt (8/16 key bytes, no flag). The canonical solve for `sratslla_sea-hkcert_ctf2021` lives in the
sibling misspelled folder `challenge-295-cryptohack-srateslla_sea-hkcert_ctf2021/AAR.md` (Run #3:
4-stage single-session attack, full key + flag, flag.txt archived). The ledger credits the slug ONCE
(nn 295, SOLVED) — that credit is the sibling folder's work, not this folder's.
