# Sources referenced during the campaign (and where)
Format: source → what it grounded → which artifact cites it.

## Platform
- https://cryptohack.org + /challenges/<slug>/ + /api/user/<name>/ → rules of the game,
  solved-list verification, leaderboard facts → FLAGS/flags.jsonl URLs; challenge AARs.
- https://cryptohack.org/scoreboard/ → dated screenshot values (README headline).

## Authors' materials (linked, never re-hosted — owner decision 11-10)
- Each challenge's own statement/attachment: linked from the challenge page → per-dir AARs.
- Official writeups, **disclosed per doctrine** (we consult only AFTER recording our own
  result, and AARs mark which phase consulted what):
  - github.com/cscbe/CSCBE-2024-WRITE-UPS (challenge 246 author repo — consulted after our
    attack was verified; our exploit predates it) → CHALLENGES/ctf-archive/challenge-246-*/AAR.md.
  - zeus.ugent.be player writeup (246) → same AAR, "2 writeups total" statement.
  - github.com/cryptohack/ctf_archive (deployment code: Dockerfiles, server.py history) →
    the 246 root-cause finding (commit 91a4a745, 2026-09-29, python-base:3.12).

## Canonical papers referenced by the skills/AARs
- Pollard 1978 (kangaroo DLP) · van Oorschot–Wiener 1999 (parallel kangaroo) → interval-dlp skill, 294/spongebob row.
- van Dijk–Gentry–Halevi–Vinograd 2012 (DGHV FHE) → challenge 246 attack shape.
- Fan–Vercauteren 2012 / FHEW 2014 lineage → DGHV-family misc rows.
- Keccak team 2012 (sponge construction) → sponge-keccak skill; 294.
- Goldreich–Micali–Wigderson 1989; Goldreich–Micali–Wigderson/ZK proofs; Fischlin 2008;
  Fiat–Shamir 1986 → zkp rows incl. 237/265 forgery.
- Matsumoto–Kim 1998 (MT19937) → mt19937 skill (tetctf 2020 analysis).
- Coppersmith 1996 / Boneh–Venkatesan 2001 → coppersmith-* skills, RSA rows.
- Lenstra–Lenstra–Lovász 1982; Kannan 1987 embedding → ctf-lattices, gp-kannan-msp.
- Hoffstein–Pipher–Silverman 1998 (NTRU) → ntru-* skills.
(Machine-readable list: SOURCES.yaml alongside this file.)
