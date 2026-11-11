# AAR — Token Appreciation (token-appreciation, 5 pts, Web course)

## Result
SOLVED 2026-10-12. Flag: `crypto{jwt_contents_can_be_easily_viewed}`
Submitted via user API in the 2026-10-12 session; accepted; present in the live solved list
(2026-10-17 verification).

## Attack
JWTs are base64url-encoded JSON — the payload ("claims") is readable by anyone. Decode the
middle segment of the provided token to read the flag. No key, no forgery: the lesson is
that JWTs are signed/encrypted, not obfuscated-by-default.

## Verification
Server-accepted flag string archived in progress.json. (Course challenge; no artifacts
archived beyond the backfilled statement in site.md.)

## Vulnerability (plain words)
A JWT is not encrypted — the payload ("claims") is just base64url-encoded JSON, readable by anyone who ever sees the token. This course challenge hides its flag inside those claims to teach exactly that.

## How the answer follows
1. Split the provided token on '.' and base64url-decode the middle segment ⇒ JSON claims contain `crypto{jwt_contents_can_be_easily_viewed}`.
2. Submitted via user API 2026-10-12; accepted; present in the live solved list (2026-10-17 verification).

## Limitations / attempts that failed
- Single-step course solve; nothing failed and no further steps recorded in run logs. No artifacts archived beyond the backfilled statement in site.md (exact decode command not recorded).

## Sources
Provided token from the course statement (site.md backfill). No external reference cited in run logs; no writeups consulted.
