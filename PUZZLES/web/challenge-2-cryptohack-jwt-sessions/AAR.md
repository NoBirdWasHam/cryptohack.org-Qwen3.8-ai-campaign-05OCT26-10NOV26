# AAR — JWT Sessions (jwt-sessions, 10 pts, Web course)

## Result
SOLVED 2026-10-12. Flag (non-standard string): `[flag — recorded in FLAGS/web/challenge-2-cryptohack-jwt-sessions/flag.txt]`
Submitted via user API in the 2026-10-12 session; accepted; present in the live solved list
(2026-10-17 verification).

## Attack
The "session" is a JWT, not a cookie — and it is transported in the `[flag — recorded in FLAGS/web/challenge-2-cryptohack-jwt-sessions/flag.txt]` header
(the flag is the header name itself). Read where the token lives (header vs cookie) per the
challenge statement.

## Verification
Server-accepted flag string archived in progress.json. (Course challenge; no artifacts
archived beyond the backfilled statement in site.md.)

## Vulnerability (plain words)
Observation lesson, not an exploit: the site's "session" is a JWT carried in an HTTP request header rather than a Cookie, and the challenge answer is simply the name of the header that carries it.

## How the answer follows
1. Per the statement, inspect where the session token travels ⇒ the JWT is transported in the `[flag — recorded in FLAGS/web/challenge-2-cryptohack-jwt-sessions/flag.txt]` header (not a cookie).
2. The flag IS that header name: bare non-crypto{} answer `[flag — recorded in FLAGS/web/challenge-2-cryptohack-jwt-sessions/flag.txt]`, submitted via user API 2026-10-12, accepted; present in the live solved list (2026-10-17 verification).

## Limitations / attempts that failed
- Nothing failed; no further steps recorded in run logs. No artifacts archived beyond the backfilled statement in site.md.

## Sources
Course statement (site.md backfill) + observed token transport. No external reference cited in run logs; no writeups consulted.
