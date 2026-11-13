# AAR — tenet_the_plagarism-hkcert_ct (CryptoHack ctf-archive, nn=298)

**Result: not solved — evidenced negative.** The self-contained cryptanalytic path bottoms out
at ≈2^50 ops (infeasible here); the intended solve path (OSINT/walkthrough) is forbidden by the
FLAG PROVENANCE rule. No flag was derived, so none was submitted or written anywhere.
> **SUPERSEDED 2026-11-06: SOLVED.** The wall was an artifact of the bit model, not the cipher.
> See the SOLVED section at the end of this file; the history above is kept as the audit trail.

## The cipher (from provided challenge.py — read first, nothing external used)
`TenetAES` runs 16 chained AES-128-CTR ciphers. CTR is XOR keystream, so the whole cipher is

    c = m XOR KS(b_0) XOR KS(b_1) XOR ... XOR KS(b_15),  b_i = key[i]

**The real weakness (stronger than it looks):** every key is built as `key[i:i+1] + b'\0'*15`,
i.e. the byte sits at **position 0 in every slot**, and every instance uses the same
`Counter.new(128, initial_value=0)`. So all 16 slots draw from the **same 256-entry keystream
table** v(b) = keystream of AES with key b||0^15. Hence

    KS = XOR_{b in S} v(b),  S = set of key bytes occurring an ODD number of times

Duplicate bytes **cancel**; the effective key space is parity subsets S with |S| even, |S| ≤ 16
(~2^83 subsets), not 2^128. Verified experimentally (`probe.py`):
- slot-0 table == slot-1 table over all 256 bytes: True
- parity-subset model reproduces 5 random self-generated ciphertexts exactly: True

## Known plaintext
`message = "Congratulations! " + flag`, flag = `hkcert21{...35 x w chars...}` (regex asserted in
challenge.py) ⇒ known: bytes 0..25 ("Congratulations! hkcert21{", 26 B) + byte 61 ('}') = 216 bits
of the keystream XOR; ciphertext is 62 bytes (124 hex), matching the format. Flag interior
entropy ≈ 35·log2(63) ≈ 208 bits — unguessable and guessing would not shrink the key search anyway.

## Attacks attempted / analyzed, with bounds
1. **Ordered 8+8 MITM** over slots: 256^8 = 2^64 per side — infeasible.
2. **Parity-subset MITM (best known self-derivable attack).** Split S (weight ≤16) into two
   weight-≤8 halves from 256 items: C(256,8) = 2^50.0 entries/side, Schroeppel–Shamir space
   2^25.4; matching on block 0 (128-bit target) then filtering with block-1 prefix (80 bits) +
   byte 61 gives E[false] ≈ 2^{100-128} < 0 — i.e. **unique candidate, algorithm correct**
   (toy version with 16-byte alphabet returns exactly 1 candidate = true subset, `probe.py`),
   but **time ≈ 2^50 subset sums ≈ 10^15 AES-block XORs — weeks-to-months of machine time and
   effectively unbounded external sort**. Declined; not run.
3. **Wagner generalized birthday:** needs list size ≥ 2^{128/(1+log2 k)}; with the parity
   collapse the smallest lists (all subsets of k/4 slots, 2^23.4 at 4 slots) still need
   2^{42.7} (k=4) — condition fails; with raw 256-item lists it fails worse. No.
4. **ISD framing (Prange/Lee-Brickell/Stern, syndrome decoding of 256 vectors in GF(2)^128 at
   weight ≤16):** weight is far below δn, so ISD degenerates to the C(256,8) MITM — no gain.
5. **AES single-byte-key structure:** every round key byte of AES_{b||0^15} is one of
   {const, b⊕const, sbox(b⊕const), ...} — 44 nested-sbox bytes; gives 256 related keys but no
   linear relation among v(b) usable for a weight-16 XOR-sum; AES internals (Sbox) kill any
   GF(2)-linear shortcut. No practical distinguisher-based speedup for this search.
6. **Oracle routes:** none — ctf-archive is offline (no listener on the card), no decrypt API.

