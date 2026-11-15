# Course lesson — Moving Problems (Elliptic Curves)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Elliptic Curves as challenge `moving`.
**Status:** completed 2026-10-07 · **Points:** 150 · **Site:** https://cryptohack.org/challenges/moving/
**Ledger row:** `course__moving_problems` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Moving Problems (moving), CryptoHack Elliptic Curves course (final lesson)

**Status:** SOLVED + API-verified (count 83→84, score 3420→3570, 2026-10-07)
**Flag:** ``flag — recorded in COURSEWORK/ecc/course-moving/flag.txt``
**No writeup consulted.** Attack derived from the provided `source.sage` + number theory.
**No Docker** — plain Python 3 (gmpy2, pycryptodome) + PARI/GP (`~\tools\gp64.exe`).

## Setup

ECDH over `E: y² = x³ − 35x + 98` on `F_p`, `p = 1331169830894825846283645180581` (101-bit prime).
Alice/Bob keys `(n,P=n·G)`, shared secret `x(P1·n_b)`, AES-128-CBC flag (key = SHA1(str(secret))[:16]).
We know `G, P1, P2, iv, ciphertext` — need Alice's `n_a` (or the shared secret).

## The group structure (the crux — and where I first went wrong)

- Full curve order `#E = 1331169830894823538756977170156 = 2²·7·271²·23687²·q`, `q = 1153763334005213`.
- **But the generator `G` does NOT have order `#E`.** `order(G) = og = 2·7·271·23687·q = 103686954799254136375814`.
  (Verified in Python: `og·G = O`, and `(og/r)·G ≠ O` for every prime `r | og`.)
  The DH protocol runs in the cyclic subgroup `<G>` of order `og`, not all of E(F_p).
- `og = q · M2`, with `q = 1153763334005213` (51-bit **prime**) and `M2 = 2·7·271·23687 = 89868478` (27-bit, **smooth, squarefree**).

## Why it's solvable (MOV)

`q | (p+1)` ⇒ the `q`-torsion has **embedding degree k = 2**, so the Weil pairing
`e_q: E[q] × E[q] → F_{p²}*` maps the (51-bit) ECDLP in the `q`-subgroup to a 51-bit DLP in
`F_{p²}*` (order `p²−1`, which contains `q`). That is the **MOV attack** — the "taste just like
pairs" hint. The smooth `M2`-subgroup DLPs are trivial (max prime factor 23687).

## Attack (solve.py)

Recover `n_a mod og = CRT(n_a mod q, n_a mod M2)` (gcd(q,M2)=1):

1. **M2-part (Pohlig–Hellman):** subgroup generator `Gm = (og/M2)·G = q·G` (order M2);
   target `P1M = (og/M2)·P1 = (n_a mod M2)·Gm`. For each prime `r | M2` (all e=1), BSGS/scan in the
   `r`-subgroup for the digit; CRT over `{2,7,271,23687}`. → `n_a mod M2 = 32135505`
   (self-check `na_M·Gm == P1M` passed).
2. **q-part (BSGS):** subgroup generator `H0 = (og/q)·G = M2·G` (order q, confirmed `q·H0 = O`);
   target `P1q = (og/q)·P1 = (n_a mod q)·H0`. BSGS with `m = ⌈√q⌉ ≈ 3.4×10⁷` (2²⁵.⁵): baby table
   ~73 s, giant hit at 67% → `n_a mod q = 774386641791944` (50 bits). (Chose direct on-curve BSGS
   over implementing Miller's algorithm: robust, ~2 min on 64 GB RAM, no pairing-code fragility.)
3. **CRT:** `n_a = 29618469991922269` (55 bits).
4. **Verify:** `n_a·G == P1` ✅ (this is the ground-truth check that `n_a` is Alice's real key).
5. **Decrypt:** `secret = x(n_a·P2) = 57514367079882430785803122958`; key = SHA1(str(secret))[:16];
   AES-CBC decrypt + unpad → ``flag — recorded in COURSEWORK/ecc/course-moving/flag.txt`` (clean PKCS7 = valid key).

## Learning / takeaways (for the skill)

- **Check the generator's order, not just the curve's.** The trap here: `G`'s order `og` is a
  proper divisor of `#E`. All subgroup arithmetic must be done in `<G>` (order `og`), so the
  coprime split is `og = q·M2` with `M2 = 2·7·271·23687`, NOT `#E = q·(q−1)`. Recovering `n mod og`
  is all the shared secret needs (`S = (n·P2)` only depends on `n mod order(P2)`).
- **MOV recipe:** factor `order(G)`; for each prime-power part, compute embedding degree
  `k = ord_r(p)` (smallest `k` with `p^k ≡ 1 mod r`). `k` small (1–3) ⇒ pairing attacks apply;
  smooth/small parts ⇒ Pohlig–Hellman / BSGS. Here `k=2` for the 51-bit `q`.
- **Direct BSGS is a perfectly good "MOV-lite"**: for a 51-bit prime subgroup, 2²⁵.⁵ on-curve
  BSGS is a couple of minutes with RAM to spare and avoids implementing/validating Miller's
  algorithm. (Pairing is the *concept*; BSGS-in-F_{p²}* or BSGS-on-the-curve both close the gap
  at this size.)
- **PARI/GP pitfalls (this build is old/custom):** `#` is NOT a comment (it's an operator — `#E`
  mis-parses, and inline `# comment` breaks files); `typeof`, `getinfo`, `bitnumber`, `Now` are
  missing; `ellcard` works; **`elllog` is a STUB (returns 0 for everything)** and `ellbilag`/
  `ellpairing`/`ellweilpairing` are unreliable — do DLPs in Python with gmpy2, use PARI only for
  `ellcard`/`ellinit`/point arithmetic.
- **`ecdsa`/curve libraries: `order`, `generator`, `curve` are attributes, not methods**;
  `Point.mul_add` is `(self_mul, other, other_mul)`; point-at-infinity `.x() is None`.
- **PH digit recovery:** for squarefree `M`, each prime is one digit (BSGS in the `r`-subgroup).
  `2P=O` for 2-torsion ⇒ guard `dbl` on `y==0`.

## Verification (no cheating)

- `n_a·G == P1` (recovered key reproduces the public key) — independent of any server.
- AES-CBC decrypt yields valid PKCS7 + a well-formed flag.
- Submitted via the logged-in flag form; API `/api/user/NoBirdWasHam/` shows "Moving Problems" in
  the solved list, count 84, score 3570. **This was the final lesson of the Elliptic Curves course.**


## Limitations / attempts that failed
- First-pass modeling error (corrected in-run): assumed order(G) = #E. In fact order(G) = og is a
  PROPER divisor of #E; all subgroup splits must use og = q·M2 (verified og·G = O and (og/r)·G ≠ O
  for every prime r | og).
- Toolchain: this PARI/GP build's `elllog` is a stub (returns 0) and the pairing functions
  (ellbilag/ellpairing/ellweilpairing) are unreliable — the 51-bit q-subgroup DLP was closed by
  direct on-curve BSGS (2^25.5, ~2 min) instead of implementing Miller's algorithm. Deliberate
  trade-off: the pairing is the concept; BSGS achieves the same reduction at this size.
- No other failed attempts logged; offline ground-truth check n_a·G == P1 passed.

## Sources
Provided `source.sage`; self-derived (group-order factoring, Pohlig–Hellman, BSGS, CRT); PARI/GP
gp64 build quirks documented in-run; no writeups consulted.

