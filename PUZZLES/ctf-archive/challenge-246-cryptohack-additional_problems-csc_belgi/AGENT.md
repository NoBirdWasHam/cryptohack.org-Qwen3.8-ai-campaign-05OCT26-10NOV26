---
record: agent-aar
puzzle: challenge-246-cryptohack-additional_problems-csc_belgi
category: ctf-archive
url: https://cryptohack.org/challenges/additional_problems-csc_belgi/
status: solved
date: 2026-11-11
flag_ref: "FLAGS/ctf-archive/challenge-246-cryptohack-additional_problems-csc_belgi/flag.txt"
flag_sha256: 6c4c5c1f7f3794ed7f5a8533e9b91f49ef60c26ab3e3252019df35c5e6faf5e1
skills: []
human_twin: AAR.md
---

# AGENT — additional_problems-csc_belgi (CryptoHack ctf-archive, nn 246)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Current state of the attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Attack fully derived and validated end-to-end against a LOCAL clone of the exact server.py (recovered p uniquely, planted flag printed exactly, first connection, ~23 modulus probes). Break: accumulate k zero-byte encryptions under modulus N -- S = sum(N*r_i) = 0 (mod N), and the oracle's (c mod p) mod N = (-b*p) mod N with b = floor(S/p); k=4 forces b in {0,1}, so a nonzero oracle byte yields p = -Y (mod N) with wrap probability >= 1/4 (k=6 fallback when p ~ 2^128); 24 zero-byte positions give 24 trials per decrypt; ~23 primes N in [128,256) give CRT modulus 2^174 > 2^128, pinning p as the unique prime in [2^127,2^128) matching all residues. The single blocker is provider-side: the LIVE listener is broken -- every connection stalls at exactly 319 bytes forever. If/when the listener ships its FLAG env var, `python3 solve.py` solves in one connection. No flag file written (intentional: no flag ever derivable).

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Live service non-functional (above) — not a solver failure; 66 historical solves
  refer to the original CSCB 2024 event.
- Plain SDA/OL lattice on the printed ciphertexts alone: fails at these parameters
  (analysis above); the oracle trick is what makes it breakable.
- No flag submitted; nothing verified against the site beyond connection behavior.

## artifacts [OBSERVED]
- code: _reprobe.sh, connect_raw.py, live_banner_probe.py, live_menu_probe.py, live_probe_2026-11-07.py, netifaces.py, probe_health.py, ref_exploit_cscbe_shim.py, retry_live_2026-11-07.sh, run_local_server.py, run_local_server_plog.py, run_pristine_310.py, server_deployed.py, server_local_clone.py, solve.py, solve_official_style.py, solve_vs_live.py, solver_oracle.py, solver_oracle2.py, solver_oracle3.py
- data/logs: banner_live.txt, banner_probe.txt, live_evidence.log, live_probe_2026-11-07.log, local_clone_flag_2026-11-07.json, local_clone_test_result.json, manual_capture_20261111_091836.json, plog.txt, probe_health_2026-11-02.log, probe_health_2026-11-05.log, reprobe_log.txt, retry_live_2026-11-07.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided server.py; live-banner evidence (banner_probe.txt, banner_live*, reprobe_log.txt, live_evidence.log, _reprobe.sh); local-clone validation (local_clone_test_result.json, netifaces.py stub). Academic reference named in AAR: Galbraith, Gebregiyorgis, Murphy, "Algorithms for the ACD problem" (ANTS 2016). No writeups/solutions consulted.
