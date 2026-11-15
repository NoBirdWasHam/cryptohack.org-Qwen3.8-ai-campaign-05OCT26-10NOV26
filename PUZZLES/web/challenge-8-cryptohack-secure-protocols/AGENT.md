---
record: agent-aar
puzzle: challenge-150-cryptohack-secure-protocols
category: web
url: https://cryptohack.org/challenges/secure-protocols/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/web/challenge-8-cryptohack-secure-protocols/flag.txt"
flag_sha256: 5ba156703098d0c33fdaa743d4306235a901b339bcf449c469f6c9fd58d1abfd
skills: []
human_twin: AAR.md
---

# AGENT — Secure Protocols (challenge-150-cryptohack-secure-protocols)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
No cryptography is broken: this is a Web-course observation challenge. It asks which certificate authority actually issued the TLS certificate of `tls1.cryptohack.org`. The skill tested is reading real certificate chains, and the meta-lesson is knowing CryptoHack answer-type challenges take the BARE answer string.

## reusable-rules
- CryptoHack **answer-type** challenges accept BARE values (no wrapper) — the wrapped form was rejected on earlier attempts; bare was accepted.
- j-invariant by invariants (b4=2a, b6=4b, b8=-a^2 b): j = c4^3 / D — no point arithmetic needed, works for any short Weierstrass curve mod p.
- Montgomery j(A) = -64(A^2-3)^3 — derive b2..b8 from a1=a3=1, a2=A; the a3^2 term makes b4=2 (a common off-by-one).
- PARI polrootsmod requires Pol(coeffs, x), not a bare list (t_VEC error otherwise).

## anti-patterns / limits
- Failed submission format only: wrapped answer form rejected before bare was accepted (recorded in Learning points). No further attempts or artifacts recorded in run logs beyond the openssl query.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/web/secure-protocols/ (cached in `challenge_meta.json`)
- **NOT consulted:** solutions/writeups (self-solve rule).
