# AAR — LWE Intro (challenge-168-cryptohack-lwe-intro)

## 1. Result
**SOLVED** — answer `[flag — recorded in FLAGS/post-quantum/challenge-9-cryptohack-lwe-intro/flag.txt]` (BARE answer-type: no wrapper), submitted via `submit_flag.py` on 2026-10-12 and live-confirmed in the user API (present in the 137 solved-challenges list as of 2026-10-13).

## 2. Source
- Statement: https://cryptohack.org/challenges/post-quantum/lwe-intro/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

## 3. The answer + verification
- `[flag — recorded in FLAGS/post-quantum/challenge-9-cryptohack-lwe-intro/flag.txt]`
Answer-type (BARE). LWE intro: the technique to solve the underdetermined linear system is **[flag — recorded in FLAGS/post-quantum/challenge-9-cryptohack-lwe-intro/flag.txt]**.
- Submitted `[flag — recorded in FLAGS/post-quantum/challenge-9-cryptohack-lwe-intro/flag.txt]` bare; accepted.

## 4. Toolchain
- Python 3.12 (~/tools/crypto-ctf/venv/Scripts/python.exe); numpy for the lattice det; PARI gp64 for mod-p polynomial roots (polrootsmod(Pol([...],x), p) — note: takes a Pol, not a coefficient list).
- Sibling solver: ../isogeny_answers.py (shared j-invariant code, sanity-verified against j(x^3+x)=1728).

## 5. Learning points
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).


## Vulnerability (plain words)
None — this is a teaching/knowledge question in the LWE intro track, not a broken system. The lesson it teaches: all of LWE's hardness lives in the error term. Strip the error away and an LWE sample (A, b) is just a system of linear equations over Z_q; the secret stops being hidden and falls out of ordinary linear algebra.

## How the answer follows
The expected answer is the name of the technique: **[flag — recorded in FLAGS/post-quantum/challenge-9-cryptohack-lwe-intro/flag.txt]**. Mechanism behind it: once you have at least n linearly independent samples b_i = <A_i, s> (mod q), row-reduce the n×n sample matrix over Z_q. Because q is prime, every nonzero pivot is invertible mod q, so elimination proceeds exactly like over the reals and yields the unique solution s with no noise window, no rounding, no lattice reduction. That is the "why it works" the track is building toward: noise-free LWE = solvable linear system. (The statement text itself was not archived into site.md — the statement field in challenge_meta.json is empty — so the mechanism above is stated from the archived answer and the surrounding track content, not quoted from a stored statement.)
Answer string `[flag — recorded in FLAGS/post-quantum/challenge-9-cryptohack-lwe-intro/flag.txt]` submitted BARE (no wrapper) 2026-10-12; live-confirmed in the user API 2026-10-13.

## Limitations / attempts that failed
- Knowledge retrieval, not a derivation — no computation was performed or needed; no solve script exists for this item.
- Exact statement wording not archived (see above); beyond the recorded wrapped-vs-bare answer-format quirk (earlier attempts), nothing else failed, and no other attempts are recorded in run logs.

## Sources
- Course statement page https://cryptohack.org/challenges/post-quantum/lwe-intro/ (URL cached in site.md / challenge_meta.json).
- Course-recommended reading: Hoffstein–Pipher–Silverman, *An Introduction to Mathematical Cryptography* (general LWE/linear-algebra background; no specific passage used for this item).
- No third-party writeups or solution artifacts consulted.
