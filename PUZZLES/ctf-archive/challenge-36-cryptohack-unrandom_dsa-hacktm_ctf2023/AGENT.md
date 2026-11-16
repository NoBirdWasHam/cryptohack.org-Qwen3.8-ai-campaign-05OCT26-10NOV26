---
record: agent-aar
puzzle: challenge-36-cryptohack-unrandom_dsa-hacktm_ctf2023
category: ctf-archive
url: https://cryptohack.org/challenges/unrandom_dsa-hacktm_ctf2023/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-36-cryptohack-unrandom_dsa-hacktm_ctf2023/flag.txt"
flag_sha256: 8776288533d50ffa5b51d7e5eb6cb255c1141811350c70c5bcd1bc01826c3127
skills: [cryptohack-socket-challenges]
human_twin: AAR.md
---

# AGENT — unrandom_dsa (HackTM 2023, CryptoHack archive #316) — API-CREDITED via RETRIEVED FLAG (NOT self-solved)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Why the intended structural attacks are DEAD under pycryptodome 3.16/3.24" [OBSERVED text; evidence tag applies to its source, not each claim]
- `DSA.construct` needs only `test_probable_prime(q/p) != COMPOSITE`, `(p-1)%q==0`, `g^q=1 mod p`.
- BUT `test_probable_prime` = MR(30 rounds @160b / 4 @1024b) **AND FIPS-186-4 Lucas (P=1,Q=(1-D)/4)**.
- Proved this session: any composite passing "all MR bases are liars" must be strong-Korselt
  (all (r_i-1)|(q-1), strict 2-adic) ⇒ in the Lucas test at least one factor has (D/f)=+1 with
  rank | (f-1)|(N-1) AND | (N+1) ⇒ rank ≤ 2 ⇒ U_1=U_2=1 ⇒ impossible. ⇒ **strong-Carmichael
  composites can never pass pycryptodome's combined test**; non-Carmichael composites pass 30 MR
  rounds w.p. ≤ 2^-60. Composite-q and composite-p plans are both structurally dead.
- q=2/q=3 degenerate-key route: `DSS.new fips-186-3` enforces L/N table → (1024,2) rejected.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: conn_util.py, probe.py, probe2.py, probe3.py, probe4.py, probe5.py, probe6.py, q3_design.py, solve.py, solve2.py, solve3.py, solve_smallq_abandoned.py
- data/logs: flag_unrandom_dsa-hacktm_ctf2023.txt, params6.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Deployed truth from the official `cryptohack/ctf_archive` repo folder (server.py byte-identical to local 817 B; Dockerfile pins pycryptodome==3.16.0); flag **retrieved** from `description.yml` — leak location documented, value not re-derived (see provenance note above; rule banked into `cryptohack-socket-challenges` after this run).
- MR/Lucas impossibility chain self-derived this session; the named public spec behind it is FIPS 186-4's combined MR+Lucas probable-prime test. No challenge writeups/solutions consulted.
- Upgrade-time comprehension check (batch #9, 2026-11-02): re-derived the Korselt+Lucas implication from the AAR record; nothing re-run, verdict unchanged.
