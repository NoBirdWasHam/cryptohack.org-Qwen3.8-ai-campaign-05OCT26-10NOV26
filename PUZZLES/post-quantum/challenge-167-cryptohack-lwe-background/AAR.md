# AAR — LWE Background (challenge-167-cryptohack-lwe-background)

## 1. Result
**SOLVED** — answer `[flag — recorded in FLAGS/post-quantum/challenge-167-cryptohack-lwe-background/flag.txt]` (BARE answer-type: no wrapper), submitted via `submit_flag.py` on 2026-10-12 and live-confirmed in the user API (present in the 137 solved-challenges list as of 2026-10-13).

## 2. Source
- Statement: https://cryptohack.org/challenges/post-quantum/lwe-background/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

## 3. The answer + verification
- `[flag — recorded in FLAGS/post-quantum/challenge-167-cryptohack-lwe-background/flag.txt]`
Answer-type (BARE, no wrapper). Conceptual: the LWE problem was introduced by **[flag — recorded in FLAGS/post-quantum/challenge-167-cryptohack-lwe-background/flag.txt]** (STOC 2005).
- Submitted `[flag — recorded in FLAGS/post-quantum/challenge-167-cryptohack-lwe-background/flag.txt]` bare; accepted.

## 4. Toolchain
- Python 3.12 (~/tools/crypto-ctf/venv/Scripts/python.exe); numpy for the lattice det; PARI gp64 for mod-p polynomial roots (polrootsmod(Pol([...],x), p) — note: takes a Pol, not a coefficient list).
- Sibling solver: ../isogeny_answers.py (shared j-invariant code, sanity-verified against j(x^3+x)=1728).

## 5. Learning points
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).
## Vulnerability (plain words)
None — this is an answer-type (background/theory) challenge with no service, no crypto object, and nothing to break. It asks a single factual question about the history of the field: who introduced the Learning With Errors problem. The honest classification is "knowledge retrieval", and the run's product is knowing the citation, not an attack.

## How the answer follows
1. LWE was introduced by [flag — recorded in FLAGS/post-quantum/challenge-167-cryptohack-lwe-background/flag.txt] in "On lattices, learning with errors, random linear codes, and cryptography" (STOC 2005) — the founding reference for the entire LWE-based post-quantum line the following challenges build on.
2. That is exactly what the statement asks for, so the answer string is the name: `[flag — recorded in FLAGS/post-quantum/challenge-167-cryptohack-lwe-background/flag.txt]`.
3. Format was part of the derivation: answer-type challenges here accept the BARE value (no `crypto{}` wrapper) — confirmed by live acceptance via submit_flag.py on 2026-10-12 and presence in the user API solved list (2026-10-13).

## Limitations / attempts that failed
- A wrapped-form submission (`crypto{...}`) was rejected on earlier attempts before the bare form was accepted; the exact earlier attempt strings are not recorded in run logs beyond that fact.
- Housekeeping for accuracy (adds nothing, changes nothing): the j-invariant / Montgomery-curve / PARI-polrootsmod learning points in section 5 above pertain to sibling answer-type challenges worked in the same session, not to this LWE-history solve.

## Sources
- [flag — recorded in FLAGS/post-quantum/challenge-167-cryptohack-lwe-background/flag.txt], "On lattices, learning with errors, random linear codes, and cryptography", STOC 2005 — public academic reference about the math/history (explicitly permitted category under source-disclosure rules; not a challenge solution).
- Statement: https://cryptohack.org/challenges/post-quantum/lwe-background/ (cached in challenge_meta.json).
- CryptoHack solutions/solves pages NOT consulted (self-solve rule).
