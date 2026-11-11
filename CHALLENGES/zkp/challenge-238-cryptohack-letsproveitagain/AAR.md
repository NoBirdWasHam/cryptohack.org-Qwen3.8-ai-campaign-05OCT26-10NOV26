# AAR — 238-cryptohack-letsproveitagain: Let's Prove It Again (CryptoHack, 175 pts)

**Result:** SOLVED — flag `crypto{CRT_1s_m4gic_for_cryptanalysis}` (score_delta +175, ok:true)
**Date:** 2026-10-22

## Source
- Platform: CryptoHack, zkp category, slug `letsproveitagain`, socket.cryptohack.org:13431
- Worked from statement + provided `13431.py` only. **NOT consulted:** /solutions/, third-party writeups (no-cheat rule).

## The vulnerability
Same Schnorr-over-flag setup as part 1 (`y = 2^FLAG mod p`, `r = (v - c·FLAG) mod (p-1)`), "fixed" by the intern in three ways that introduce a *better* flaw:
1. `v` is now drawn **once in `__init__` and reused in every proof** (previously re-randomized per proof).
2. `c = sha3_256(t^y^g^salt)` with `salt = R.randint(2, BITS)` — unknown to us, but only **~1023 possibilities** (2..1024).
3. `max_turns` cut 12 → 4.

The client-seed oracle from part 1 remains: `refresh` with our own seed makes two separate proofs use the **same prime p** (and the same fixed `v`).

## The attack
With `c·FLAG < p-1` and `v < p-1`, each proof satisfies `r = p-1 + v - c·FLAG` over the integers. Two proofs (a, b) sharing p and v:

    r_a - r_b = (c_b - c_a) · FLAG   ⇒   FLAG = (r_a - r_b) / (c_b - c_a)

No knowledge of `p` or `v` needed at all. Brute-force `salt_a, salt_b ∈ [2,1024]` (≈10^6 recomputations of `c = sha3_256(t^y^g^salt)`), keep the pair where the quotient is an integer that decodes to a valid flag.

Turn choreography (exactly 4 get_proofs, the max): `P1` (unlocks refresh) → `refresh(seed)` → `P2` (our p) → `P3` (burn, re-unlocks refresh) → `refresh(seed)` → `P4` (same p, same v). Sanity check `y_a == y_b` confirms the shared prime.

Flag decode as in part 1: 39 bytes = `"crypto{" + (middle31 XOR nonce) + "}"` with one inserted non-printable byte; un-XOR nonce, strip one byte, validate.

## Key numbers
- salt space: 1023; brute force ≈ 10^6 hash candidates; 4/4 turns used; c ≈ 2^256 (no squaring this time).

## Learning points
- Reusing the nonce `v` across two Schnorr-style proofs with the same group is fatal: the system becomes linear in `(v, FLAG)` and the secret falls out by subtraction — the classic nonce-reuse ⇒ key-recovery pattern (cf. ECDSA k-reuse), here baked into the design.
- A "hiding" salt drawn from a tiny range (`randint(2, 1024)`) is no protection: brute-force the salt, not the secret.
- When a turn budget blocks the obvious refresh pattern, burn a throwaway proof to reset the turn-state machine (`your_turn`).

## Limitations
- Solved on the first live attempt; no failed live approaches. Offline harness validated 3/3 before connecting. (The offline harness's FLAG-replacement string didn't match the placeholder, so locally it recovers the `????` placeholder — attack mechanics still fully exercised against the real server logic.)

## Files
- `solve.py` (offline `--local` harness + live mode), `flag_letsproveitagain.txt`, `13431.py`, `statement.txt`

## Configuration (environment for this run)
- Host: Windows 11, git-bash; venv `~\tools\crypto-ctf\venv\Scripts\python.exe` (PyCryptodome)
- Submission via `submit_flag.py <slug> <flag>`; correctness from API score delta (+175).

## Vulnerability (plain words)
The same Schnorr-over-flag server as part 1, "fixed" by the intern in three ways that introduce a better flaw: the commitment nonce v is drawn once in __init__ and REUSED in every proof; the hiding salt in c = sha3_256(t^y^g^salt) is drawn from randint(2, 1024) -- unknown but only ~1023 possibilities; turns cut 12 -> 4. The client-seed oracle from part 1 survives, so refresh can force two proofs onto the same prime p and the same v: two Schnorr-style responses with a shared nonce are linear in (v, FLAG), and subtracting cancels v completely -- no p or v knowledge needed.

## How the answer follows
1. Turn choreography inside the 4-turn budget: get_proof (unlocks refresh) -> refresh(seed) -> P2 -> get_proof (burn, re-unlocks refresh) -> refresh(seed) -> P4; y_a == y_b confirms the shared prime; c*FLAG < p-1 and v < p-1 make both responses exact over the integers.
2. Subtract: r_a - r_b = (c_b - c_a)*FLAG, so FLAG = (r_a - r_b)/(c_b - c_a). Brute-force salt_a, salt_b in [2,1024] (~10^6 recomputations of sha3_256(t^y^g^salt)); keep the pair where the quotient is an integer decoding to a valid flag (decode as part 1: nonce-XOR + one-byte strip + validate).
3. Flag crypto{CRT_1s_m4gic_for_cryptanalysis} credited on the FIRST live attempt (score_delta +175, ok:true); 4/4 turns used; salt space 1023; c ~ 2^256 (no squaring this time).

## Limitations / attempts that failed
- No failed live approaches (recorded as such); offline harness validated 3/3 before connecting. Recorded caveat: the offline harness's FLAG-replacement string didn't match the placeholder, so locally it recovers the '????' placeholder -- attack mechanics were still fully exercised against the real server logic.

## Sources
Statement + provided 13431.py only; own solve.py. The AAR names the ECDSA k-reuse pattern as a general analogy (not a writeup). No /solutions/ or third-party writeups consulted (no-cheat rule, stated in AAR).
