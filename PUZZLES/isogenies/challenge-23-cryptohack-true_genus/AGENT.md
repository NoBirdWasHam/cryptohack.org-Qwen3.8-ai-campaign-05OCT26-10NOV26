---
record: agent-aar
puzzle: challenge-222-cryptohack-true_genus
category: isogenies
url: https://cryptohack.org/challenges/true_genus/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/isogenies/challenge-23-cryptohack-true_genus/flag.txt"
flag_sha256: 829c327d37948b6e80ea31466943cf7de039259dfab2aeea658626c494ea2605
skills: []
human_twin: AAR.md
---

# AGENT — true_genus — AAR (parked OPEN, 2026-10-24)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
A CSIDH-style class-group action on the j=0 orbit over F_p (p ≈ 2^155,
Cl(−4p) ≅ Z/36q), carrying a planted backdoor: backdoor(priv) XORs the signer's
exponent marks against a private vector, and with probability ~0.99 tells the
verifier that a "bit 0" instance used a resampled key avoiding those marks. The
run did NOT crack the class-group DLP (that route was killed with evidence, listed
below). The actual break is a genus-theoretic parity invariant: the quartic
residue character of the curve discriminant is a cheap, explicit character of the
class-group action that reads the parity of the action exponent — Gauss genus
theory (discriminant characters detect the 2-part of a class group), which the
flag name spells out. Combined with the source's own bit semantics, parity pins
each of the 63 SECRET bits down to a 2^26 candidate set, brute-forceable directly
through the AES check.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Character batteries (jac/quadratic/quartic/cubic of a4, a6, Delta, j−1728 over
  F_p and F_{p²}): uniform on the real instances; on the labeled testbed NO cheap
  invariant satisfied val(x) = g^x except the parity-level q4(Delta).
- Mod-3/9 extraction was proved structurally impossible for this family: the
  class action commutes with End(E) ⊇ Z[sqrt(−p)] ∋ Frob = ±sqrt(−p), so Frob on
  E[ℓ^k] (ℓ ≠ p) is class-independent up to GL2-conjugacy — cubic symbols and
  9-torsion eigenstructure carry no class info (testbed evidence + argument; one
  apparent positive was a broken psi-recurrence and was retracted).
- Mod-36 via smooth-ideal walks: minimum smooth ideal degree ≈ 2^65 (lattice
  determinant estimate) — infeasible; Pollard rho in the q-part: 2^37 class ops —
  infeasible; MITM on the 7^29 key space: 2^81 — infeasible.
- tg11's 2^27 search returned found=0 from a missing IV XOR in the CBC filter —
  a glue bug, not the math.
- An earlier session parked this as UNSOLVED after 3 solver deaths; a later
  session re-opened and solved it — the AAR's earlier status lines are historical
  record, the final section is the outcome.

## artifacts [OBSERVED]
- code: cls.gp, cls2.gp, cls3.gp, cls4.gp, cls5.gp, cls6.gp, h.gp, h2.gp, hunt2.gp, hunt3.gp, iso_t.gp, iso_t2.gp, iso_t3.gp, iso_t4.gp, orbit.gp, small.gp, small2.gp, small3.gp, t1.gp, t2.gp, t3.gp, t4.gp, t5.gp, tg10.py, tg11.py, tg12.py, tg2.py, tg4.py, tg5.py, tg8.py, tg9.py
- data/logs: flag_true_genus.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- PARI/GP bnfinit (bnf.dat cache; cls6.gp class logs of all 29 primes) for class
  group structure.
- Quartic residue symbols / genus theory: textbook-level number theory
  (knowledge retrieval stated plainly); the specific invariant was searched for
  and verified in-run on the labeled p = 1289 testbed.
- No third-party writeups or solution pages consulted (run log).
