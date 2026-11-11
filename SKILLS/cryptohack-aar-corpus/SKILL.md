---
name: cryptohack-aar-corpus
description: Use when auditing/remediating/publishing a CTF AAR corpus.
---

# CTF AAR corpus publication workflow

Use when bringing an AAR corpus to audit/publication standard, reconstructing missing AARs, or prepping a corpus for upload/handoff. Solve-side doctrine (flag provenance, source disclosure) lives in the campaign SOLVER_BRIEF.md; this skill is the corpus mechanics.

## Hard rules (every batch)
- Append-only remediation: never alter existing bytes, claims, flags, or verdicts. Hash old content pre/post to prove the append (byte-prefix check); keep the hashes as batch evidence.
- Write-ups must state evidence limits honestly: 'not recorded in run logs' / 'recovery procedure not recorded' beats a reverse-engineered plausible story. Marking HOW-impossible is a pass, not a failure.
- Negatives are skill maps, not shame lists: OPEN/NEGATIVE AARs keep exact counts, proofs, and bounds; never soften or pad.
- Editor units are offline-only: no re-running challenges, no touching solve scripts, no new solves or submissions.

## Falsifying decisive-negative AARs (validation units)
- Before believing a NEGATIVE verdict hinged on artifact data quality, byte-diff the archived instance against the live static file AND the organizer's public repo copy (CryptoHack ctf-archive category HTML carries each challenge's `/static/challenges/<file>_<hash>` links; the source CTF repo, e.g. DownUnderCTF/Challenges_2020_public, ships the identical output plus often an official exploit.sage and flag). Data matching all three = canonical; the bug is in our pipeline, not the data.
- A negative that priced only the GENERIC formulation (e.g. bivariate Coppersmith on a sqrt-sum hint) must be re-checked against the author's planted path before finalizing: fetch the organizer writeup/repo solution and record it as the technique source.

## Indexer header gotcha
- Legacy AARs using numbered headers (`## 4. How it was solved`, `## 7. Limitations`) FAIL the indexer's HOW/LIM regexes (they require `## how`/`## limitations` adjacency). Clearing the queue means APPENDING the exact un-numbered doctrine headers, not judging the numbered content as missing. The `failed`/`didn't work` LIM alternatives match anywhere in the body, so a LIM flag can be a false pass — check which header matched.

## Publication sections
SOLVED: '## Vulnerability (plain words)' (2-4 sentences, the mechanism, not click-narration), '## How the answer follows' (derivation steps with the key numbers from AAR/scripts), '## Limitations / attempts that failed', '## Sources' (cited refs, or 'self-derived per logs').
OPEN/NEGATIVE: '## The challenge (plain words)', '## Current state of the attack', '## What has been ruled out and why', '## Sources'. The indexer's HOW regex must accept these negative headers, or OPEN AARs can never clear the quality queue. Same for the LIM regex: batch #9 (2026-11-02) extended aar_index.py's LIM regex to accept `## what has been ruled out` — without it, task-mandated negative vocabulary never clears the gate. Note LIM also matches the word `failed` in prose ANYWHERE, so prose-only lim=True is common; gate the HOW header only. When a gate fix reclassifies other units' folders, list them in the batch report (honest queue delta).

## Batch procedure
1. Regenerate the index (`python3 aar_index.py` → AAR_INDEX.md + aar_index.json). Its 'Remediation queue' lists folders missing HOW/LIM or lacking an AAR; take the queue head as this batch (~9-14 folders per unit).
2. Dispatch editor subagents with DISJOINT folder lists (parallel batches are safe; index regeneration is idempotent — tell each unit concurrent batches exist).
3. Every editor brief must carry: doctrine sections to read first, the exact section vocabulary, append-only + byte-prefix rule, 'not recorded in run logs' rule, call budget (~35-45), deliverable = per-folder one-liners + queue delta, regenerate index at end.
4. Verify the claimed queue delta with your OWN aar_index.py re-run before reporting it.
5. NO-AAR folders are a separate RECONSTRUCTION class: evidence order = ledger notes (progress.json) → folder solve scripts/logs → statement. Scripts evidence the method but do not extend its HOW past what the script shows. Mark output '## RECONSTRUCTED AAR (post-hoc)'.
6. Missing flag.txt on a SOLVED folder: restore from the flag verbatim in the ledger/AAR (provenance = ledger/solved-list, not fresh retrieval — legitimate housekeeping).
7. Wall-map AARs that grew past ~10k chars across runs: append a plain-words state summary at the TOP so a fresh session reads the state in one screen.

