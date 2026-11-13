# AAR — No Way JOSE (no-way-jose, 20 pts, Web course)

## Result
SOLVED 2026-10-12. Flag: `[flag — recorded in FLAGS/web/challenge-155-cryptohack-no-way-jose/flag.txt]`
Submitted via user API in the 2026-10-12 session; accepted; present in the live solved list
(2026-10-17 verification).

## Attack
The Cryptographic Doom Principle: a single token carrying BOTH a signature and encryption
is attackable — tamper with the JOSE header (e.g., flip the `alg` so the verifier checks a
signature you can produce, or drop the encryption layer) and the "protected" payload is
yours. The challenge walks the JOSE header fields to set this up.

## Verification
Server-accepted flag string archived in progress.json. (Course challenge; no artifacts
archived beyond the backfilled statement in site.md.)
## Vulnerability (plain words)
The server must read the JOSE header — which is attacker-controlled and NOT covered by any integrity check — *before* it knows how to verify the token. Choosing the verification recipe is therefore delegated to the attacker. The canonical instance (named in the statement) is `"alg":"none"`: the library honors a token that declares itself unsigned and skips signature checking entirely. This is Moxie Marlinspike's Cryptographic Doom Principle — doing anything with untrusted input before verifying it "will somehow inevitably lead to doom" — and it emulated a bug that existed in many real JWT libraries.

## How the answer follows
1. The session token's integrity claim is conditional on the `alg` field; downgrade that field (the none-alg class of bypass) and the payload's privilege claims ("who am I" / admin bits) are never authenticated — so editing them in plaintext is sufficient to be served as the privileged user.
2. The broken session API then returns the flag to the newly-forged "authenticated" session; the flag text `[flag — recorded in FLAGS/web/challenge-155-cryptohack-no-way-jose/flag.txt]` is itself the lesson label: verify-before-parse.
3. Server acceptance (user API, 2026-10-12, re-verified in the live solved list 2026-10-17) confirms the bypass.
- Note: this was a guided course challenge; the step-by-step crafted-token detail beyond the alg-manipulation mechanism above is not recorded in run logs.

## Limitations / attempts that failed
- No failed submission recorded in run logs.
- No request/response artifact was archived (course challenge; only the server-accepted flag string lives in progress.json), so the exact token bytes cannot be re-verified from the folder.

## Sources
- Statement text (cached in statement.txt / site.md) — it names the none-alg issue and the doom principle.
- Public format specs (about JWT itself, not the solution): RFC 7515 (JWS header/`alg`), RFC 7519 (JWT claims).
- No third-party writeup or solution artifact consulted (source-disclosure rule).
