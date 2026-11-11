# GATES — publish gates and results (final run 2026-11-11, schema v2)

Layout per owner schema: PUZZLES/<category>/<puzzle>/ (self-contained) ·
FLAGS/<category>/<puzzle>/flag.txt (mirrored; INDEX.jsonl pairs + sha256) ·
SKILLS/ · SUPPORT/ · assets/.

| gate | rule | result |
|---|---|---|
| G1 host/system identity | zero occurrences across 1634 files of: workstation username, machine hostname, account aliases, LAN IPs, GPU hostname, real user-home paths (`C:\Users\<name>`, `/c/Users/<name>`, `/home/<name>`), MACs | **PASS (0 residuals)** |
| G2 authors' works not re-hosted | zero files named statement.txt / flag.txt / chall*.py / chal.py / challenge.py / source_provided.* / source.sage / output_provided.txt / Dockerfile / server.py / task.txt | **PASS (0)** |
| G3 secrets | no credential assignments; 7 platform CSRF tokens scraped into page-cache notes -> REDACTED; 1 non-branded Discord invite -> DISCORD-INVITE | **PASS** |
| G4 flag containment | flags live in FLAGS/flags.jsonl (+ our own AAR prose); LEDGER copy flag-stripped | **PASS** |
| G5 honest nulls | 3 solved rows whose flags were ledger-redacted publish as null + note; 85 course rows are flagless by platform design; 229 rows carry values; nothing fabricated | **PASS** |
| G6 provenance | every row dated + classed (WALKED / SERVICE-GIVEN / PRE-LEDGER-ERA labeled rather than back-classified) | **PASS** |

## PII sweep (owner directive 2026-11-11)
- Third-party player handles -> SOLVER-A..D, maintainer account -> MAINT-ACCOUNT
  (role-preserving; the row-246 analysis reads identically, and the public solves page
  remains the verification pointer - cited by URL, not by name).
- Workstation hostname -> WORKSTATION. Sanitizer shipped in TOOLS carries generalized
  regexes only - it documents the rules without embedding any identity.
- Kept deliberately: RFC-reserved .example addresses that are part of challenge fiction;
  username-free path templates (/c/Users/.../f.py) that document MSYS behavior;
  published author attribution in SOURCES (GitHub handles / blog URLs - citation, not PII);
  the campaign account name itself (owner decision, dated in README).

## Generator
TOOLS/build_repo.py - whitelist of our artifact filename families; hard-exclude of authors'
artifact names; 500 KB per-file cap (1 oversize file skipped); sanitizer substitutions incl.
CSRF scrub. Corpus/repo locations come from CAMPAIGN_SRC / REPO_OUT env vars, so the
generator itself ships identity-free. Rerunning it reproduces this tree.

## Manual-review residuals (owner's eyes, not a script's)
AAR prose is first-person campaign history. Where a public leaderboard/API record is
discussed, the verification path is the cited URL + date; names were swept per above.
Discord participants are role-described.

## Image gate (added 2026-11-11)
Five screenshots ship in assets/. Two (profile, category grid) verified identity-clean
except the campaign account name (kept by owner decision). Three were pixelated
(solves-lists ×2 incl. First Blood lines, service-report chat incl. inline mentions +
avatars) and each was re-verified by an independent OCR vision pass returning NO readable
handle/fragment. One terminal screenshot was EXCLUDED outright (shell prompt content).
Image PII cannot be regex-gated; the OCR verification pass is the gate, documented here.