## Near-duplicate folder names
- Mirror folders can differ by ONE typo character (e.g. `srateslla` vs `sratslla` for one challenge): `ls` renders them as identical duplicates. Hex/byte-compare folder names before assuming a listing glitch — the canonical solve may live in the misspelled twin while the correctly-spelled one holds an earlier partial-attempt record whose text contradicts the ledger status (indexer status is keyed by slug, so the ledger SOLVED override rides on both).

## Ledger hygiene
- Folder mirrors (one challenge living in two folders, e.g. canonical solve vs server-artifact stub): annotate canonical attribution on the ledger row so audits count one credit; the indexer keys status by slug, so the stub shows the real status — the stub's AAR text must say so.
- Editor upgrades that re-check arithmetic (verifying a j-invariant, re-deriving a rational) are comprehension checks: disclose them in Sources as upgrade-time checks, never as new solves.

## Read-only audit procedure (no writes to the tree)
The corpus carries THREE ledgers with DIFFERENT key spaces — reconcile by slug, and expect the counts to differ:
- `progress.json` queue: one entry per LIVE site challenge, keyed by SITE slug; status `solved`/`open`; carries `flag`, `notes`, `folder`.
- `aar_index.json`: one entry per AAR, keyed by FOLDER-style slug (`challenge-NN-cryptohack-...`); status `SOLVED`/`OPEN`/`NEGATIVE`; the `name` field is often EMPTY — a name-set diff produces a garbage result (every entry "missing"); match on slug/folder.
- `AAR_INDEX.md`: human table, should be 1:1 with the JSON; row count is the cross-check.
Folder count > queue count > index count is EXPECTED, not corruption: the delta = duplicate/variant folders (see Near-duplicate folder names) plus root-level extra copies of a challenge. Explain every audit delta by naming the duplicates; under a read-only audit report, never fix.
- Hash check: aar_index.py hashes NORMALIZED text (UTF-8 read, universal newlines → LF, re-encoded, first 16 hex of SHA-256), NOT raw bytes. A raw `sha256sum` mismatch vs the index is expected — re-hash with the same normalization before calling any AAR modified.
- Verify saved `api_*.json`/dump files actually parse as JSON before treating them as ground truth — saved HTTP error pages (404s) masquerade as dumps; an unparseable dump is non-authoritative, not a source.
- Status-contradiction checklist per entry: (a) progress.json status vs (b) aar_index.json status vs (c) flag file on disk vs (d) AAR Result wording. Any divergence is an audit FINDING (e.g. flag on disk + AAR says unsolved + index SOLVED + queue open) — report it; only the owner's ruling closes it.
- Mirror folders for one challenge can carry DIFFERENT statuses (SOLVED vs NEGATIVE): the indexer keys by slug, so both rows exist. Flag the contradiction, don't pick a winner.
- When the audit is followed by "math sources for the open puzzles": map each open entry's `notes` (they already encode the attack family) to canonical references — papers, books, tools — and pair each with its public-solution availability. Verify every citation before listing it (see the citation pitfall in `ctf-practice-runs`); an unverified reference in a publication-bound corpus is a provenance failure.

## Public-solve status (corpus attribute)
Public-solve availability is a corpus attribute for publication value and practice-value triage — full recipe in `references/public-solve-verification.md` (category set, parsing anchors, ledger↔site matching, third-party writeup search).
- The only usable public source is the category pages' per-row `N Solves` / `N Solutions` counts. `/solutions/` is a limited landing view; per-challenge solution pages are completion-gated (login + solved).
- Report two layers: (1) site solutions per challenge; (2) for the zero-site-solution set, third-party writeup availability per source CTF in calibrated vocabulary (Observed / Not observed / Unknown), location cited.
- Cataloging contaminates: writeup-search snippets routinely contain FULL solution text. Record locations only; flag to the owner that a puzzle with a confirmed public writeup is no longer cleanly self-solvable.
