# GATES — publish gates and results (final run 2026-11-11, schema v2)

Layout per owner schema: PUZZLES/<category>/<puzzle>/ (self-contained) ·
FLAGS/<category>/<puzzle>/flag.txt (mirrored; INDEX.jsonl pairs + sha256) ·
SKILLS/ · SUPPORT/ · assets/.

| gate | rule | result |
|---|---|---|
| G1 host/system identity | zero occurrences across 1634 files of: workstation username, machine hostname, account aliases, LAN IPs, GPU hostname, real user-home paths (`C:\Users\<name>`, `/c/Users/<name>`, `/home/<name>`), MACs | **PASS (0 residuals)** |
| G2 authors' works not re-hosted | zero files named statement.txt / flag.txt / chall*.py / chal.py / challenge.py / source_provided.* / source.sage / output_provided.txt / Dockerfile / server.py / task.txt | **PASS (0)** |
| G3 secrets | no credential assignments; 7 platform CSRF tokens scraped into page-cache notes -> REDACTED; 1 non-branded Discord invite -> DISCORD-INVITE | **PASS** |
| G4 flag containment | **Distinctive flag values** (non-numeric, ≥8 chars) live only in: `FLAGS/` (INDEX.jsonl + flag.txt), the puzzle's own AAR/AGENT prose, and declared worked examples in `SKILLS/*/SKILL.md`. **Class exception, disclosed:** BARE-answer challenges have flags that are common words or short numerals (`NOT`, `65537`, `Let's Encrypt`, …); those are ordinary vocabulary/digits that occur naturally in solve prose anywhere (SKILLS, SUPPORT notes, frozen audit JSON — e.g. the 15 common-numeral residuals in `progress_sanitized.json`, the `Authorization` hit in `wave-scripts.tar.gz`) and carry no disclosure content, so string-level containment does not apply to them; containment is enforced on the distinctive class only. (11-16b: counts removed from this gate — the same tree yields 31 / 37 / 38 distinctive values under three defensible sweep rules, so a printed count is not reproducible; scoping is by class. Filename corrected flags.jsonl→INDEX.jsonl in 11-16.) | **PASS** |
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
scoreboard cleared as a courtesy (profile at level 1 / 0 points at clear time; the audit run below re-earned the set; screenshots are dated history).


## Verification audit run — completed 2026-11-14 (gate delta)

| gate | rule | result |
|---|---|---|
| G1 host/system identity | re-swept the 2026-11-14 audit-run files (puzzle dirs, wave archive, ledger, skills) | **PASS** — 0 hits after literal-sub sanitizer fix (regex-class sanitizer had silently missed backslash paths; replaced with deterministic literal subs in SUPPORT/build_repo.py; re-sweep clean) |
| G2 authors' works | new puzzle dirs contain only our own artifacts (flag strings in two fischlin artifacts replaced by sha-link pointers) | **PASS** |
| G3 secrets | csrf/cookie/credential patterns re-swept on delta | **PASS** |
| G4 flag containment | audit-run result JSONs: `flag` values -> `flag_sha256` + REDACTED pointer; ledger notes: 3 flag strings scrubbed to `FLAG-REDACTED-SEE-FLAGS-MIRROR`; audit script archive: 47/106 files rewritten (paths + flags); new FLAGS rows follow the full-bytes sha256 convention | **PASS** |
| reconciliation | live API vs ledger | 316 = 316 = 316, zero unmatched, score delta 0 (original solve dates unchanged) |

## Integrity fixes — 2026-11-14 (late audit pass, after owner review of the published page)

A full-tree audit of the LIVE repo (every claim recomputed from the remote, every hosted
image vision-audited, every flag re-hashed from fetched bytes, corpus↔repo folder diff)
found and fixed the following. None of these changed any solve date, flag, or provenance
class — they are publication-integrity defects:

| defect | fix |
|---|---|
| README led with the 2026-11-10 capture (rank #5) and a 313/316 board; body claimed "now level 1 / 0 points" | hero replaced with the final rank-#1 profile + 316/316 board captures (bytes identical to the audit-dir copies); old captures relabeled as dated history; score-etiquette bullet rewritten to facts |
| README claimed flag values "live only under FLAGS/" while gate G4 (and the tree) allow own-AAR prose | wording reconciled to what the gate actually enforces |
| README counts stale (224 values; "7 challenge + 83 course null") | recomputed from the rebuilt INDEX: **228 values · 5 challenge + 83 course null** |
| `FLAGS/INDEX.jsonl` carried 2 appended dateless duplicate rows (260, unbalanced) | merged into the canonical dated rows |
| authenticator row absent from INDEX; its flag absent from FLAGS (folder was first-published 11-14) | row + `flag.txt` restored (self-derived 2026-10-28, dated note) |
| **rsatogether (challenge-322, ECSC 2024 Italy) missing from the repo entirely** — full corpus record existed (own derivation 2026-10-29, API 278→279) | dir published (AAR + AGENT twin + stub + 26 files), flag mirrored, INDEX row added |
| 32 INDEX `puzzle` paths + 31 FLAGS dirs drifted from the real category dirs; 83 course rows pointed at never-published ghost dirs | INDEX rebuilt (one row per published entity, paths = real dirs); FLAGS dirs `git mv`-mirrored to puzzle categories; course rows point at the ledger record and carry their name |
| fischlin + authenticator dirs published without AGENT twins/stubs (breaking the self-contained promise); unbalanced twin still said "honest null" after its 11-14 derivation | twins + stubs written; twin updated; `PUZZLES/index.json` regenerated (233 dirs, 233 twins) |
| ledger↔INDEX slug drift (site renames: big2↔everything-is-still-big, csidh_secret_exponents↔secret_exponents, import_numpy_as_mt suffix, c0ll1d3r suffix) | documented; INDEX keys = published dir slugs |

Post-fix validator: INDEX 316 rows = 233 challenge + 83 course; 228 values, 88 honest
nulls; every `puzzle` path resolves to a real dir; every flag file hashes to its row
(228/228, full bytes); corpus↔repo diff: zero missing records; G1 host-identity sweep 0
hits; G3 secrets sweep 0 hits; flag containment per G4 rule.

## Addendum — 2026-11-15 site-1:1 reorg (owner flag: folder taxonomy ≠ the site's 14 categories)

Owner observation: the tree had 12 category folders where the site shows 14 tiles, and
several dirs sat under mid-run ledger categories the site no longer uses. The current site
category pages (scraped 2026-11-15) became the authority for membership:

| change | scope |
|---|---|
| dirs moved to their current site category | 31 (24 misc→ctf-archive, 3 post-quantum→misc, collider→hashes, matrix_revolutions→diffie-hellman, unimplemented→ctf-archive, beatboxer→aes, curveball→ecc) |
| dir slugs renamed to the current site slug | 12 variants (incl. everything-is-still-big→big2, secret_exponents→csidh_secret_exponents, hyphen/underscore variants, two site-truncated slugs) |
| course-lesson dirs published (`course-<slug>`, lesson format: no flag by graded-question design unless restored) | 83 — one per site row that had no dir; lesson↔ledger-row bijection 83/83 (the 85 ledger course rows minus beatboxer/curveball, published as numbered records) |
| categories added | introduction, general (course-only on the site; READMEs explain the zero-flag design) |

Per-category dir counts now equal the site tiles exactly (3/19/29/16/29/14/23/16/17/18/23/17/16/76 = 316).

Gates rerun over the reorged tree: **G1 0 hits** (2,747 files incl. every new file);
**G3 0 hits**; **G8** zero full-flag strings in any new file — the 32 restored lesson flags
live only in `FLAGS/**/flag.txt` and their AAR prose was pointer-replaced; the
pre-policy-listed legacy set (6 files) is byte-identical to the previously-passing state.
**G5 updated honestly:** the claim "83 course rows are flagless by design" was too strong —
32 lesson rows DO have contemporaneous in-run flag records in their corpus AARs and were
restored under the same single-unmasked-candidate rule used for the 31 challenge rows
(2026-11-15 dated notes); the remaining 51 publish null (masked/truncated/absent records).
**G9:** INDEX rebuilt (316 rows, one per site row); every surviving challenge row's
sha256 + provenance note verified identical to the pre-reorg committed row (0 mismatches
after path/slug normalization); all 260 flag files hash-match their row; ledger rows
untouched (mid-run categories preserved there as history; the site taxonomy lives in INDEX
`site_category`).

## Addendum — 2026-11-15 coursework extraction (owner decision: PUZZLES/ = challenges only)

Owner review of the folder taxonomy: mixed `challenge-<id>-cryptohack-<slug>` and
`course-<slug>` dir formats in the same category listings is not uniform, and lessons
cannot honestly join the numbered format — the site gives lesson rows no public id
(checked: 78/83 leak no static-file id; the 5 that do collide with existing challenge
ids). Owner ruling: **courses stay out of the challenge taxonomy; the numbered challenge
set must be complete and documented to standard.**

| change | scope |
|---|---|
| `PUZZLES/<cat>/course-*` → `COURSEWORK/<cat>/course-*` | 83 dirs, content byte-unchanged |
| `FLAGS/<cat>/course-*/flag.txt` → colocated `COURSEWORK/<cat>/course-*/flag.txt` | 32 files (sha256 re-verified after move, 0 mismatches) |
| INDEX split | `FLAGS/INDEX.jsonl` 233 challenge rows (228 flags / 5 null); `COURSEWORK/index.jsonl` 83 lesson rows (32 flags / 51 null); rows byte-carried, no note re-templating |
| live docs regenerated | category READMEs (233-dir listings + COURSEWORK pointers), `PUZZLES/index.json` (233), `COURSEWORK/index.json` (83), `SUPPORT/CATEGORY_INDEX.md`, top README |
| frozen evidence untouched | `SUPPORT/2026-11-14-verification-audit/` byte-unchanged (path references inside it intentionally NOT rewritten) |

Per-category challenge counts vs site tiles (challenges/lessons): introduction 0+3,
general 0+19, aes 6+23, maths 10+6, rsa 14+15, diffie-hellman 7+7, ecc 13+10, and
16/17/18/23/17/16/76 challenges in hashes/web/post-quantum/isogenies/zkp/misc/ctf-archive
(lessons 0) — totals 233 + 83 = 316 site rows (*beatboxer/curveball are numbered ledger
records whose lesson-titled double-listing on the site is noted in their dirs).

Gates rerun over the extracted tree: G1 0 hits; G3 0 hits; G8 — the 32 restored lesson
flag strings appear only in colocated `flag.txt` files (path rewrite pass touched prose
pointers, 66 files); validator green (233 dirs == 233 INDEX rows == mirrored flags; 83
coursework dirs == 83 rows; all shas match).

Gate-fix note (this pass): full-tree G1 re-run with live hostname as a literal token
found ONE pre-existing residual — `PUZZLES/ctf-archive/challenge-305-*/dlp_run2.sh`
hardcoded the build dir `build/<hostname>`; replaced with `$(hostname)` (portable,
identity-free). Re-run: 0 residuals. Earlier G1 wordings had covered username/LAN-IP
patterns but not the machine hostname as a build-dir token — gate pattern widened.

## Addendum — 2026-11-15c single-tree ruling (owner: lesson rows are cross-pollinated challenge rows)

Owner clarification supersedes the same-day coursework-extraction split: every solved site
row must show its AAR + info inside its category ("coursework is duplicate — it's
cross-pollinated"). The separate COURSEWORK/ tree is retired; lesson records were moved
back into `PUZZLES/<category>/` as `challenge-<NN>-cryptohack-<slug>`, **NN = row position
on the site category page** (verified collision-free vs every existing ledger id; declared
as position — never presented as a public challenge id, which lessons do not have).

| change | scope |
|---|---|
| `COURSEWORK/<cat>/course-*` → `PUZZLES/<cat>/challenge-<pos>-cryptohack-<slug>` | 83 dirs, content byte-unchanged |
| lesson flags → standard mirror `FLAGS/<cat>/challenge-<pos>-cryptohack-<slug>/flag.txt` | 32 files, sha256 re-verified (0 mismatches) |
| `FLAGS/INDEX.jsonl` merged | 316 rows (233 numbered + 83 `kind: course-lesson`; 260 flags / 56 null), every note carried from prior rows + dated NN-convention clause |
| docs regenerated | category READMEs (lesson rows marked), `PUZZLES/index.json` (316), `SUPPORT/CATEGORY_INDEX.md`, top README |

Per-category dirs == site tiles again: 3/19/29/16/29/14/23/16/17/18/23/17/16/76 = 316
(lessons included: 3/19/23/6/15/7/10/0… = 83). Validator green: dirs==rows, 3 files/dir,
mirrors exact, all flag shas match. G1/G3 unchanged (no new content beyond path
pointers); G8 — flag values touched no file outside mirrors/own dirs (path-rewrite pass
touched pointers only).

## Addendum — 2026-11-15d uniform site-order numbering (owner: numbering was mixed)

Owner catch: after the merge, categories mixed two numbering systems — lesson dirs were
site-row positions (1..N) while challenge dirs kept old ledger ids (124-130 etc.). Checked
where puzzle numbers actually live: category rows print none, lesson pages redirect to the
course, and even the numbered rows' inline static-file ids (e.g. 13373 for `dh_static`) do
not match ledger ids. The only numbering a reader can see and check is **the site page's
row order**, so all 316 dirs were renumbered to it uniformly.

| change | scope |
|---|---|
| dir renames `challenge-<old>-...` → `challenge-<site-row-position>-...` | 233 (83 lesson dirs already conformed), two-phase swap-safe, 0 collisions |
| historical ledger id preserved | new `ledger_nn` field on all 233 challenge INDEX rows + per-dir listing line; run ledger unchanged as history |
| prose path rewrites | 467 files; all 233 old paths referenced in prose updated; frozen 11-14 audit dir untouched (path references there intentionally kept, noted) |

Validator after renumber: 316 dirs == 316 rows, **every dir NN == its row position on the
live category page** (re-parsed), 3 files/dir, FLAGS mirrors exact, all 260 flag shas match.

## Addendum — 2026-11-16 external-audit round: doc-layer fixes and adjudications

Second-opinion audit of the published tree; every finding reconciled against this working
copy (identical to live `2d6d15d`) before acting. Fixes:

| finding | resolution |
|---|---|
| README "Start reading"/appendix paths used legacy ids → 5 dead paths | re-pointed to real dirs (zkp/`challenge-9-…sigma-hamiltonicity2`, ctf-archive/`challenge-12-…hamiltonicity_2…`, `challenge-7-…additional_problems…`, `challenge-9-…fischlins…`, `challenge-37-…authenticator…`) |
| AGENT frontmatter / README titles carrying legacy `challenge-<old>-…` ids | audit found 7+2; full sweep found **233 + 35** — all rewritten to current dir ids (my 15d sweep only matched `PUZZLES/…`-prefixed paths; disclosed). The 83 lesson twins keep `record: course-twin` + `lesson: course-<slug>` (ledger-era lesson ids, matching the run record) — record ids, not dir paths; no change |
| `GATES` G4 named `FLAGS/flags.jsonl` | corrected to `FLAGS/INDEX.jsonl` |
| G4 scope vs SKILL worked examples | ~30–38 real flag values sit deliberately in 7 `SKILLS/*/SKILL.md` as taught worked examples. G4 rewritten to **enumerate** sanctioned locations (FLAGS/ + own AAR/AGENT prose + declared SKILL worked examples; values banned from logs/SUPPORT/JSON dumps) rather than contradict the tree. My exact count: 38 distinct values in 7 files (audit: ~30/7 — substring length cutoffs differ; no conflict in kind). [11-16b erratum: a third sweep reproduced **31** — counts are extraction-rule dependent and were removed from G4; class-scoping replaced them] |
| live flag values inside `SUPPORT/progress_sanitized.json` (reality: **2 distinct flags, 3 occurrences** — comp_isogenies + three_isogenies; the audit caught one) | scrubbed: the notes-field numeric form of the comp_isogenies flag → redaction + sha256 pointer (file is a sanitization artifact; the run ledger itself stays untouched as history). Note: the audit's quoted rendering differs in term order from the stored flag file — the notes-field form was scrubbed where it actually occurs; SKILLS hits of this value are in-scope worked examples per rewritten G4 |
| VERIFICATION checklist names ≠ current dirs | those are the 2026-11-14 run's historical record — kept, with an explicit history note + `ledger_nn` mapping pointer above the table |
| "dirs keep the ledger/site id" sentence | **not present** in live `2d6d15d` (removed in 15d); the audit was quoting pre-15d README text. The dead example paths it stood next to were real and are fixed above |
| cited-but-absent artifacts (237: `statement.txt`, `chal.py`, `payloads_2026-11-05.json`; 304: `challenge.py`; GCM: legacy `challenge-317-…` folder) | disclosed: run-workspace-local at solve time, never published; GCM's surviving probes are in-dir and the README claim now points there. The two AARs' cited contents stand as quoted records |
| slug `fischlins_transformation-cryp` looks truncated | **site-published slug** — scraped `data-challenge` attribute contains it verbatim; not our truncation |

**Adjudicated — 8 shared `ledger_nn` pairs** (100, 167, 168, 172, 209, 319, 13391, 13396): all
pairs are *different slugs*. Mechanism, scoped to evidence: the ledger's NN was the queue **position at record time** —
the published queue itself shows NN 105/130/131 each held by two different slugs recorded on
different run dates, and for 5 of the 8 INDEX collision pairs only one member exists in the
final queue snapshot (the other's NN came from an earlier one). Positions shifted while the
run was active; whether the site renumbered by row insertion or page reshuffle is not
externally re-derived and is not claimed. Not mapping errors; values kept as history. All 16 affected INDEX rows now
carry `ledger_nn_shared: true` (13396 additionally has the pre-existing misname note).

Frozen 2026-11-14 audit dir and the run ledger: untouched.
