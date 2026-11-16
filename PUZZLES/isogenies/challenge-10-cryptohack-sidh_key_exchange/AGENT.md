---
record: agent-aar
puzzle: challenge-10-cryptohack-sidh_key_exchange
category: isogenies
url: https://cryptohack.org/challenges/sidh_key_exchange/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/isogenies/challenge-10-cryptohack-sidh_key_exchange/flag.txt"
flag_sha256: 9358901925ece3f08fbbd4c473539f8f30191e446e982753a528d9f8ff3c4059
skills: []
human_twin: AAR.md
---

# AGENT — challenge-216: SIDH Key Exchange (cryptohack.org, 80 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
None — the challenge hands you both secrets sA, sB and asks you to run SIDH
honestly: perform Alice's 2^110-step walk and Bob's 3^67-step walk from
E0: y² = x³ + x over F_{p²}, p = 2^110·3^67 − 1, carrying the other party's
torsion images along. The shared secret is the j-invariant of the corner curve of
the SIDH diamond; the "math" is that the diamond commutes.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- `ellj()` rejects curves over F_q (t_FR coefficients) → compute j from a4,a6 by hand.
- `for(i=a,b, s1; s2)` multi-statement bodies are a **parse error** (even single-line).
  Workaround: put the body in a function and use the `if(1, s1; s2)` single-expression idiom.
- Destructuring `[a,b] = f()` inside a `for` body mis-parses → use `iso[1]`, `iso[2]`.
- Trailing `;` before the closing `)` of `for(...)` is a parse error.
- `t_FFELT` (lift of t_FR) has no usable `polcoeff`/`lift`-to-integer path → parse the
  printed `A*w + B` form in Python instead.
- Python f-strings generating gp code must be **raw** (`rf"""`), else `\\` comments
  collapse to `\` and gp dies; `{`/`}` in f-strings need doubling.
- `lift(sqrt(Mod(-4,p)/(Mod(D,p))))` for the √; `((p+1)\ 2)` for integer division.

## artifacts [OBSERVED]
- code: decrypt_gp.py, gen_gp.py, gen_gp2.py, gpsidh.gp, gpsidh_probe.gp, gpsidh_probe2.gp, gpsidh_test.gp, gptest.gp, gptest2.gp, gptest3.gp, gptest4.gp, gptest5.gp, gptest6.gp, solve.py, t1.gp, t10.gp, t2.gp, t3.gp, t4.gp, t5.gp, t6.gp, t7.gp, t8.gp, t9.gp
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- PARI/GP 2.17 ellisogeny / ellisogenyapply over ffgen fields (docs).
- SIDH protocol structure from the challenge's own source.sage.
- No third-party writeups or solution pages consulted (run log).