## Why this is an evidenced negative (not a missing trick, per best analysis)
Generic birthday-type floor for the hidden weight-≤16 even subset among 256 items against a
128-bit target is Θ(C(256,8)^{1/1}) streaming ≈ 2^50; every alternative family above (Wagner,
ISD, lattice) provably fails or degenerates to it. 2^50 is ~10^15 ops — far beyond this
session's budget by design. The statement's own hint (author blog post "interesting flag
submissions — OSINT master", linked in the challenge card) is the historical solve route:
the original HKCERT flag value circulating among teams. **That route is exactly what the
provenance rule forbids** (answer from web/author writeup), and it was NOT opened.

## Limitations
- Not run: the ~2^50 parity-subset MITM (would need a compute cluster + disk sort; documented
  bounds above, toy-validated algorithm in `probe.py`). If such tooling existed, this challenge
  becomes feasible at ~2^50 with UNIQUE candidate (no regex needed even).
- Did not consult cryptohack solutions/solves pages, the author's blog post, or any third-party
  writeup (provenance rule); the leak location (author blog post linked from the card, containing
  original-flag discussion) is recorded here without values.
- Assumed the 216-bit known-plaintext (prefix + '}') is correct; the given ciphertext length (62 B)
  is consistent, and self-generated ciphertexts validate the attack model end-to-end.

## Files
- `challenge.py` — provided source (downloaded from card link)
- `statement.txt`, `site.md` — statement/card notes
- `probe.py` — runnable: model validation, parity-subset MITM toy validation, cost estimates

## Learning points
- CTR chaining = keystream XOR; chained single-byte AES instances whose keys share the same
  **shape** collapse the space to parity subsets (duplicates cancel) — always check the actual
  key layout (`key[i:i+1] + zeros` put every byte in position 0 here).
- Cancellation reduces 2^128 → ~2^83 (search floor 2^50) — a real break *conceptually*, but the
  residual 2^50 is still CTF-solo-infeasible, which is why the historical solves were OSINT.

## Sources
Provided materials only; the AAR names the historical third-party solve route (author blog post) and records it was NOT opened. Disclosure wording preserved verbatim:
> The statement's own hint (author blog post "interesting flag
> submissions — OSINT master", linked in the challenge card) is the historical solve route:
> the original HKCERT flag value circulating among teams. **That route is exactly what the
> provenance rule forbids** (answer from web/author writeup), and it was NOT opened.
> Did not consult cryptohack solutions/solves pages, the author's blog post, or any third-party
>   writeup (provenance rule); the leak location (author blog post linked from the card, containing
>   original-flag discussion) is recorded here without values.

## VALIDATION (2026-11-05, doctrine re-audit) — live re-verified; wall is priced on the PLANTED structure, not the generic one — holds
### Live card + endpoint re-verification
- Card live on /challenges/ctf-archive/: **59 Solves · 0 Solutions** (was 57 on 2026-10-30; +2 solvers since —
  consistent with a circulating flag string, not with new 2^49-scale derivations). Capture: `_ctfarch_live_20261105.html`.
- Provided challenge.py endpoint live and byte-identical to local evidence (sha256[:16] `5cc8ada49f2c4c28`).
- Ciphertext = 62 B, exactly len("Congratulations! hkcert21{" + 35w + "}") — known-plaintext model re-verified.
### Intended-path re-derivation from the planted structure (doctrine requirement)
Planted weakness = key layout `key[i:i+1]||0^15` + shared counter ⇒ all 16 slots index the SAME 256-entry
keystream table v(b) ⇒ parity collapse KS = XOR_{b in S} v(b), |S| <= 16 even: ~2^75.5 answers vs 216 known KS
bits ⇒ unique candidate. The wall was NOT priced at the generic 2^128. Floor re-derived independently this audit:
MITM half C(256,8) ≈ 2^48.7 (Schroeppel–Shamir space 2^25); Wagner/BDJ inapplicable (need lists >= 2^{128/(1+log2 16)}
= 2^25.6, we have 2^8 per list); ISD/lattice degenerate to the same exponent in the sparse regime (expected
solutions 2^{75.5-128} << 1 kills representation-style speedups); no GF(2)-linear shortcut through AES internals.
Intended path per the statement's own text ("reuse the solve script last year"; blog hint "OSINT master"): the
reused original-HKCERT flag string on a flag-form archive card — which the 59-solve/0-solution counter is fully
consistent with, and which the FLAG PROVENANCE rule forbids (not opened).
### Per-requirement
- Cipher model + experimental validation (slot-table equality over all 256 bytes; model reproduces self-generated
  ciphertexts): **have**
- Known plaintext 216 bits + target ciphertext + length-consistency: **have** (live re-verified)
- Toy-validated parity-subset MITM + uniqueness argument: **have** (probe.py)
- Sub-2^50 algorithm: **missing** (best-known generic floor in the sparse k-XOR regime ≈ 2^48.7 AES-block ops)
- Cluster-scale compute + external sort for that MITM: **missing**
- Provenance-permitted flag source on the intended (OSINT) route: **missing by rule**
### ONE next move
Ask the user the single governance decision: on FLAG-FORM ctf-archive cards, does the provenance rule permit
submitting the historically circulating original-CTF flag string (the card's own intended OSINT route)?
YES → one search + submit + API-verify. NO → card is permanently rule-blocked (self-derivation path = documented
cluster-scale 2^48.7); record and move on. No other experiment can change the outcome.
### Verdict
Prior 2026-10-30 evidenced-negative VALIDATED: the wall prices the planted structure (2^48.7, not generic 2^128)
and the intended path is re-derived from the statement itself; the only thing separating SOLVED-by-intent from
permanently-rule-blocked is the governance answer above.

---

# SOLVED (2026-11-06) — 251-bit ASCII leak turns the "wall" into a GF(2) linear solve

**Flag (derived, accepted):** `[flag — recorded in FLAGS/ctf-archive/challenge-298-cryptohack-tenet_the_plagarism-hkcert_ct/flag.txt]`

## What the earlier passes got wrong
Both prior analyses counted only the 216 whole-byte known bits and treated the 35 interior bytes as
8-bit unknowns usable only as a post-hoc set filter. But `\w` = `[0-9A-Za-z_]` is pure ASCII: **bit 7 of
every interior byte is exactly 0**, so each interior byte contributes one exact keystream-bit equation.
Exact known keystream bits: 208 (prefix) + 35 (interior MSBs) + 8 ('}') = **251**. That was never a
set-membership hint; it is linear information. The 2^48.7 Schroeppel–Shamir / ISD pricing priced OUR
parity-subset formulation under 216 bits, not the true 251-bit regime.

## The attack (milliseconds; no MITM, no cluster)
Parity collapse (probe.py): KS = XOR_{b in S} v(b), S = key bytes with odd multiplicity, |S| <= 16 even,
v(b) = 64-byte keystream of AES-128-CTR key b||0^15. With indicator vector u in GF(2)^256 (u[b]=1 <=> b in S),
every known bit (byte j, bit t) is the equation sum_b u[b] * v(b)[j]_t = D[j]_t. The system
M u = D, **251 x 256, rank 251** (verified on twins and on the real ct), leaves a 5-dim solution coset:
32 vectors. Keep weight <= 16 even => **unique** S (expected spurious solutions ~ C(256,<=16)*2^-251 ~ 2^-167).
Keystream from S decrypts all 62 bytes; padding S with duplicate byte pairs rebuilds a full 16-byte key.

## Synthetic-twin gate (run FIRST, before the real ciphertext) — `solve.py --synth`
5 trials, same 62 B model ("Congratulations! hkcert21{" + 35w + "}"), fresh random 16-byte keys:
every trial rank=251, coset dim=5, exactly **1** weight<=16 candidate, true parity set recovered,
decrypt == original plaintext, padded key re-encrypts to the exact twin ciphertext. `SYNTHETIC TWIN: ALL OK`.
The gate earned its keep: it caught two implementation bugs (a double flag-prefix in the generator;
padding that added two distinct bytes instead of a duplicate pair) before any real-data claim was made.

## Real run — `solve.py --real`
rank=251, coset dim=5, 32 solutions enumerated, weight<=16 even candidates: **1** (weight 14).
Plaintext: `Congratulations! [flag — recorded in FLAGS/ctf-archive/challenge-298-cryptohack-tenet_the_plagarism-hkcert_ct/flag.txt]` (interior = 35 \w chars, regex fullmatch).
End-to-end: recovered parity set padded to a 16-byte key `0c3e626681aebcbfc3c6c9ced9f4ffff` re-encrypts the
plaintext to the **exact 62-byte statement ciphertext**.

## Submission + acceptance (2026-11-06)
`python submit_flag.py tenet_the_plagarism-hkcert_ct '<flag>'` from the workspace root returned
`{"ok": true, "status": 200, "body": "Flag submitted. ..."}`, solved counter 305 -> 306.
User-API readback confirms the entry by name: `{"category": "CTF Archive", "date": "06 Nov 2026",
"name": "Tenet: The Plagarism (HKCERT CTF)", "points": 0, "solves": 60}` (archive cards award 0 points;
the counter + named entry are the acceptance proof, matching the sus-imaginaryctf2023 precedent).

## PATH WALKED (provenance)
**SELF-DERIVED.** Flag computed from the statement ciphertext alone: table build -> 251-row GF(2)
RREF -> 32-candidate coset -> weight filter -> XOR decrypt -> regex, gated by a synthetic twin
before the real run. The author postmortem (mystiz.hk/posts/2021/2021-11-18-hkcert-ctf-2) is cited
as the technique pointer named in the dispatch; it was NOT opened, and no writeup, solves page, or
circulating flag string was searched, retrieved, or consulted at any step. Any coincidence with the
historical 2021 flag is inherent (the CTF's answer is fixed) — it is not the source; the source is
this run's ciphertext-only derivation, reproducible with `solve.py` and nothing else.

## Corrections to the record
- "Sub-2^50 algorithm: missing" — superseded; the missing ingredient was counting the interior MSBs.
- "216 known bits" — undercount; the planted `\w` constraint yields 251 exact bits.
- The governance question (OSINT route) is moot: the self-derivation path closes the card.

## Files (this pass)
- `solve.py` — keystream table, RREF solver + coset enumeration, `--synth` twin gate, `--real` run, writes `flag.txt`
- `flag.txt` — derived flag (written only after format check + end-to-end re-encryption check)

## Learning point
An alphabet constraint (`\w`, `[a-z]`, hex, base64...) is per-bit information before it is a filter:
count EXACT leaked bits per character class (ASCII families leak the top bit(s); hex leaks 4 bits)
and re-check the known-bit budget against the unknown budget before pricing any sparse-solution
attack. Here 35 leaked single bits turned 2^48.7 into a 32-vector enumeration.
