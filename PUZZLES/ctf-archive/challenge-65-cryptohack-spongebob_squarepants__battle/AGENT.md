---
record: agent-aar
puzzle: challenge-65-cryptohack-spongebob_squarepants__battle
category: CTF Archive
url: https://cryptohack.org/challenges/spongebob_squarepants__battle/
status: solved
date: None
flag_ref: "FLAGS/ctf-archive/challenge-65-cryptohack-spongebob_squarepants__battle/flag.txt"
flag_sha256: a6c80933fe4421c271c99b5fa5f234707e9b602cb54d5ebc177216d0b33b40ca
skills: []
human_twin: AAR.md
---

# AGENT — challenge-323 spongebob_squarepants__battle (CryptoHack / HTB Cyber Apocalypse crossover)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (derived)" [OBSERVED text; evidence tag applies to its source, not each claim]
R bijective ⇒ 2-block collision: H(m1‖m2)=H(m1'‖m2') ⟺ s1[8:18]==s1'[8:18] and m2' = m2 ⊕ s1[:8] ⊕ s1'[:8]
(m2=0). I.e. birthday on the 80-bit **capacity** of the post-block-1 map f: {0,1}^64 → {0,1}^80.
Wall ≈ 1.4·2^40 evaluations (any 2-block/capacity-equality formulation). No preimage shortcut exists (output=full state).

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: gen_tables.py, harvest.py, harvest3.py, launch_walker3.sh, live_probe.py, probe.py, real_spongebob.py, solve.py, spongebob.py, tv3_check.py
- data/logs: brent_1.log, brent_2.log, found_PROD_1.txt, hunt.log, hunt3.log, hunt_r1.log, walker3_run.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Self-derived per logs (server-verified protocol, own kernel/walker code, hunt.log/brent_*.log/walker2 smoke data). Named math references: van Oorschot-Wiener 1999 parallel rho (the |X| >= |Y| condition explains the failure mode); birthday median ~1.2e12 for a 2^80 collision space. No writeups/solutions consulted; no flag exists for this folder.
- Upgrade-time note (batch #9, 2026-11-02): plain-words wall-map consolidation from existing AAR/hunt logs only — nothing re-run or relaunched; the `## Status at handoff` section above reflects the superseded pre-DIAG state and is preserved verbatim per append-only rules (walker2.c is the live candidate; the running-hunt sentence there is historical).

---
