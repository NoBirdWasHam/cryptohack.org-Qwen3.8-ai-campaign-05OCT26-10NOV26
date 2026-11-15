# AAR — Introduction to Isogenies (iso_introduction_chall)

## Result
**SOLVED.** Flag = `65537` (bare integer). Submitted 2026-10-12, +10 points (score
6380 → 6390), API-verified via `submit_flag.py` score_delta.

## Source
- Statement page: https://cryptohack.org/challenges/isogenies/ (the section intro; this
  challenge is the "wall of text" itself — the answer lives in its final paragraph).
- No provided files. No `/solutions/`, `/solves/`, or search-engine writeups consulted.

## The flag (and verification)
`65537` — bare integer (answer-type challenge; no `crypto{}` wrapper). Verified by
`submit_flag.py`, which reports a `score_delta > 0` (a real solve) and re-reads the
account API before/after.

## How it was solved
1. Read the section intro. The question: *"what would the size of a kernel be for a
   separable isogeny of degree 65537?"*
2. The text defines separable isogenies earlier: *"the degree of the map is exactly
   equal to the size of the kernel."*
3. Therefore kernel size = degree = **65537**.
4. Submitted the bare number via `submit_flag.py iso_introduction_chall 65537`.

No computation needed — this is a reading-comprehension check on the definition.

## Learning points
- For a **separable** isogeny, deg(φ) = #ker(φ) exactly. (For a *non*-separable /
  inseparable isogeny in char p, the degree = [ker size] · p^e where e is the
  inseparability exponent — the "size of the kernel" as a scheme is p^e times the
  geometric kernel.) The challenge tests that you can find the definition and apply it.
- Answer-type challenges want the **bare value** (see `ctf-answer-challenges`).

## What I did / did not do
- Did: read the provided statement, applied its own definition, submitted the flag.
- Did not: use any external writeup or the solutions page.

## Limitations
None — flag submitted and API-verified.

## Configuration
- Date: 2026-10-13 09:37 UTC (AAR written; solve submitted 2026-10-12).
- Host: Windows 11, shell bash (git-bash/MSYS), user OWNER.
- Interpreter: Python 3.12.0 (venv `~\tools\crypto-ctf\venv`).
- Working dir: `~\Practice_runs\cryptohack_org`.
- Tools: `submit_flag.py` (cookie + requests, no browser). No gp64 needed for this one.
- Network contact: cryptohack.org (statement scrape) + API (submit/verify).

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
