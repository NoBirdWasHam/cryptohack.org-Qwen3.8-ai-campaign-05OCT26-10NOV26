# AAR — Curveball (curveball, 100 pts, ECC course)

## Result
SOLVED 2026-10-07 (first solve session, ECC course track).
Flag: NOT archived (solved before the flag-archiving convention; the challenge is in the
live solved list as of the 2026-10-17 verification).

## Attack
The server takes MY "generator" `g` (no validation) and computes `Q = g * d`, then matches
`Q` against its trusted-cert cache. Send `g = Q_bing` (Bing's trusted public key) and
`d = n + 1` (P-256 order + 1): `Q = (n+1) Q_bing = Q_bing + n Q_bing = Q_bing + O =
Q_bing` — a cache hit for Bing's cert without solving any DLP or changing the curve.
Protocol: one JSON object over the socket (private_key, host, curve, generator [x,y]).

## Verification
- `solve.py` (archived) performs the single-socket attack; `verify_math.py` checks
  `(n+1)*Q_bing == Q_bing` locally.
- Flag not archived (see Result).

## Evidence
- `source_provided.py`, `solve.py`, `verify_math.py`


## Limitations / attempts that failed
None recorded — solve.py's single-socket attack worked on the first try (2026-10-07 session); no
failed attempts are in the run notes. Evidence limit (not a failure): the flag STRING was never
archived (pre-convention solve); solved-list presence was verified 2026-10-17.

## Sources
Server behavior + provided `source_provided.py`; P-256 group law (order n ⇒ (n+1)·Q = Q); archived
`solve.py` + `verify_math.py`; self-derived; no writeups consulted.
