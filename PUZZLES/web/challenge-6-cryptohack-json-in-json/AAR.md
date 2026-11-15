# AAR — JSON in JSON (json-in-json, 40 pts, Web course)

## Result
SOLVED 2026-10-12. Flag: `[flag — recorded in FLAGS/web/challenge-6-cryptohack-json-in-json/flag.txt]`
Submitted via user API in the 2026-10-12 session; accepted; present in the live solved list
(2026-10-17 verification).

## Attack
JSON injection: the server embeds user-controlled JSON INSIDE another JSON document without
proper serialization, so crafted input breaks out of the string and injects new fields
(the OWASP Injection Theory the flag links to). Craft the payload so the inner JSON adds /
overrides the field that carries the flag.

## Verification
Server-accepted flag string archived in progress.json. (Course challenge; no artifacts
archived beyond the backfilled statement in site.md.)
## Vulnerability (plain words)
Double serialization without proper re-escaping: the server embeds user-controlled JSON *inside* another JSON document (a string field of what will become a JWT). If escaping is done once, wrongly, or at the wrong layer, crafted input closes the enclosing string mid-JSON and injects NEW fields into the inner document. The signature is no defense here — per the statement the code will happily *sign unexpected data*: a signature proves WHO signed, never WHAT was signed, so injected claims ride the signature into trust. This is OWASP Injection Theory — a data/code boundary crossing, structurally the same as SQL injection.

## How the answer follows
1. The server signs whatever the inner JSON parses out to; escaping failure means attacker text becomes parsed structure inside the signed payload.
2. Craft a value that breaks out of the string context and adds/overrides the claim that governs authorization; the server then signs the tampered claims and its own verifier trusts them (the signature now covers the attacker's field, exactly as if it had been legitimate).
3. The privileged response carries the flag — and the flag value IS the lesson pointer: `[flag — recorded in FLAGS/web/challenge-6-cryptohack-json-in-json/flag.txt]`. Server-accepted (2026-10-12, live-list re-verified 2026-10-17).
- Note: exact crafted payload bytes are not recorded in run logs (guided in-browser course flow).

## Limitations / attempts that failed
- No failed submission recorded in run logs.
- No request/response artifact archived (course challenge; accepted flag recorded in progress.json), so the payload cannot be re-verified from this folder.

## Sources
- Statement text (cached) — "exploit the code to sign unexpected data"; the flag itself links OWASP Injection Theory.
- Public spec (about the format itself): RFC 8259 (JSON string escaping rules — the layer where the bug lives).
- No third-party writeup or solution artifact consulted (source-disclosure rule).
