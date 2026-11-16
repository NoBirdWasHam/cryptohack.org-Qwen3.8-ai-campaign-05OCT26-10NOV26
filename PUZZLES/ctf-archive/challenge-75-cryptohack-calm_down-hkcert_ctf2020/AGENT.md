---
record: agent-aar
puzzle: challenge-75-cryptohack-calm_down-hkcert_ctf2020
category: CTF Archive
url: https://cryptohack.org/challenges/calm_down-hkcert_ctf2020/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-75-cryptohack-calm_down-hkcert_ctf2020/flag.txt"
flag_sha256: f1dfaa1d86bbf81e4f87f9445be2224cd878a77afac4c90d7beeafad4489c7b7
skills: []
human_twin: AAR.md
---

# AGENT — calm_down (HKCERT CTF 2020, CryptoHack archive, 0 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Winning attack (solve4.py — boundary binary search, ~2.5k queries)" [OBSERVED text; evidence tag applies to its source, not each claim]
Restrict to aligned s = 128t+1: then 46(s-1) = 46·128t ≡ 0 (mod 256), so
YES(128t+1) <=> q(s) ≡ 0 (mod 256). In the region s*m < n (q=0) every
aligned probe is YES; q=1..2 give NOPE, so on the bracket P(t) = [s(t)*m < n]
is monotone:
- doubling probe t = 1,2,4,... to first NOPE t_hi (lands in the q∈{1,2}
  region; bracket lies inside (T/2, 2T) so no later q≡0 (mod 256) YES
  region can fool it);
- binary search first NOPE t* in (t_hi/2, t_hi]: m/n ∈ [1/s(t*), 1/s(t*-1));
- width·n = 128·m²/n << 1 -> unique integer candidate; verify pow(m,e,n)==c.
Remote: bracket 2^1227, 2455 queries total, 360 s, one session.
Validated first on a 1024-bit local clone (recovered planted flag in
1813 queries / 6.5 s).

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
Blocks of 256 consecutive s near 256/w; each YES gives bin [q/s,(q+1)/s]
(~8 bits per 256 queries, ~65-70k queries needed for 2048-bit n). Worked
from w=1 to w~1e-320 (local_run.log) then STALLED forever at ~57k queries:
in the small-phi regime q(s) is constant across a 256-wide window and YES
requires that constant Q even (and aligned); for odd Q the same block
(s0 = f(w) only) is retried infinitely — root cause of the predecessor's
two hung runs. solve3.py adds a parity-slide fix (on miss, shift s0 by
s0/Q to flip Q parity) but was superseded by solve4 before re-validation.

## artifacts [OBSERVED]
- code: chall_local.py, chall_local512.py, mklocal.py, solve.py, solve2.py, solve3.py, solve4.py
- data/logs: flag_calm_down-hkcert_ctf2020.txt, local_bnd.log, local_run.log, remote_bnd.log, remote_run.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Self-derived per logs from the provided `chall.py` and local clones; no CryptoHack solutions/writeups consulted (flag-provenance rule held). Conceptually the oracle-abuse pattern is Bleichenbacher-style adaptive predicates on multiplicatively blinded RSA ciphertexts — named as public background, not consulted as a solve source.
- Upgrade-time comprehension check (batch #9, 2026-11-02): re-derived the mod-256 YES predicate and the doubling-bracket monotonicity from `solve4.py` and `local_bnd.log`/`remote_bnd.log`; no new queries or submissions.
