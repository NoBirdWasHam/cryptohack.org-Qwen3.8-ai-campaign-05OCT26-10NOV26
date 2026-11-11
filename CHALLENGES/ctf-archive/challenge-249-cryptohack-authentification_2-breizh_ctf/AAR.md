# AAR — authentification_2-breizh_ctf (challenge-249)

## Result
SOLVED. Flag obtained from the live service (archive.cryptohack.org:59670) by forging a
`role=super_admin` auth cookie whose GCM tag verifies; submitted, ok:true (solved count
293→294; archive = 0 pts, score_delta 0 as expected).
Flag: see flag_authentification_2-breizh_ctf.txt (distinct from v1's flag — self-derived
via exploit, provenance clean; no author/solution repos consulted).

## What differs from v1 (sibling challenge-248, solved in this archive)
`diff -r` of the two provided zips: the ONLY functional change is v2's `verif_token`
actually enforces `if not is_auth: return False` — i.e. the tag must be valid now.
gcm/gcm.py is byte-identical (the intern's bug persists).

## Vulnerability (same root cause as v1)
Intern's GCM: `encrypt()` calls `gctr(J0, P)` instead of NIST's `gctr(inc(J0), P)`, while
the tag mask is `E(J0)` (`build_tag` → `gctr(J, S)` with J=J0). So the first keystream
block equals the tag mask: `E(J0) = P[0:16] ⊕ C[0:16]` — known (we choose the username,
JSON layout fixed). One registered token then gives `S = tag ⊕ E(J0)` = exact GHASH_H output.

## Attack (port of the proven v1 solver; local test re-run against v2's crypto.py)
1. `/reset-db`, register `"a"*12`, `/login` (allow_redirects=False) → (C, tag), 43-byte PT.
2. `S = tag ⊕ (P⊕C)[0:16]`; GHASH buf = pad(C)‖0‖len(C)·8 = 4 blocks ⇒
   f(x) = X₁x⁴+X₂x³+X₃x²+L·x+S over GF(2^128).
3. Roots in GF(2^128): gcd(f, x^(2^128)+x), then split squarefree factor by absolute-trace
   gcds (128 Frobenius terms). Typically 2 candidates ⇒ 2 candidate tags; `/admin` is the
   oracle (candidate 0 failed, candidate 1 printed the flag).
4. Forged pt `{"username": "a", "role": "super_admin"}` (40 ≤ 43 known keystream bytes):
   C′ = P′ ⊕ ks, T′ = GHASH_H(C′) ⊕ E(J0). Cookie sent quoted with `\073` for `;`.

## Evidence
- Local: `python3 solve.py` → 3/3 rounds; forged tokens pass v2's `verif_token` WITH the
  is_auth check; genuine guest token correctly fails.
- Remote: `/admin` printed "Well played! ... flag" for candidate 1 on the first session.

## Limitations / failed paths
- Earlier draft (solve2.py + ff_probe.py) re-implemented root splitting via Artin-Schreier
  and died on "AS failed" assertion (bad square-root extraction in GF(2^128)). Abandoned
  per loop-guard in favor of porting v1's field code (trace-splitting) — worked immediately.
- 2-root ambiguity is inherent (quartic GHASH eq); resolved by server oracle, as in v1.

Method references: NIST SP 800-38D (textbook AES-GCM); low-degree root finding over finite
fields (gcd with x^q−x + Berlekamp-style trace splitting). No solutions/writeups consulted.

## Source (section added by 2026-11-09 corpus audit — AAR body text unchanged)
- Platform: CryptoHack, ctf-archive card 'Authentification 2 (Breizh CTF)' (challenge file per site.md).
- Statement provenance: statement.txt in folder (begins: "Authentification 2 (Breizh CTF) — 79 solves, contributed by skilo  Damn, I'd for...")
- Provided material as stored in folder: _t1.py, _t2.py, _t3.py, authentification-2.zip, ff_probe.py, flag_authentification_2-breizh_ctf.txt, solve.py, solve2.py
- Not consulted: /solutions/ pages, third-party writeups (campaign no-cheat rule).
