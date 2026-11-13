---
record: agent-aar
puzzle: challenge-249-cryptohack-authentification_2-breizh_ctf
category: ctf-archive
url: https://cryptohack.org/challenges/authentification_2-breizh_ctf/
status: solved
date: 2026-10-31
flag_ref: "FLAGS/ctf-archive/challenge-249-cryptohack-authentification_2-breizh_ctf/flag.txt"
flag_sha256: 1ed285b174ebd7cf2055c86e73d30e06d4ab5d9f24be7a1770108d5a5e43f92c
skills: []
human_twin: AAR.md
---

# AGENT — authentification_2-breizh_ctf (challenge-249)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (same root cause as v1)" [OBSERVED text; evidence tag applies to its source, not each claim]
Intern's GCM: `encrypt()` calls `gctr(J0, P)` instead of NIST's `gctr(inc(J0), P)`, while
the tag mask is `E(J0)` (`build_tag` → `gctr(J, S)` with J=J0). So the first keystream
block equals the tag mask: `E(J0) = P[0:16] ⊕ C[0:16]` — known (we choose the username,
JSON layout fixed). One registered token then gives `S = tag ⊕ E(J0)` = exact GHASH_H output.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Earlier draft (solve2.py + ff_probe.py) re-implemented root splitting via Artin-Schreier
  and died on "AS failed" assertion (bad square-root extraction in GF(2^128)). Abandoned
  per loop-guard in favor of porting v1's field code (trace-splitting) — worked immediately.
- 2-root ambiguity is inherent (quartic GHASH eq); resolved by server oracle, as in v1.

Method references: NIST SP 800-38D (textbook AES-GCM); low-degree root finding over finite
fields (gcd with x^q−x + Berlekamp-style trace splitting). No solutions/writeups consulted.

## artifacts [OBSERVED]
- code: _t1.py, _t2.py, _t3.py, ff_probe.py, solve.py, solve2.py
- data/logs: flag_authentification_2-breizh_ctf.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Platform: CryptoHack, ctf-archive card 'Authentification 2 (Breizh CTF)' (challenge file per site.md).
- Statement provenance: statement.txt in folder (begins: "Authentification 2 (Breizh CTF) — 79 solves, contributed by skilo  Damn, I'd for...")
- Provided material as stored in folder: _t1.py, _t2.py, _t3.py, authentification-2.zip, ff_probe.py, flag_authentification_2-breizh_ctf.txt, solve.py, solve2.py
- Not consulted: /solutions/ pages, third-party writeups (campaign no-cheat rule).
