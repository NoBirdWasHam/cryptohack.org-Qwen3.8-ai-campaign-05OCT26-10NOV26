---
name: public-solve-verification
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, cryptohack, audit, publication]
    related_skills: [cryptohack-aar-corpus, ctf-practice-runs]
---

# Public-solve verification (CryptoHack)

## When to Use
Deciding which challenges in the corpus have published solutions (site or third-party)
— for publication value or practice-value triage. Read-only: never write into the
audited tree; web artifacts go to scratch only.

## Layer 1 — site solutions (canonical)
Source: category pages `https://cryptohack.org/challenges/<category>/` — readable
without login, server-rendered. The `/solutions/` landing is a limited recent/top view
only; per-challenge solution pages are completion-gated (login + challenge solved), so
category-page rows are the only public view of solution counts.

Working category set (14): introduction, general, aes, maths, rsa, diffie-hellman,
ecc, hashes, web, post-quantum, misc, isogenies, zkp, ctf-archive.
`symmetric` and `lattices` misbehave as category names (redirects) — follow redirects
or drop them; `aes` is the live name for the symmetric block-cipher category.

Per-row parsing anchors (category HTML):
- slug: `data-challenge="([^"]+)"`
- display name: `class="challenge-text truncate">([^<]+)</div>`
- solves: `<span id="solves-[^"]+">(\d+) Solves</span>`
- solutions: `/solutions/">\s*(\d+)\s*Solutions?\s*</a>`

Cross-check the parsed slug count against the ledger queue count — a 1:1 match means
the scrape is complete.

## Ledger ↔ site matching
Match by NORMALIZED DISPLAY NAME, never by slug: ledger `slug` values can be None or
carry the display name, and site names contain HTML-escaped punctuation.
Normalization that works: `re.sub(r"\s+", " ", html.unescape(s)).lower().strip()`.
The `html.unescape` is load-bearing — without it, escaped apostrophes leave a handful
of names unmatched. Verify the mapping is 1:1 before reporting any counts.

Report shape: total with ≥1 published solution vs zero; then per-open-entry
`solutions` + `solves` counts (open entries are the decision-relevant set).

## Layer 2 — third-party writeups (for the zero-site-solution set)
Query per SOURCE CTF, not per challenge: `"<CTF name> <year> writeup [challenge word]"`.
Calibrated vocabulary only: Observed (location cited) / Not observed (searched, none in
top results) / Unknown (not searched). CTF-level writeup existence is NOT
per-challenge confirmation — say so explicitly when only the CTF level is confirmed.

Common public-writeup locations (observed patterns): author blogs, author challenge
repos (personal My-CTF-Challenges-style repos, official CTF GitHub repos with writeups
dirs), the CTFtime writeup aggregator and per-task pages, public gists.

## Contamination rule (hard)
Writeup searches return FULL solution text inside the snippets. Record the LOCATION
(URL) only. Never ingest snippet solution content into a solve context, never quote it
into an AAR, and flag to the owner that a puzzle with a confirmed public writeup is no
longer cleanly self-solvable — its remaining value is corpus/audit value.
