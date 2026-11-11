# Flag provenance doctrine (the campaign's red line)
1. A submitted flag is only ever **self-derived** (computed by our code from the challenge's
   own math) or **service-given** (printed by a live challenge service to us).
2. A flag **retrieved** from elsewhere (author repos, solution dumps, other players) is never
   submitted. If an external source teaches us a *method*, the AAR discloses source + phase,
   and the flag is still independently derived. Disclosing a violation is honesty, not absolution.
3. Classes used in flags.jsonl:
   - `WALKED` — service printed the flag to us and we submitted exactly that.
   - `SERVICE-GIVEN` — service-supplied during interactive solve, equivalent provenance.
   - `PRE-LEDGER-ERA` — solved before the 2026-11-06/07/08 ledgers formalized classes;
     provenance is honest-but-uncertified for those rows. Labeled, not smoothed over.
4. Three solved rows carry redacted flags in the ledger (e.g. `crypto{...}`); flags.jsonl
   marks them `FLAG-NOT-IN-LEDGER`. We never fabricate a flag value.
5. Closed-unsolved rows stay unsolved in every artifact (row 246).
