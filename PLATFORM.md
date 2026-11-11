# CryptoHack — platform notes (as observed, Oct–Nov 2026)
- Site: https://cryptohack.org — learn-by-doing cryptography exercises, categories from
  basics to research-level (RSA, ECC, isogenies, ZKP, post-quantum, a large CTF-archive pool).
- Community: explicitly friendly/learning-oriented; Discord-linked; public scoreboard
  (https://cryptohack.org/scoreboard/).
- **Honor system.** Submission is pasting a flag string; there is no proctoring, no separate
  AI track, and rules against flag-sharing are not technically enforced. Humans can and do
  look up flags. That is context, not an excuse: our doctrine (FLAGS/PROVENANCE.md) is stricter
  than the platform.
- **Etiquette decision (owner, 2026-11-10):** because the leaderboard is honor-system and this
  was a learning campaign, the account's score will be **cleared as a courtesy** after this
  documentation was verified and before upload, with per-batch reclearing (BATCHES.md).
- Archive services observation, dated: archive challenges run one container per port under
  `archive.cryptohack.org`. Observed states with evidence in-tree: healthy solves through
  2026-11-09 on multiple ports; `:21970` (challenge 246) dead since its 2026-09-29 base-image
  bump; `:63222` (tetctf 2020) serving a build that differs from the published repo;
  hamiltonicity pair historically served an older build. Live ≠ repo, sometimes.
