# AAR — twist_and_shout-ecsc_2023_nor (CryptoHack archive, ECSC 2023 Norway)

## Solved: YES
Flag: `[flag — recorded in FLAGS/ctf-archive/challenge-31-cryptohack-twist_and_shout-ecsc_2023_nor/flag.txt]` — submitted `ok:true`, solved count 261→262,
score_delta 0 (archive challenge = 0 pts, already-credited semantics per brief).
Flag provenance: derived locally from 6 oracle queries via the attack below, then
verified against three live service responses BEFORE submission. No external
writeups/solutions consulted.

## The vulnerability
Service oracle: `shout(x, d) = x([d]P)` computed by an x-only Montgomery ladder
(EFD ladd-2002-it) with **no check that x is a valid curve x-coordinate**.
E: y²=x³+x+1494 over q=2^128-159, #E prime (= claimed "secure"), but the
**quadratic twist** order
#E' = 340282366920938463461745030229583898519
   = 3 · 79 · 644899 · 1283505703 · 19385376821 · 89480282251 (squarefree).
For any x with x³+x+1494 a quadratic non-residue, the ladder faithfully computes
x([d]P) in the twist group (verified: ladder output == full E(F_{q²}) arithmetic
for the same x). Classic invalid-curve attack.

## Attack
- Model twist subgroup as E over F_{q²}=F_q[w]/(w²−ξ): twist points have
  x ∈ F_q, y = c·w; specialized addition/doubling in (x,c) coords, one
  128-bit modular inverse per group op.
- Per prime factor ℓ: generator Q=[#E'/ℓ]P for a small twist x; query oracle with
  x(Q) → xd = x([d]Q); BSGS in ⟨Q⟩ (order ℓ, B up to 299134) → e ∈ {d, −d} mod ℓ
  (x-coordinate is blind to sign).
- If the query crashes the server (`pow(0,-1)`) → d ≡ 0 mod ℓ (free info).
  (d ≡ 0 mod 79 actually happened live.)
- 2⁶ sign-combination CRT (modulus = #E' ≈ 2^128) + printable-ASCII filter →
  unique candidate d = int(b"7w1st_&&_sh0ut!") (15-byte body < 16 B, so d < #E').
- Flag = ECSC{...decoded body...}.

## Key numbers
- trace t = 1629577202184312463; #E prime; #E' smooth above.
- 6 live oracle queries total. Local solve ≈ 4 s after table build (3.6 s).
- Local validation: 20/20 round-trips against a module-level clone of the service
  logic (varying fake flags), including d≡0-mod-ℓ crash cases.

## Gotchas hit
- sympy 1.12 `crt()` returns **(solution, modulus)**, not (modulus, solution) —
  reversed unpacking silently produced 0 candidates at first.
- x-coords of the order-ℓ generators must be the oracle queries (not the base
  points P used to build them).
- Listener keeps the connection open with a prompt; must consume the initial
  "x-coordinate: " banner in connect() or every reply parses as empty.

## Limitations
- Recovers d only up to #E' ≈ 2^128: flag bodies > 16 bytes would need extra
  info not available here (design limit of the challenge; real flag fits).
- The two 35–37-bit factors need BSGS (~2×3e5 group ops); if they were any
  larger, a Pollard-rho/p-airing upgrade would be required.

## Files
- solve.py (build tables + `test` / `live` modes), live2.py (residue dump +
  CRT sweep used for the real run), statement.txt, site.md, twist_and_shout.py,
  Dockerfile (from /static/challenges/), residues.pkl.

## Sources
Sources: challenge-provided materials only; self-derived per run logs.

## Current state of the attack
Ledger-hygiene annotation (2026-11-02 twin sweep; append-only, claims untouched):
NOT a twin of `challenge-13391-cryptohack-twist_and_shout-zh3r0_ctf_v22` despite the
shared title — DISTINCT INSTANCES, one credit each. Evidence (both AARs): this
folder = ECSC 2023 Norway invalid-curve oracle attack on an x-only Montgomery ladder
over y²=x³+x+1494 mod 2^128−159 (smooth quadratic-twist order, per-prime BSGS +
sign-CRT; lines 11-31), flag ECSC{...}, readback 261→262 (line 4). 13391 = Zh3r0
CTF V2 MT19937 full-state seed leak (624 tempered words → untwist; its AAR lines
6-9), readback 253→254 (its line 30). No shared derivation, files, ports or flag
string. Both credits stand; no dedupe action.
