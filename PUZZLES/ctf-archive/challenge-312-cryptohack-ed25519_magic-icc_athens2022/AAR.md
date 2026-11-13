# AAR — ed25519_magic (ICC Athens), CryptoHack archive #312

**Solved:** yes. Flag: `[flag — recorded in FLAGS/ctf-archive/challenge-312-cryptohack-ed25519_magic-icc_athens2022/flag.txt]` (submit ok:true, solved-list 244→245, reconcile shows slug in LIVE solved set; archive challenges award 0 pts).

## The vuln
Server (`chal.py`) uses PyPI `ed25519==1.5` — C bindings to **ed25519-supercop-ref**
(floody-era code, pre-RFC-8032 hardening). Reading `crypto_sign_open` in
`src/ed25519-supercop-ref/ed25519.c` shows three missing checks:

1. **No `S < L` check** (and no `sig[63] & 224` check). `sc25519_from32bytes` runs
   `barrett_reduce` → S is silently reduced mod L.
2. **No subgroup check** in `ge25519_unpackneg_vartime` (accepts small-order points).
3. **No identity rejection**: y=1, x=0 decodes fine (x²=0 path, parity check passes
   for either sign bit).

Verification is `pack(s·B + h·(−A)) == R` as raw bytes, h = SHA512(R‖pk‖M) mod L.

## The attack
- **Level 1** (re-sign `b"CryptoHack"` with a different signature): send
  `R ‖ LE32(s + L)`. Different 64 bytes (passes `new_sig == sig` guard), same scalar
  after barrett reduction → identical check point → verifies.
- **Level 2** (supply vk + sig for an unseen random 16-byte msg): vk = identity point
  `01‖0*31`, sig = `01‖0*31 ‖ 0*32` (R = identity, s = 0). Then
  `0·B + h·(−O) = O` and `pack(O) = 01‖0*31 = R` for **any** message. Deterministic.

## Validation
- Pure-Python emulator of the exact C semantics (barrett-mod-L S, unpackneg parity
  rule `parity(x)=1−sign`, no checks) in `solve.py --local`: baseline sig accepted,
  both forgeries accepted.
- Live run against `archive.cryptohack.org:31144`: level 1 banner → level 2 → flag.

## Key numbers
L = 2²⁵² + 27742317777372353535851937790883648493; s+L < 2²⁵⁴ < 2²⁵⁶ always.

## Limitations
- Did not build the C extension locally (py3.12-era sdist on this host); validated
  against a hand-written emulator of the C code instead — the live server was the
  real ground truth.
- Small-order-A variant (order-8 torsion, 1/8 message-dependent) was considered and
  rejected as non-deterministic; identity-key is deterministic.
- First live attempt died on a client-side protocol-read bug (consumed the b64 line
  before the prompt); fixed, second attempt solved. No server-side failures.

## Learning points
- Pre-RFC reference implementations lack the canonical-form checks RFC 8032 §8.4
  mandates (S < L, and the cofactored equation). "Magic as originally conceived" =
  exactly these malleabilities.
- When a verifier reduces the scalar itself, `s + kL` is a free signature mutation.
- Identity public key + zero signature is a universal accept against verifiers that
  don't reject the small subgroup / identity — works even with unknown message.

## Vulnerability (plain words)
The server verifies Ed25519 through PyPI `ed25519==1.5`, C bindings to the pre-RFC ed25519-supercop-ref code. Reading `crypto_sign_open` in the shipped source shows the three canonical-form checks RFC 8032 later mandated are simply missing: S is Barrett-reduced mod L with no `S < L` test, public keys are accepted without a subgroup check, and the identity point (y=1, x=0) decodes as a valid key. Consequence: signatures are trivially malleable (s + L is the same signature in different bytes), and with an identity public key the verification equation `pack(s·B + h·(−A)) == R` collapses to `pack(O) == R` — a universal accept for ANY message.

## How the answer follows
1. Level 1 (must re-sign "CryptoHack" with different bytes): send `R ‖ LE32(s + L)` — all 64 signature bytes change (passes the `new_sig == sig` guard), Barrett reduction maps S back to s, so the check point and h are unchanged → verifies.
2. Level 2 (forge an unseen random 16-byte message with an attacker-supplied vk): vk = identity `01‖0*31`, sig = `01‖0*31 ‖ 0*32` (R = identity, s = 0). Then 0·B + h·(−O) = O and pack(O) = 01‖0*31 = R for every message — deterministic, message-independent. (s+L < 2^254 < 2^256, so the Level-1 mutation never overflows the 32-byte field.)
3. Validated before live: a pure-Python emulator of the exact C semantics (barrett-mod-L S, unpackneg parity rule `parity(x)=1−sign`, no checks) accepts the baseline signature and both forgeries (solve.py --local); the live run then cleared both levels and printed the flag.

## Limitations / attempts that failed
- Could not build the C extension locally (py3.12-era sdist on this host) — validation rested on the hand-written emulator plus the live server as ground truth.
- An order-8 small-torsion A variant was considered and rejected: only ~1/8 of messages satisfy the check; the identity key is deterministic.
- First live attempt died on a client-side protocol-read bug (consumed the b64 line before the prompt); fixed, second attempt solved. No server-side failures.

## Sources
chal.py + the shipped ed25519-1.5 source tree (src/ed25519-supercop-ref/ed25519.c: crypto_sign_open, sc25519_from32bytes, ge25519_unpackneg_vartime) + the live listener (archive.cryptohack.org:31144). RFC 8032 §8.4 used as the reference standard naming the missing checks (a standard, not a solution writeup). Flag came from the live service after our own forgeries; no third-party writeups consulted.
