# AGENT.md — machine-readable campaign facts
Vocabulary: [OBSERVED] event captured in-tree · [NOT OBSERVED] checked, absent ·
[UNKNOWN] not determinable from published evidence. Claim IDs stable: A-nnn.

A-001 [OBSERVED] Ledger 2026-11-10: 316 solved rows (231 challenges, 85 courses), baseline 85 (2026-10-07). src: LEDGER/progress_sanitized.json
A-002 [OBSERVED] Site scoreboard 11-10 screenshots: level 33, 17195 stars, rank #5. src: README
A-003 [OBSERVED] archive.cryptohack.org:21970 emits 319-byte banner + silence; sha256 prefix 8ef798aae9a0d378 stable across 38+ captures 10-27→11-10. src: CHALLENGES/ctf-archive/challenge-246-*/AAR.md
A-004 [OBSERVED] Same host, other ports: full interactive solves 10-19→11-09 (8+ ports). Kills host-level and client-level hypotheses by flags, not banners. src: AAR cross-sweep section, 246
A-005 [OBSERVED] Upstream commit 91a4a745 (2026-09-29) switched 246's base image python:3.10→3.12; `rmax = 2**128 / N / 4` then `randint(0, float)` is fatal ≥3.12; byte-identical local repro on python:3.12. src: 246 AAR + github raw
A-006 [NOT OBSERVED] Any capture >319 B from :21970, including menu interaction, in the whole capture window.
A-007 [UNKNOWN] Whether individual third-party leaderboard solves used the live service; submission API cannot show method.
A-008 [OBSERVED] 237/265 dual instance share one flag via digit-stream hash-binding forgery; exploit in CHALLENGES/zkp/challenge-237-*/ (solve*.py).
A-009 [OBSERVED] Model attribution: phase-level only; no per-message model IDs logged. [UNKNOWN] finer attribution.
A-010 [OBSERVED] Three flags redacted in ledger; published as null+note, never reconstructed.

## Decision rules learned (transferable)
R-1 dead-service 4-test + A/B live control before declaring an endpoint dead, and again before declaring it alive.
R-2 shape-audit before compute; bounded searches with stated probability gates (Poisson/Pollard bounds written down pre-run).
R-3 owner-facing verification tools print raw bytes/hashes only; verdicts are not authored by the tool.
R-4 flag provenance classes recorded at solve time (retro-classification degrades honestly).
R-5 retracted claims stay visible: retraction is an edit to the AAR, not an overwrite of history.

## Anti-patterns logged
- Reading banners for days while never sending bytes.
- Grinds without a falsifiable bound.
- Verdict-instrument circularity (tool restates its author's hypothesis as output).
- Atmosphere-claims about other players' methods.
