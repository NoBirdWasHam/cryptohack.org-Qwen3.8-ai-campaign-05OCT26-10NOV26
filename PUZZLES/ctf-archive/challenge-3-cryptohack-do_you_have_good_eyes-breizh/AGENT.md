---
record: agent-aar
puzzle: challenge-256-cryptohack-do_you_have_good_eyes-breizh
category: ctf-archive
url: https://cryptohack.org/challenges/do_you_have_good_eyes-breizh/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/ctf-archive/challenge-3-cryptohack-do_you_have_good_eyes-breizh/flag.txt"
flag_sha256: a733fc30abb1832324f94f164e8c615ab2344cdf499586682ea0b55ec87d59f6
skills: []
human_twin: AAR.md
---

# AGENT — do_you_have_good_eyes-breizh (Breizh CTF / CryptoHack archive, port 43607)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
The parameters are "real" Dilithium-5, but the challenge is a *ring with zero-divisors
that splits completely*: q−1 = 2^13·3·11·31, so x^256−1 has all 256 roots in F_q, and
in particular x−1 | x^256−1. Evaluation at x=1 is then a ring homomorphism
φ: R_q → F_q, φ(p) = Σ_k p_k (sum of coefficients). Homomorphisms are supposed to
preserve nothing useful to the attacker — but here the secret and error have
SMALL INTEGER coefficients, and φ turns the ring equation
    t = A·s + e   into  8 scalar equations over F_q:
    T_m := t_m(1) = Σ_j A1_{mj}·σ_j + μ_m (mod q),  A1_{mj} = A_{mj}(1),
where σ_j = s_j(1) = Σ_k s_j[k] and μ_m = e_m(1) are still small INTEGERS
(|σ|,|μ| ≤ 512 — sum of 256 values in [−2,2]). For a uniform t the same equations
exist only if some small box point (σ,μ) satisfies them: with 15 unknowns in a
box of 1025 and 8 equations mod q, expected number of false solutions
≈ 1025^15 / q^8 ≈ e^−24 ≈ 4e−11. So: MLWE ⇒ tiny CVP instance has a solution;
uniform ⇒ essentially never. One shot per round, error ~1e−10 both directions.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- The x=1 projection kills all ring structure; on real Dilithium the secret is not
  recoverable this way only because the real e is binomial and s1,s2 ranges are
  larger... (NOT the true reason: for THIS instance type, both s and e have the
  same tiny box, which makes the projected problem massively overdetermined.
  For FIPS-204 Dilithium, η=2/η2=32 boxes make σ,μ up to 512·(16)… projected
  box q-ratio no longer tiny; the break is specific to e being as small as s.)
  Did not test against a hardened variant.
- Single homomorphism (x=1) used; other divisors x^d−1 (d|256) give more
  independent equations (d=2 doubles equations; box halves per coefficient) —
  unused margin.

## artifacts [OBSERVED]
- code: dbg1.py, solve.py
- data/logs: flag_do_you_have_good_eyes-breizh.txt, game_log.json, game_out.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- HPS textbook (hps2014.txt scratch) not needed beyond cyclotomic-ring basics.
- No writeups/solutions consulted (brief compliance).
