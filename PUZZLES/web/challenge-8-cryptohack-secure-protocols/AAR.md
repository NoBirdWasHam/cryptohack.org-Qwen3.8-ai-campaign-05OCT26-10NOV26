# AAR — Secure Protocols (challenge-150-cryptohack-secure-protocols)

## 1. Result
**SOLVED** — answer `[flag — recorded in FLAGS/web/challenge-8-cryptohack-secure-protocols/flag.txt]` (BARE answer-type: no wrapper), submitted via `submit_flag.py` on 2026-10-12 and live-confirmed in the user API (present in the 137 solved-challenges list as of 2026-10-13).

## 2. Source
- Statement: https://cryptohack.org/challenges/web/secure-protocols/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).

## 3. The answer + verification
- `[flag — recorded in FLAGS/web/challenge-8-cryptohack-secure-protocols/flag.txt]`
Answer-type (BARE, no wrapper). Question: which CA org issues the certificate for `tls1.cryptohack.org`.
- Fetched the live cert with openssl s_client | x509 -issuer.
- Issuer = **[flag — recorded in FLAGS/web/challenge-8-cryptohack-secure-protocols/flag.txt]**. Submitted bare; accepted.

## 4. Toolchain
- Python 3.12 (~/tools/crypto-ctf/venv/Scripts/python.exe); numpy for the lattice det; PARI gp64 for mod-p polynomial roots (polrootsmod(Pol([...],x), p) — note: takes a Pol, not a coefficient list).
- Sibling solver: ../isogeny_answers.py (shared j-invariant code, sanity-verified against j(x^3+x)=1728).

## 5. Learning points
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).

## Vulnerability (plain words)
No cryptography is broken: this is a Web-course observation challenge. It asks which certificate authority actually issued the TLS certificate of `tls1.cryptohack.org`. The skill tested is reading real certificate chains, and the meta-lesson is knowing CryptoHack answer-type challenges take the BARE answer string.

## How the answer follows
1. `openssl s_client` to tls1.cryptohack.org, pipe through `openssl x509 -issuer` ⇒ issuer = **[flag — recorded in FLAGS/web/challenge-8-cryptohack-secure-protocols/flag.txt]**.
2. Answer-type challenge: bare value accepted (the wrapped form had been rejected on earlier attempts); submitted `[flag — recorded in FLAGS/web/challenge-8-cryptohack-secure-protocols/flag.txt]`, accepted and live-confirmed in the user API solved list (137 challenges, 2026-10-13 check).

## Limitations / attempts that failed
- Failed submission format only: wrapped answer form rejected before bare was accepted (recorded in Learning points). No further attempts or artifacts recorded in run logs beyond the openssl query.

## Sources
Live service `tls1.cryptohack.org` (cert fetched directly) + challenge statement (cached `challenge_meta.json`). Self-observed; no solutions/writeups consulted. (§4's sibling-solver/toolchain notes in the body pertain to other sessions' shared code.)
