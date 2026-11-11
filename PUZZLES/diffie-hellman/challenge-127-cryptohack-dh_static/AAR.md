# AAR — dh_static (100 pts)

**Result:** SOLVED — flag submitted, `score_delta: 100`. Date: 2026-10-15 (UTC).

## Source

- Statement: https://cryptohack.org/challenges/diffie-hellman/ (slug `dh_static`)
- Service: `socket.cryptohack.org:13373` (protocol in site.md)
- **NOT consulted:** /solutions/, /solves/, any external writeups. (No web search
  needed either — the attack follows from the protocol once you realize Bob
  returns (your g)^b.)

## Flag

`crypto{n07_3ph3m3r4l_3n0u6h}`

## How it was solved

1. Probed the protocol (3 probe scripts): phase 1 prints an intercepted DH
   conversation (fresh A per connection) + flag ciphertext; phase 2 asks me to
   send Bob `{p, g, A}`, and Bob returns `{"B": g^b mod p}` plus a fixed
   message under `SHA1(str(A^b mod p))[:16]`. **Bob uses my p and g.**
2. Verified the "static" part: Bob's B in the intercepted conversation is the
   SAME 1536-bit constant across every connection (6+ observations).
   `B_static = 0x8d79b693...94ebfa8ef0`.
3. Dead ends explored (documented for honesty):
   - `A=1` → shared = 1 → decrypts only the fixed chit-chat message, not the flag.
   - `A=P−1` with QNR g → shared = (−1)^b ∈ {1, P−1} → same fixed message.
   - Replaying Alice's A as my A → still only the fixed message.
   - P is a SAFE prime (P−1 = 2q, q 1535-bit prime; sympy), so no
     order-lifting via small subgroups.
   - BSGS for a small constant b < 2^46 (2^20 baby table, 67M giant steps,
     `bsgs_b.log`): **no hit** — b is not small.
4. The actual attack (the one-line insight): Bob's phase-2 reply field "B" is
   **(my g)^b mod p**. Choose `g = A` (Alice's public value from the
   intercepted conversation). Then Bob returns `A^b mod P` — the very shared
   secret the flag was encrypted under — in the clear. The static key is what
   makes phase-2's `A^b` equal the intercepted conversation's `A^b` (a fresh
   per-session b would give a different secret).
5. key = SHA1(str(A^b))[:16] → AES-128-CBC decrypt of the intercepted
   `{iv, encrypted}` → flag.

## Exact commands

```
~/tools/crypto-ctf/venv/Scripts/python.exe -u solve.py
cd ~/Practice_runs/cryptohack_org && python submit_flag.py dh_static "crypto{n07_3ph3m3r4l_3n0u6h}"
```

## Exact outputs

`solve.py` (full in `live_transcript_2026-10-15.txt`):
```
S: Intercepted from Alice: {"p": "0xffffffffffffffffc90fdaa22168c234c4c6628...
S: Intercepted from Bob: {"B": "0x8d79b69390f639501d81bdce911ec9defb0e93...
S: Intercepted from Alice: {"iv": "64686547c674f67334ec0945da4c51f2", ...}
B static across connections: verified
C: p=P, g=A (Alice's public value), A=1
S: Bob connects to you, send him some parameters: Bob says to you: {"B": "0xb1b00b48..."}
S: Bob says to you: {"iv": "b5d3a6de707df6916d63ab0d2dfe6e3b", ...}
shared secret s = A^b = 1672979704285245405540501819961909904698007377736076490271366396267786065674680629188219127597989604881283666046967412573262658391763801441018328185357500633854947639554905447923643380791821492760682950904361155289193535247290914356789403714288754218578607745054242775937105828896065533337976946907332080466764135754930965614040223373214902915323532760846659185976036119820093468471698545466453870973827806711857530568297666285659986195401914621622457371808306877
PLAINTEXT: crypto{n07_3ph3m3r4l_3n0u6h}
```

`submit_flag.py dh_static "crypto{n07_3ph3m3r4l_3n0u6h}"`:
```json
{"submitted": "crypto{n07_3ph3m3r4l_3n0u6h}", "submit": {"ok": true, "status": 200, "body": "Flag submitted. Press back to return to the challenge. Please enable JavaScript for a better experience"}, "before": {"score": 8035, "solved": 168}, "after": {"score": 8135, "solved": 169}, "score_delta": 100}
```

## Verification

- B_static equality asserted in-script against 6 prior live observations.
- Decryption produced clean ASCII flag with valid PKCS7 padding (a wrong key
  gives ~zero chance of this).
- Independent earlier run (probe `attack_13373.py` logic) recovered a
  different-connection flag `crypto{n07_3ph3m3r4l_3n0u6h}` too — the flag
  string is constant per challenge, ciphertext fresh.
- `score_delta: 100` from the user API — ground truth.

## Lessons

- **Read what the server ECHOES back.** Phase 2's "B" is `g^b` with MY g —
  a "raise-to-b oracle" on the generator, not just on my public value. Setting
  `g = A` makes Bob compute and return the intercepted shared secret.
- **Static DH keys turn an eavesdropped conversation into a derivable secret**:
  the attacker runs a follow-up session that reproduces the original
  `A^b`. (Textbook static-key DH attack.)
- Safe-prime structure (P−1 = 2q, q huge prime) kills small-subgroup lifting —
  verify the group structure before committing to an attack family.
- "Bored generating random numbers" = the key is static (not small): BSGS to
  2^46 confirmed b is not a small constant; don't burn time guessing.
- A fixed ciphertext-size mismatch (phase-2 message = 80 bytes, flag = 48
  bytes) told me the flag lives in phase 1, not phase 2.

## What I did / did not do

- Probed protocol with 4 minimal connections; ran one BSGS offline (b < 2^46).
- Did not hammer the server; each attempt was one clean connection.
- Did not consult any writeup; the attack emerged from protocol analysis.

## Limitations

None. Flag submitted and API-verified (score_delta > 0).

## Configuration

- Date: 2026-10-15 (UTC); host: Windows 11, git-bash; user OWNER.
- Interpreter: `~/tools/crypto-ctf/venv/Scripts/python.exe`
  (PyCryptodome, sympy).
- Working dir: `~\Practice_runs\cryptohack_org\challenge-127-cryptohack-dh_static`.
- Network: `socket.cryptohack.org:13373` (~8 connections total), cryptohack.org
  (submit/API).
- Evidence: `solve.py`, `explore_A1.py` (A=1 probe), `bsgs_b.log`,
  `live_transcript_2026-10-15.txt`, `flag.txt`.
