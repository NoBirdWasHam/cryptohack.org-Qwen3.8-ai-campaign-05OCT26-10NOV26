# AAR — Saying Hello (saying-hello, 20 pts, Web course)

## Result
SOLVED 2026-10-13. Flag (non-standard string): `[flag — recorded in FLAGS/web/challenge-156-cryptohack-saying-hello/flag.txt]`
Submitted via user API in the 2026-10-13 session; accepted; present in the live solved list
(2026-10-17 verification).

## Attack
TLS handshake reading: the client's `ClientHello` and the server's `ServerHello` exchange
cipher suites in the clear. The flag is the negotiated cipher suite — read it from the
handshake (the challenge provides the handshake to inspect).

## Verification
Server-accepted flag string archived in progress.json. (Course challenge; no artifacts
archived beyond the backfilled statement in site.md.)
## Vulnerability (plain words)
None — observation-type, no crypto to break. TLS negotiates its parameters (version, cipher suite) in the clear during ClientHello/ServerHello, on purpose: confidentiality only starts after the handshake keys are established. The challenge asks you to read the negotiated suite out of the handshake, i.e. to understand what a suite name means, not to attack anything.

## How the answer follows
1. The negotiated suite is the single cipher-suite ID the *server* echoes in its ServerHello (the client only offers a preference list, so the server's echo is the authoritative answer).
2. Decoding the name: `ECDHE` = ephemeral ECDH key exchange (forward secrecy), `RSA` = server authentication/signing, `AES256-GCM` = AEAD bulk cipher (256-bit key), `SHA384` = PRF/hash. The human-readable string of that ID *is* the answer: `[flag — recorded in FLAGS/web/challenge-156-cryptohack-saying-hello/flag.txt]`.
3. Submitted through the user API (2026-10-13) and accepted; re-verified present in the live solved list on 2026-10-17.

## Limitations / attempts that failed
- No failed submission recorded in run logs.
- The specific reader/tool used to view the handshake was not recorded (course challenge; the handshake to inspect was provided by the challenge itself, and no capture artifact was archived beyond the backfilled statement in site.md).

## Sources
- Statement text (cached) — it defines record format and suite-name components.
- Public spec (about TLS itself): RFC 5246 appendix A (cipher-suite naming/IDs).
- No third-party writeup or solution artifact consulted (source-disclosure rule).
