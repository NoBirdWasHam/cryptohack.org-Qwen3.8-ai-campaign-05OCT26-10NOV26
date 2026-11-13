# AAR — schneierfact842_2 "Bruce Schneier's Password: Part 2" (misc 250) — SOLVED 2026-10-22 (+250)

Flag: `[flag value withheld — real-flag strings live only under FLAGS/]` (listener socket.cryptohack.org:13401; submit ok:true, score_delta 250)

## The check
`array = np.array(list(map(ord, password)))`; accept iff `isPrime(int(array.sum()))` and
`array.sum() == array.prod()` (np.int64, server = 64-bit Linux → product wraps mod 2^64).
Part 1 only needed prod to be *prime* (random search sufficed); Part 2 demands prod == sum,
so random search is dead (2^-64 hit rate) — structure is required.

## Attack
1. **Parity forcing.** sum is exact (no overflow at sane lengths) and prime ⇒ odd.
   If any char code is even, prod ≡ 0 mod 2^v2 with v2 ≥ 1 ⇒ prod mod 2^64 is even ⇒ can't
   equal an odd prime. So **every code must be odd**.
2. **Work in G = (1+4Z)/2^64 = ⟨5⟩, cyclic of order 2^62.** Restrict the alphabet to codes
   ≡ 1 mod 4 (digits 1,5; upper A,E,…,Y; lower a,e,…,y — all classes present).
   Condition: p_base · Π ρ_j^{k_j} ≡ S (mod 2^64), S = sum prime.
3. **Sum-preserving swaps.** Vectors v with Σ v[c]·c = 0 (e.g. +53+101−65−89, equal-sum pairs)
   change the product by ρ = Π c^{v[c]} while keeping S fixed. Discrete log base 5
   (bit-lifting, mathlib.log5) turns the condition into a linear congruence
   Σ k_j·λ_j ≡ log5(S/p_base) (mod 2^62).
4. **2-adic valuation gate.** For equal-sum pairs in this pool, ρ ≡ 1 mod 8 always
   (sum mod 8 fixes #codes≡5 mod 2), and empirically min v2(λ) = 2 ⇒ need
   S ≡ p_base (mod 16); enforce by adding d1·'1' + d2·'a' copies (both codes ≡ 1 mod 16,
   so p mod 16 is invariant while S mod 16 = S0 + d1 + d2) and searching for prime S.
   Then solve mod 2^60 with odd λ' = λ/4.
5. **Small k via CVP** (fpylll, BKZ-40 + CVP.closest_vector): lattice rows (2^60,0..0),(λ'_j,e_j),
   target (T',0..0). J=24 swaps ⇒ |k| ~ 2^{60/25} ≈ 5, so base inventory 30/char suffices.
6. Result: 433-char password, S = 35617 (prime), prod mod 2^64 == S. Verified locally with
   int64 emulation, then live: banner → {"password": pw} → flag.

## Key numbers
- Pool: 14 codes ≡1 mod 4; 36 min-v2(λ)=2 swaps available; J=24, INV=30, |k|max=5.
- S = 35617, password length 433 (listener limit: **1024 bytes/message** — first 9601-char
  solution got the connection dropped; v2 minimized length via bigger J, smaller inventory).

## Learning points
- "prod == sum" under int64 wrap = a discrete-log-in-(Z/2^64)* problem; parity kills even codes.
- Equal-sum pair swaps convert "fix the sum" into a free lattice move — the sum constraint
  becomes automatic and only one congruence (mod 2^62) remains.
- v2 of the λ_j gates which S classes are reachable (here S ≡ p_base mod 16); pick the
  adjustment characters in 1+16Z so the gate stays satisfiable while hunting a prime S.
- CryptoHack listener hard-caps messages at 1024 bytes ("You may send up to 1024 bytes per
  message." / silent reset) — budget password length from the start; more swap vectors (larger
  J) shrinks |k| as det^{1/(J+1)} and thus the required inventory.

## Limitations
- `/challenge/<slug>/` URLs 404'd (even for solved part 1); statement was taken from the
  /challenges/misc/ index HTML instead — file + port confirmed from there.
- The 2-vs-2 swap family provably gives ρ ≡ 1 mod 8 (v2(λ) ≥ 2); I did not explore 3-vs-3
  swaps to try to reach v2 = 1 (would have relaxed the mod-16 gate to mod-8 — unnecessary here).
- No third-party writeups consulted (brief rule); group-theory facts (5 generates 1+4Z mod 2^n,
  order 2^{n-2}) are standard textbook (cf. HPS / Rosen), verified computationally in mathlib.py.

## Files
- mathlib.py (log5, swap search), solve.py (v1, 9601 chars — over msg limit),
  solve2.py (final, 433 chars), password.txt, listen.py (listener client),
  13401_ec4ac92cc54df2ed096a0acee93be11e.py (challenge file, copied from challenge-189b),
  statement.txt, site.md, flag_schneierfact842_2.txt

## Source (section added by 2026-11-09 corpus audit — AAR body text unchanged)
- Platform: CryptoHack, ctf-archive card 'Bruce Schneier's Password: Part 2' (challenge file per site.md).
- Statement provenance: statement.txt in folder (begins: "Bruce Schneier's Password: Part 2 (misc, 250 pts) https://www.schneierfacts.com/...")
- Provided material as stored in folder: 13401_ec4ac92cc54df2ed096a0acee93be11e.py, flag_schneierfact842_2.txt, listen.py, mathlib.py, password.txt, solve.py, solve2.py, statement.txt
- Not consulted: /solutions/ pages, third-party writeups (campaign no-cheat rule).
