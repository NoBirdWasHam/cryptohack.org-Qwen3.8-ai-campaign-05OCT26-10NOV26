# AAR — JWT Secrets (jwt-secrets, 25 pts, Web course)

## Result
SOLVED 2026-10-12. Flag: `[flag — recorded in FLAGS/web/challenge-4-cryptohack-jwt-secrets/flag.txt]`
Submitted via user API in the 2026-10-12 session; accepted; present in the live solved list
(2026-10-17 verification).

## Attack
HS256 JWTs are only as strong as their HMAC secret. The challenge's secret is guessable /
crackable (weak or published) — recover it (dictionary / the provided hint), re-sign a
forged token with it, and the server accepts it.

## Verification
Server-accepted flag string archived in progress.json. (Course challenge; no artifacts
archived beyond the backfilled statement in site.md.)
## Vulnerability (plain words)
HS256 signs and verifies with the SAME symmetric secret, so every service that can verify a token can also mint one; and developers often pick a weak or default secret. Once the secret is known or crackable, "signature verification" is not a protection at all — the attacker recomputes the HMAC exactly as the server does and forges any session, including admin. The statement primes this directly: the shown code carries "a strange comment about the secret key".

## How the answer follows
1. A JWT's HMAC is computable by anyone holding the secret; recovering this challenge's weak/hinted secret therefore converts "cannot forge" into "one HMAC call from forging".
2. Re-sign a payload with elevated claims (`admin: true`), send it to the authorise endpoint; the server's own verification succeeds because the signature is genuinely valid under its secret — the only failed assumption was secrecy of the key.
3. The privileged response carries `[flag — recorded in FLAGS/web/challenge-4-cryptohack-jwt-secrets/flag.txt]`; server-accepted (2026-10-12, live-list re-verified 2026-10-17).
- Note: the exact recovered secret value and any wordlist used are not recorded in run logs.

## Limitations / attempts that failed
- No failed submission recorded in run logs.
- No token/request artifact archived (course challenge; accepted flag recorded via progress.json only), so the crack step cannot be re-verified from this folder.

## Sources
- Statement text (cached) — HS256 vs RS256 trade-off and the weak-secret hint.
- Public specs (about the formats themselves): RFC 2104 (HMAC), RFC 7518 (JWA/HS256).
- No third-party writeup or solution artifact consulted (source-disclosure rule).
