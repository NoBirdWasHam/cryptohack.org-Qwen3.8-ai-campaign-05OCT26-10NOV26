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
  username-free path templates (~/f.py) that document MSYS behavior;
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
Six screenshots ship in assets/. Two (profile, category grid) verified identity-clean
except the campaign account name (kept by owner decision). Three were pixelated
(solves-lists ×2 incl. First Blood lines, service-report chat incl. inline mentions +
avatars, maintainer-fix reply incl. quoted @mention + name line) and each was re-verified by an independent OCR vision pass returning NO readable
handle/fragment. One terminal screenshot was EXCLUDED outright (shell prompt content).
Image PII cannot be regex-gated; the OCR verification pass is the gate, documented here.

## Addendum — 2026-11-13 audit pass (regenerates G1–G6; adds G7–G9)
Owner directive: verify AAR + method per puzzle, then check the flag in like a checklist.
Findings this pass fixed, in the open:

| gate | rule | result |
|---|---|---|
| G7 dual record | every puzzle dir carries a human `AAR.md` **and** an AI-twin `AGENT.md` with extracted procedure | **PASS 230/230 generated; 229/230 rows fully PASS** (`zkpintro` method is 114 chars — intro-level; row honestly marked fail rather than relaxing the 120-char gate) |
| G8 flag separation | flag values live only in `FLAGS/**/flag.txt`; zero real-flag strings in prose/code; fakes/placeholders/code-fragments policy-listed by one shared classifier | **PASS (0 residual)** — purged 547+ occurrences from 323+ files incl. 170 AARs |
| G9 ledger integrity | every `FLAGS/INDEX.jsonl` sha256 verifies against the published bytes; flag.txt canonicalized to value+LF; `.gitattributes` `eol=lf`; INDEX deduped | **PASS** — all 230→224 sha rows re-verified; found & fixed: autocrlf byte-rot, hashes computed from pre-publication bytes, 2 exact-duplicate rows |
| flag-restore honesty | masked placeholders in flag.txt (`crypto{???…}`, short answers) were not silently kept: numeric/short answers restored from ledger-era values; real flags restored only where a contemporaneous record held a single unmasked candidate (31 rows, dated notes); the rest publish null+note (7 challenge + 83 course) | **PASS — nothing fabricated** |
| artifacts-cited | scripts/logs cited in AARs but absent from the dir were copied in (sanitized, 500 KB cap, author-work names excluded): 629 artifacts; 19 oversize stay out and are named in `PUZZLES/index.json` | **PASS** |

Also 2026-11-13: `/home/<user>` added to the sanitizer (one real leak found in a copied
shell script), `GPU-HOST`-alias match made word-boundary sensitive, and the account's
scoreboard cleared as a courtesy (profile now level 1 / 0 points; screenshots are dated history).


## Verification audit run — completed 2026-11-14 (gate delta)

| gate | rule | result |
|---|---|---|
| G1 host/system identity | re-swept the 2026-11-14 audit-run files (puzzle dirs, wave archive, ledger, skills) | **PASS** — 0 hits after literal-sub sanitizer fix (regex-class sanitizer had silently missed backslash paths; replaced with deterministic literal subs in SUPPORT/build_repo.py; re-sweep clean) |
| G2 authors' works | new puzzle dirs contain only our own artifacts (flag strings in two fischlin artifacts replaced by sha-link pointers) | **PASS** |
| G3 secrets | csrf/cookie/credential patterns re-swept on delta | **PASS** |
| G4 flag containment | audit-run result JSONs: `flag` values -> `flag_sha256` + REDACTED pointer; ledger notes: 3 flag strings scrubbed to `FLAG-REDACTED-SEE-FLAGS-MIRROR`; audit script archive: 47/106 files rewritten (paths + flags); new FLAGS rows follow the full-bytes sha256 convention | **PASS** |
| reconciliation | live API vs ledger | 316 = 316 = 316, zero unmatched, score delta 0 (original solve dates unchanged) |
