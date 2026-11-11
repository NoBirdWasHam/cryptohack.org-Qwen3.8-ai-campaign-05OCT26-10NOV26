# What's My Kernel (whats_my_kernel) — 70 pts, Isogenies

- URL: https://cryptohack.org/challenges/isogenies/ (listed under the isogenies category; direct challenge URL redirects — statement fetched via category page)
- Slug: `whats_my_kernel` · Challenge ID: 214
- Files (server-provided, static):
  - `https://cryptohack.org/static/challenges/source_1b6b34f345b56131770fb63819ea4435.sage`
  - `https://cryptohack.org/static/challenges/output_f0f36907a0a0be13b6587ab3cfdde72a.txt`
- Local copies: `source_real.sage`, `output_real.txt` (verified byte-identical to the static files; the older `source.sage`/`output.txt` in this folder are the same content)

## Statement (verbatim)

> Here's my SIDH public key, can you solve the isogeny problem and recover the kernel? Challenge files: source.sage, output.txt

## Setup (from source)

- `p = 2^216 * 3^137 - 1`, `F = GF(p^2, name="i", modulus=[1,0,1])` (= F_p[i])
- `E_0: y^2 = x^3 + 1` over F; `E.order() = (2^216 * 3^137)^2` (supersingular, full 2^216-torsion)
- `P, Q = E.gens()` (order N = 2^216·3^137); cofactor `c_a = c_b = 3^137`
- `P_a = Q_a-source = c_a*P, c_a*Q` (order 2^216; "a" and "b" points are identical — the planted "bug")
- Secret: `n = bytes_to_long(FLAG[7:-1])` — **FLAG inner is 27 chars, so n is up to 216 bits (27 bytes), NOT 19 hex digits**
- Isogeny: `R = P_a + n*Q_a` (order 2^216 since n is odd), `phi = E.isogeny(R)` (degree 2^216)
- Public key: `E_A = phi.codomain()`, `P_B = phi(P_b) = phi(P_a)`, `Q_B = phi(Q_b) = phi(Q_a)`

## Public data (output.txt)

- E_0, P_a, Q_a, P_b, Q_b (P_b = P_a, Q_b = Q_a)
- E_A: y^2 = x^3 + a x + b over F_{p^2}, with a, b given
- P_B = phi_a(P_b), Q_B = phi_a(Q_b)

## Flag

`crypto{whoops_this_was_just_a_dlog}` — SUBMITTED & ACCEPTED 2026-10-16 (+70; score 8135→8205, 170 solved)
