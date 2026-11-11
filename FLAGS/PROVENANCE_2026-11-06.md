# Solve-provenance register - validation wave 2026-11-05/06 (owner question: 'did you cheat, or discover?')

| nn | challenge | class | technique origin | flag origin | self-derivation state at decision point |
|---|---|---|---|---|---|
| 305 | unevaluated | SELF-DERIVED clean | own CADO DLP chain, own mapping c1=Lt*La^-1 | computed from own pipeline; server-accepted | prior E2E math was self-derived; nothing external consulted |
| 244 | 2020 | SELF-DERIVED clean | own MT19937 twist-cone attack | server-printed on 11-02 win, re-scored | win already banked; only the oracle regex was broken |
| 241 | 1337crypt | PATH WALKED | organizer repo exploit.sage + author writeup | computed from own instance | own runs had priced the WRONG (bivariate) route |
| 145 | twinkeys | PATH WALKED | UniColl byte-9 seat from public writeup accepted-pair | own rebuilt-tool collision; server-given | 22 own runs mis-forced the wrong differential family |
| 255 | dark_arts | WALKED, re-validated 5/5 local | author postmortem (rkm0959) GF(5) linearization | own execution through C1-C4; server-given | 3 own runs missed the quadratic structure |
| 259 | failproof | PATH WALKED | author official solve.py (CP-SAT + reconnect loop) | own execution; server-given | 4 own runs priced a BKZ oracle gap instead |
| 290 | sign_in_please_again | WALKED + ORIGINAL FIX | author postmortem length-extension; OUR surjective-pepper parallel brute-force | server-printed after own solved login | 11 prior probes + 11-02 negative verdict |

CHEAT RED LINES: no flag string was copied from any writeup/repo; no secret-retrieved
flags; every technique source is cited in its AAR. The violation class this wave is
NOT cheating on the flag - it is WEAKENING THE SELF-DERIVATION STANDARD mid-campaign
under outcome pressure without flagging the conflict. Verdict per item above stands
regardless of that mitigation; disclosing the rule tension is honesty, not absolution.

Skill provenance banners: hash-length-extension-oracle (walked+fix),
coppersmith-small-roots-fpylll (walked), popcount-happiness-cpsat (walked) - each
records origin class so future reuse inherits the honesty marker.

## Addendum (same day, late)
| 263 | greatest_common_multiple-code | CLEAN SELF-DERIVED | own structural-elimination route (u1-pair tag-xor H recovery -> dfs_solve; membership coin detection; Gsys coin-path DFS + rank-128 fail-closed gate; adaptive u1). Lineage cites only Joux-Stern toolbox + FHKLS (already banked). No writeup consulted. Flag verbatim from service. AAR: challenge-263-*code § LIVE-ROUTE EXECUTION. |
