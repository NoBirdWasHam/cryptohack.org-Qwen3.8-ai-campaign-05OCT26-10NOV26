# AAR — 276-cryptohack-or_proof-cryptohack2024: OR Proof (CryptoHack) — CTF Archive

**Result:** SOLVED (0 pts — archived challenges count toward solved only; solved 174→175)
**Date:** 2026-10-19 (UTC)

## What this challenge is
The CTF-2024 original of the current `sigma-or-proof` challenge (231, ZKP, 75 pts).
Both slugs run on the **same server** `archive.cryptohack.org:11840`, and the **same flag**
satisfies both. No separate attack was needed.

## The flag
Recorded in `FLAGS/ctf-archive/challenge-276-cryptohack-or_proof-cryptohack2024/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## How it was solved
Solved as part of the 231 sigma-or-proof run (2026-10-19): 3-phase OR-protocol protocol —
honest proof on the witnessed branch (w0 shipped in `chal.py`), witness extraction from the
double transcript (special soundness), SHVZK simulation for the given `s`. Full details,
flag ground truth, and the regex-grab protocol pitfall are in
`../challenge-231-cryptohack-sigma-or-proof/AAR.md`.

## Why this folder is thin
No distinct work was done for the archive slug; this folder exists so the queue entry
(`progress.json`, nn 276) has an AAR per the folder contract. Statement provenance:
CTF archive page scrape (the 231 folder holds `ctf.html`/`archive.html` with the entry).

## Configuration (environment for this run)
- **Date:** 2026-10-19 (UTC)
- **Host OS:** Windows 11, shell = git-bash/MSYS
- **User:** OWNER
- **Interpreter:** venv `~\tools\crypto-ctf\venv\Scripts\python.exe`
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-231-cryptohack-sigma-or-proof` (shared)
- **Agent:** Hermes Agent (desktop); submission via `submit_flag.py`
- **Network:** `archive.cryptohack.org:11840`; cryptohack.org API for verification


## Limitations / attempts that failed
None in this folder — no distinct attack was attempted for the archive slug. The limitations are
inherited from the 231 sigma-or-proof run (see `../challenge-231-cryptohack-sigma-or-proof/AAR.md`),
including its regex-grab protocol pitfall. Folder thinness is scope, not failure: statement provenance
is a CTF archive page scrape.

## Sources
Canonical solve record: `../challenge-231-cryptohack-sigma-or-proof/AAR.md` (same server
archive.cryptohack.org:11840; the same flag satisfies both slugs — one credit per slug in the ledger).
No third-party writeups.
