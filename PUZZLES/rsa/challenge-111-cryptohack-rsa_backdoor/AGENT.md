---
record: agent-aar
puzzle: challenge-111-cryptohack-rsa_backdoor
category: rsa
url: https://cryptohack.org/challenges/rsa_backdoor/
status: solved
date: 2026-10-24
flag_ref: "FLAGS/rsa/challenge-111-cryptohack-rsa_backdoor/flag.txt"
flag_sha256: 925e37b07a2a11fdcb372fc394475c53291765b514b1d69c9b1a2baf3cb51a10
skills: []
human_twin: AAR.md
---

# AGENT — 111-cryptohack-rsa_backdoor: RSA Backdoor Viability (CryptoHack)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
`p = (427·s²+1)/4` ⇒ **4p−1 = 427·s² is 427 times a square** (the flag pun confirms this is
the intended backdoor). Equivalently p is represented by the **principal form** x²+xy+107y²
of discriminant −427 (h(−427)=2), so p **splits completely in the ring class field** of
Q(√−427). Consequences used:
1. The Hilbert class polynomial H₋₄₂₇(x) = x² + HB·x + HC splits mod p; its roots j are
   CM j-invariants of curves with **#E(F_p) = p+1−t, t = ±1** (Frobenius π = (1+s√−427)/2,
   π+π̄ = 1; both class-group components share the same t since the two CM curves are
   3-isogenous over F_p — 3 is the inert prime carrying the nontrivial class).
2. When t = +1, #E(F_p) = p divides n = pq, so **[n]P = O mod p** for every P ∈ E(F_p) —
   an Atkin–Morain factoring oracle.

## reusable-rules
- p=(D·s²+1)/4 ⇒ p principal of disc −D ⇒ CM curve with trace ±1 ⇒ factor via [n]P over
  an étale algebra when #E(F_p) | n. The "recursion limit" hint is a red herring for this
  route.
- **Formal-Y trick:** to get a point on a curve over Z/n without sqrt mod n, adjoin Y with
  Y² := g(x0) as a formal quadratic extension; the group law never needs Y to exist in Z/n.
- Jacobi bookkeeping pins the splitting behavior: (−7/n) = −1 with (−7/p) = +1 forced
  (−7/q) = −1 ⇒ H irreducible mod q ⇒ no integer-j curve over Z/n exists — the rank-2
  algebra R is mandatory. (−427/q) = +1 ⇒ #E(F_{q²}) ∤ n, keeping the q-component alive.
- Trace t = ±1 is a coin flip; random R-twists (1/4 hit) cover t = −1.
- Composite-n exponent traps cost hours: a QR mod p AND mod q does NOT satisfy
  a^((n−1)/2) ≡ 1 mod n, and a^((n+1)/4) is not a sqrt mod composite n even for
  guaranteed squares a = k² (verified empirically, 0/20).

## anti-patterns / limits
- `gcd(α^((n−1)/2)−1, n)` battery for α ∈ {−7, 61, −427} (probe2.py/solve.py): gcd = 1.
  Reason: w_p^q ≠ w_p; α^((n−1)/2) mod p = (α/p)·α^((q−1)/2), not 1.
- Integer-root-of-H curve over Z/n (solve2.py): disc(H) is not a QR mod n because
  (−7/q) = −1 ⇒ H irreducible mod q. Dead end for this instance.
- Square root in R via y = g·x/N(g) (old solve.py/cm_attack.py): y² = g²/N ≠ g — broken;
  also sqrt in R ≡ factoring. cm_attack.py additionally used j = δ instead of j = (δ−HB)/2.
- Plain Coppersmith on 427qs²+q = 4n and univariate 427s²+1 mod p (bound N^{β²/δ} = N^{1/8}
  ≪ s ~ N^{0.25}): no slack (pre-established, not re-derived).
- Fermat/p−1/ECM, naive Frobenius gcd batteries (probe1.py): hopeless at these sizes
  (pre-established).

## artifacts [OBSERVED]
- code: cls.gp, cm_R.py, cm_attack.py, cm_fast.py, cm_formal.py, hcl.gp, probe1.py, probe2.py, selftest.py, solve.py, solve2.py, solve_cm.py
- data/logs: flag_rsa_backdoor.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Challenge:** "RSA Backdoor Viability" (175 pts, slug `rsa_backdoor`), contributed by joachim
- **NOT consulted:** `/challenges/rsa_backdoor/solutions/`, third-party writeups (no-cheat rule)
- Theory reference: Cox, *Primes of the form x²+ny²* (class field / genus theory facts); Atkin–Morain style CM factoring.
