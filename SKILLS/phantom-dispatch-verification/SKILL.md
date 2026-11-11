---
name: phantom-dispatch-verification
description: Use when a dispatched challenge cannot be found on its site.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, practice, orchestrator, verification]
    related_skills: [ctf-practice-runs, ctf-lattices]
---

# Phantom dispatch verification — kill ghost targets with evidence, never fabricate

## When to Use
A dispatched challenge/folder/queue entry cannot be found on its host site (name or slug
greps come up empty, folder number collides, or the brief cites files that don't exist).

> Proven 4x on cryptohack_org (2026-11-02/03): `polynomials-with-errors`, `ecclcg2`,
> `partial-key-recovery-short-vector` (#106), `short-vector-recovery-code` (#113), plus
> `short-pad-code` (#127). Signature: dispatch slug carries a bogus `-code` suffix (site
> slugs truncate at 29 chars), the brief cites helper files/sections that don't exist on
> disk, and the folder number already belongs to a different solved challenge.

## Order of checks (all cheap, run in this order)
1. **Site is authoritative:** scrape ALL category pages (for cryptohack: 14 slugs under
   `/challenges/`; cards carry `id="check-<slug>"` + `.challenge-text` name — that pair is
   the slug map; category detail pages 302 for BOTH real and fake slugs via curl, so they
   prove nothing). Token-scan every slug+name for the brief's words.
2. **Total-count diff vs inventory:** sum of category counts == inventory total means the
   site set is unchanged (no new challenge hiding).
3. **API ground truth:** `/api/user/<user>/` solved list — also answers "which open
   challenge could the parent have meant?" If the whole family is already 100% solved,
   no open candidate exists. First curl can return an EMPTY body (silent truncation) —
   retry via urllib with UA header and length check before trusting.
4. **Organizer GitHub, directory names only** (e.g. `api.github.com/repos/<org>/<repo>/contents`):
   catches archive challenges not yet on the site listing. Never open file contents.
5. **Ledger collision:** look up the dispatch folder number in progress.json — phantoms
   routinely reuse the number of an unrelated SOLVED challenge.
6. **Corpus grep** for the dispatch line + name (README/progress/kanban) — the queue entry
   usually exists only in the parent's context.
7. **Validate the brief's own citations** (named files, named doc sections) with rg on
   disk. Fabricated arsenal sections / helper scripts are part of the phantom signature —
   report them explicitly so the parent can fix its queue generator.

## Outcome contract
- **Do NOT create the challenge folder** (implies a verbatim statement exists) and never
  substitute a "nearby" challenge — that contaminates the ledger.
- Write `PHANTOM-<slug>.md` in the site dir: evidence list with numbers (counts, API
  score/solved, grep hits, 404 probes), nearest real referents + their solved status,
  gate/engine accounting (if 0 solver invocations, say so — 'no rank/timeout/aborted
  numbers to report'), full configuration section, and a bolded **DO NOT re-dispatch
  without a slug confirmed on a fresh scrape** line.
- Append a `phantom-task check #N` session-log entry to the SITE README in the same turn.
- Return banked=false with the phantom verdict as `wall`; cite the PHANTOM file path.

## Why
Reading a fabricated brief as real burns the fleet budget (a solver can spend hours
building a Kannan pipeline for a lattice that was never served) and a fabricated
solution would poison the AAR corpus. The evidence-pack negative is the success case:
auditable, citeable, and it prices the parent's queue generator against disk truth.
