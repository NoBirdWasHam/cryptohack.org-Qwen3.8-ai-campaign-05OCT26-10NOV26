# CryptoHack — Qwen3.8 AI Learning Campaign
### 2026-10-05 → 2026-11-10 · verification audit run completed 2026-11-14 · `NoBirdWasHam` · two local models · no cloud APIs

![Final state 2026-11-14, after the verification audit run — Level 34 · 17,370 stars · rank #1](assets/profile_final_2026-11-14.png)

![Full clear — every category complete, 316/316 (2026-11-14)](assets/categories_final_2026-11-14.png)

An AI agent learned graduate-level cryptography by solving CryptoHack end-to-end — and this
repository is the complete, sourced record: **every puzzle is independent and self-contained**
(its AAR + every script we wrote), every flag is dated with honest provenance, and the
failures are documented as carefully as the wins. Built so a human or another AI can
verify, recreate, and **learn** from it.

## Where this ended
**316 / 316 on the site.** Level **34** · **17,370** stars · rank **#1** — final state
2026-11-14 (captures above; audit evidence in `SUPPORT/2026-11-14-verification-audit/`).
Solving ran 2026-10-05 → 2026-11-10, the last row (246) closing 2026-11-11 after the
upstream service fix; every original solve date in the ledger stands, and the 11-14
date is used only for the audit run itself. **316 site rows = 233 numbered challenges
+ 83 course lessons** (the site double-lists two lesson-titled rows), from an 85-solved
baseline. Since 2026-11-15 the tree mirrors the site's 14 current category pages with a
two-tree layout (owner decision): **`PUZZLES/` holds only the 233 numbered challenge
records — one self-contained dir per numbered site row, 1:1** — and the 83 course-lesson
records live under **`COURSEWORK/`**, because the site retro-folded lesson rows into its
challenge lists without giving lessons any public challenge id, and the run recorded them
as taught lessons, not challenges. `FLAGS/INDEX.jsonl` mirrors the 233 challenge dirs 1:1;
`COURSEWORK/index.jsonl` mirrors the lessons. Category membership follows today's site
pages, not the mid-run ledger labels — see the 2026-11-15 errata addendum; every row carries
its own record (the two rows published `null` on record-never-written findings received own
derivations in the audit run; appendix at the bottom).

## The three hard rows — the honest heart of this repo
| row | outcome |
|---|---|
| **246 · Additional Problems (CSC Belgium)** | **WALKED 2026-11-11 — after being the campaign's documented failure for weeks.** Attack verified locally while the container sat dead (`python:3.10`→`3.12` bump made `randint(0, float)` fatal); root cause reported upstream with byte-evidence; maintainers shipped the one-line fix; we then solved it live against the repaired service and submitted what we derived — nothing was submitted while the service was dead. Full failure-to-walk record in its AAR. |
| **237 · Sigma: Hamiltonicity 2** | SOLVED 2026-11-10 — forgery exploiting that the Fiat-Shamir hash binds the digit *stream*, not the matrix. |
| **265 · Hamiltonicity 2** | SOLVED same day — same forgery; two instances, one flag. |

![Other solves kept landing while the container stayed dead — third-party names redacted](assets/solves_246_redacted.png)

The dead-service dispute in one picture: players solve (the flag string circulates — the
author's own writeup publishes it), while the TCP service answers literally nobody with
more than a 319-byte corpse. And when we reported it, the maintainer-side reply was exactly
the kind of good-faith debugging question we'd have asked:

![Service report thread with maintainer (handles redacted)](assets/service_report_redacted.png)

The report landed:

![Maintainer ships the fix — commit title is our exact diagnosis (handles redacted)](assets/maintainer_fix_reply_redacted.png)

Hours later the solver ran against the repaired container and the row closed **WALKED**:
`[flag — recorded in FLAGS/ctf-archive/challenge-246-cryptohack-additional_problems-csc_belgi/flag.txt]` — service-given ciphertext, self-recovered key,
submitted and verified. This row is still the thesis of this repo: document the failure
completely enough that even the other side can fix it, and let the solve finish the story.

## What you get here
Two after-action reports per puzzle — one written for humans, one optimized for AI/LLM
ingestion — plus a verification checklist where every flag row earns its check:
```
PUZZLES/<category>/<puzzle>/   AAR.md (human) + AGENT.md (AI twin) + every script we wrote
                               + README.md stub (facts, skills, concept tags) — self-contained
FLAGS/<category>/<puzzle>/     flag.txt — mirrored paths; INDEX.jsonl pairs+checksums each
COURSEWORK/<category>/<lesson>/ the 83 course-lesson records (same dual record, lesson
                               format; captured flags colocated; index.jsonl + index.json)
TAGS/                          concept tags (rsa, fiat-shamir-forgery, …) linking the puzzles
SKILLS/                        the transferable skills this campaign produced (INDEX.yaml)
SUPPORT/                       VERIFICATION.md (per-puzzle audit checklist), platform notes,
                               runtime/models, sources, friction ledger, campaign-level
                               HUMAN.md + AGENT.md, provenance doctrine, build_repo.py
GATES.md                       the publish gates (PII sweep, author-work exclusion) and results
```
- **Verified, not asserted.** `SUPPORT/VERIFICATION.md` audits every puzzle dir (AAR present,
  method has substance, AI-twin extracted, flag sha256 matches `FLAGS/INDEX.jsonl`, PII- and
  flag-clean) and prints a pass/fail checklist; `PUZZLES/index.json` is its machine twin.
  Flag values live under `FLAGS/` mirrored paths and may appear in **our own** AAR prose
  (gate G4); every copy that had leaked into support files or logs was replaced by a
  sha256 pointer. `FLAGS/<cat>/<puzzle>/` mirrors the puzzle's category path exactly.
- **Honor system, honored.** CryptoHack grades the submitted string; our doctrine is
  stricter: flags here were self-derived or service-given only — retrieved flags were never
  submitted (SUPPORT/PROVENANCE.md). **260 flags carry values: 228 under `FLAGS/` mirrors
  (31 challenge rows restored from contemporaneous records, 2 derived fresh in the 2026-11-14
  audit run — rows 260 and unbalanced — each with a dated provenance note in
  `FLAGS/INDEX.jsonl`) + 32 colocated under `COURSEWORK/` (lesson rows restored 2026-11-15
  from contemporaneous records, single unmasked candidate only)**; 5 challenge rows + 51
  course rows publish `null` + note instead of a fabricated value (lesson rows
  without an unmasked single candidate stay null — nothing reconstructed).
- **Score etiquette:** this was learning on a friendly platform — CryptoHack's scoreboard is
  an honor system intended for humans, and anyone can copy flag strings onto it. Our
  doctrine keeps the account's presence there temporary by design: the owner cleared it as a
  courtesy on 2026-11-13 after documentation verification, the verification audit pass then
  re-earned/re-verified the full set (its captures above are dated history of that pass, not
  a claim about the live account), and on **2026-11-15 the account was cleared again** once
  learning and verification were complete (live profile: Level 1 · 0 points). The evidence
  of this campaign is this repository, not a leaderboard row.
- **Recreatable:** rerun `SUPPORT/build_repo.py` against the working corpus to re-derive this
  tree; every puzzle dir runs standalone with a plain Python venv (fpylll/PARI where noted).
- **PII-free by gate, not by promise:** zero host identity, zero third-party handles in text
  *and* images (pixelation verified by independent OCR pass), authors' files linked not hosted.

## Start reading
1. `SUPPORT/HUMAN.md` — the whole arc, plain language
2. `SUPPORT/AGENT.md` — the same facts as tagged claims (`[OBSERVED/NOT OBSERVED/UNKNOWN]`)
3. `PUZZLES/zkp/challenge-237-*` + `PUZZLES/ctf-archive/challenge-265-*` — the twin forgery
4. `PUZZLES/ctf-archive/challenge-246-*` — how a *failure* should be documented
5. `SUPPORT/FRICTION.md` — 104 wasted GPU-hours, eight days of read-only probing, and the
   probe that printed its author's verdict as its own conclusion ("That is YOU.")


---

## Appendix — verification audit run, completed 2026-11-14

The ledger's original solve dates stand: the campaign finished 2026-11-10, with the last
row (246) closing 2026-11-11 after the upstream service fix. After the owner clear of
2026-11-13, a **verification audit pass (2026-11-13/14) independently re-derived the 87
badges that did not persist** and reconciled the site against the ledger: live score
17370, solved 316 == local 316 == queue 316, unmatched zero in both directions.
Evidence lives in `SUPPORT/2026-11-14-verification-audit/` (`VERIFICATION-AUDIT-2026-11-14.md`
row table, the 106-file solve-script archive with host paths and flag values stripped to
sha256 links, the full-clear category board capture, and the final profile capture:
**Level 34 · 17,370 · rank #1**).

Rows whose published record changed during the audit:

| row | delta |
|---|---|
| **260 · Fischlin's transformation** | was: `null`, "record never written" — audit produced its **own derivation**: live-service replay of the Fischlin-OR search path (64/64 rounds); puzzle dir `PUZZLES/ctf-archive/challenge-260-…` created with AAR + artifacts. Original row-credit date (2026-10-25) stands. |
| **304 · Unbalanced (ICC Athens 2022)** | original credit 2026-11-02 stood on a credited-but-undocumented solve; the audit **independently derived it** (Durfee-Nguyen trivariate Coppersmith, rank-126 lattice, +46 b/dim margin, Bareiss-resultant extraction). Prior evidenced-negative sections remain, scoped to the bivariate route. |
| **247/13396 · Authenticator** | original solve 2026-10-28 stands; the audit **re-derived it with an independent algorithm** (rainbow tables vs the original GPU brute). The puzzle folder — previously absent from this repo due to a legacy folder misname — is now published at `PUZZLES/ctf-archive/challenge-13396-…`. |

| **322 · RSATogether (ECSC 2024 Italy)** | solved & documented 2026-10-29 (own derivation: staircase Shamir-over-φ → exact φ-multiple → Miller/Sabt factoring) but the **directory never made it into the 2026-11-11 build** — a full-tree corpus↔repo audit in the late 11-14 pass caught it; dir, AAR, twin, flag and INDEX row now published. Original solve date stands. |

Full delta bookkeeping (incl. the late-pass integrity fixes — INDEX rebuild, mirror moves,
front-page reconciliation): `SUPPORT/2026-11-14-verification-audit/ERRATA-UPDATE-2026-11-14.md`.
The provenance red lines are unchanged: submitted flags are exclusively self-derived or
service-given; `UNDISCLOSED = 0`.

Dated intermediate captures, kept as history: the campaign-end profile at 2026-11-10
(Level 33 · 17,195 · rank #5 — `assets/scoreboard_profile.png`) and the 313/316 category
board of the same date (`assets/categories.png`); the account clear of 2026-11-13 sits
between them and the final captures above.
