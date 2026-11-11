# PROVENANCE_2026-11-08 — 257 / 273 / 280 / 297
Reconstructed 2026-11-08 (not from memory) from: challenge-folder AARs, logs, receipts, session file mtimes,
live user API. Governing policy (revised same day, owner audit): general textbooks/papers/libraries/generic
implementations = research sources; material authored for the same instance (author repos, solver scripts,
READMEs, writeups) = challenge-specific SOLUTION sources — permitted, but classify the solve WALKED/SOURCE-ASSISTED
and disclose chronology.

## 257 — ECLCG (HITCON CTF) — SOLVED_ACCEPTED (API 310->311, 2026-11-08)
- Flag origin: LOCALLY DERIVED — AES-CTR decrypt (key=sha256(str(d))) of folder file output.txt; identical on
  independent re-run. d verified by ALL 17 ECDSA r-checks (independent of any source).
- Attack-method origin: WALKED — author repo file
  https://github.com/maple3142/My-CTF-Challenges/blob/master/HITCON%20CTF%202024/ECLCG/solution/solve2.py
  fetched 2026-11-08 BEFORE derivation; ported as algorithm only (solve3.py variant tried earlier the same day and
  abandoned).
- Instance-data origin: static challenge files already in folder (output.txt from the CryptoHack instance).
- External exposure chronology: author repo (README + solution dir) fetched -> ported -> synthetic-control gate ->
  real run. Repo solution-comment string later matched the decrypted plaintext (expected for the static archive
  instance; never used in derivation — noted transparently because plaintext identity is unfalsifiable post-hoc).
- Final value came from: computation (locally verified), then service acceptance 2026-11-08.

## 273 — Leet Universe (ImaginaryCTF Daily) — SOLVED_ACCEPTED (API 308->309, 2026-11-07 17:2xZ)
- Flag origin: SERVICE-GIVEN — verbatim live-server output under g=R (275 digits >= len(flag)); NOT the OSINT
  string (archive shows only truncated form).
- Attack-method origin: SOURCE-ASSISTED (reclassified from "self-derived" today). Same-turn web_search run to
  locate the owner-gated OSINT value surfaced imaginaryctf.org/ArchivedChallenges/47 BEFORE the exploit:
  entry contains the author's one-line idea "you don't really need to factor the resultant as computing polynomial
  gcd is enough" — the decisive hint for Euclid-in-(Z/RZ)[x]. Chronology per AAR: hint exposure precedes exploit
  construction in the same turn; factoring-R was abandoned as unnecessary immediately after.
- Instance-data origin: live service interaction only.
- Date correction: ledger row said 2026-11-03 (derivation-era); acceptance is 2026-11-07 per AAR-recorded HTTP 200
  + API name verification (no standalone receipt file existed then; SUBMIT_RECEIPT convention adopted 2026-11-08).
- ECM ladder erratum: ecm_ladder_273.log kept running after the solve; last line 2026-11-08 09:41:56Z, stage
  1100000, curves 26550/50000 — never completed, no stop reason recorded, process confirmed gone 2026-11-08.
  Long-odds by our own ECM/NFS budget math; should have been stopped at solve. Oversight logged.

## 280 — Origami (NNS CTF 2025) — SOLVED_ACCEPTED (API 311->312, 2026-11-08 17:22:25-05:00)
- Flag origin: LOCALLY DERIVED: sigma-bit linear solve over pair sums -> try_f decrypt of provided ciphertext;
  regenerable byte-identical from frozen inputs (t280_fpm_h.cur.fplll sha256 b652717c…, output.txt 99f979f0…,
  REAL_FPP_RECOVERED.txt cc752411…) via t280_fin2.py (regen Bw_cands=8; FLAG_FOUND.txt never used as input).
- Attack-method origin: SELF-DERIVED — AAR records explicitly "no third-party solutions/writeups consulted"
  (lines ~78, ~159; provided materials + service interaction only). Folding/lattice/sigma structure developed
  across the campaign per AAR history. ERRATUM 2026-11-08 (audit round 4): a prior version of this section implied owner direction was goal-level only — WRONG. The owner's 11-07 ruling (PROVENANCE_2026-11-07.md) explicitly named the NTRU key-recovery family list for 280 including 'Atamagorodov-Coster folding'. Per that ruling, published-family names are in-scope method inputs, not contamination; the ruling mandates an AAR annotation which was missing and is now added. No per-instance solution content was ever supplied or consulted. Budget calls by the owner remained goal-level
- Instance-data origin: provided challenge files + earlier live-service interactions (recorded in AAR).
- Service: HTTP 200 accepted once; SUBMIT_RECEIPT_2026-11-08.json (command line, before/after counts 311->312,
  timestamps). Score +0: archive card is 0-point by design.
- Same-day erratum: two conflicting internal claims retracted (early: "SOLVED" with the WRONG flag belonging to
  297; later: "f+- NOT found, stays open" read from the fplll wrapper tally while the finisher had already fired
  at 14:41). See ledger notes + ERRATA_E4.

## 297 — Sus (ImaginaryCTF) — SOLVED_ACCEPTED (API 309->310, 2026-11-08)
- Flag origin: LOCALLY COMPUTED — from supplied instance data once p known; p found by Bach-Shallit-style gcd in a
  random cubic (Z/n)[x] ring (n = p(p^2+p+1)r form), try 3; q,r primality checked.
- Attack-method origin: WALKED — author README: https://github.com/maple3142/My-CTF-Challenges/tree/master/
  ImaginaryCTF%202023/Sus/README.md (fetched 2026-11-08 BEFORE derivation). Execution independently performed
  (solve_cyc.py, re-run end-to-end persisted as evidence).
- Reclassification note: earlier label "flag self-derived, red line intact" was true for the FLAG but the METHOD
  is walked under the revised policy — corrected here and in the ledger; disclosure preserved.
- Service: accepted via API check (0-pt archive); challenge folder challenge-13393-cryptohack-sus-imaginaryctf2023.

## Cross-cutting
- Submission receipts: SUBMIT_RECEIPT_280_2026-11-08.json (new convention; retro-fitting earlier solves would be
  backfill — not done, disclosed instead).
- API snapshot for reconciliation: api_solved_names_20261108_pm.json (312 names; Origami/Sus/Leet Universe/ECLCG
  all name-verified).
