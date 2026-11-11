# AAR — OffTopic (ECSC 2024 Italy), CryptoHack ctf-archive

**Solved: yes.** Flag delivered by the live listener after 128/128 OT rounds;
submitted via submit_flag.py (`ok:true`, solved 273→274, score_delta 0 — archive
challenges are worth 0 pts by design).

## The challenge
Receiver-side OT built on ElGamal-over-EC (P-256): `from_pt(m) = (rG, rH + mG)`.
Server flow: WE supply the receiver "public key" `H` (only check: `H != G`),
then 128 rounds where we send an encryption of a choice bit, the server
homomorphically computes `res = m0*(1-C) + m1*C` (an encryption of `m_c`), and
we must return BOTH random digits m0, m1 ∈ [0,9] to stay alive.

## The vulnerability (malicious receiver, first principles from the source)
1. `H` is attacker-chosen. Send `H = O` (point at infinity, `(0,0)`).
   `assert H != G` passes, and pycryptodome's `EccPoint(0,0)` is the identity.
2. Every re-randomization term is `r*H` → with `H = O` all noise in the S
   component collapses to zero: `from_pt(m).S = mG`, `rand.S = 0`.
3. Our ciphertext needs no validity check either: pick `C.S = K·G` with `K = 10^9`
   (a "ciphertext" of unknown r, which the server never verifies).
   Then exactly: `res.S = (m0·(1−K) + m1·K)·G` — noise-free (the R component
   keeps its `rG` noise and is useless, but R is not needed).
4. On digits [0,9]² the map `(m0,m1) ↦ m0 + K·(m1−m0) mod q` is injective
   (`|K·(m1−m0)| ≤ 9K ≪ q`, distinct pairs give distinct integers). Recovery =
   a precomputed 100-entry table (100 EC scalings, done once).
So one round leaks BOTH messages: OT's 1-out-of-2 choice property is broken —
soundness relies on the receiver not controlling `H`, and on S-noise, neither of
which is enforced. (The statement's joke: with a fully-homomorphic scheme that
mangles re-randomization, "FHE ⇒ OT" loses the obliviousness/soundness.)

## Key numbers
- Curve: NIST P-256 (p, q as in the file); `K = 10^9`; `H = O = (0,0)`;
  `C = (G, K·G)`. Per-round work: O(1) dict lookup. 128 rounds ≈ seconds.

## Validation
- `sim_test.py`: drove the REAL `offtopic.round()` in-process with `H=O`,
  128/128 accepted (pycryptodome 3.24; zero-point mult returns (0,0), and the
  m0=m1=0 round prints S=(0,0) — handled).
- Live fingerprint (single raw session): banner, prompt strings, and res JSON
  format match the posted file exactly → attack transfers unchanged.
- Live run `run3.log`: rounds 0–127 all matched, flag printed by server.

## Flag provenance
Flag came ONLY from the live service (`FINAL:` line in run3.log) after our own
derivation. No solutions pages / writeups / description.yml consulted.

## Limitations / dead ends
- Local subprocess test harness (`solve.py --local`, `--local-sock`) died on
  Windows pipe/text-mode quirks (OSError errno 22 on flush; buffering). Abandoned
  in favor of the in-process sim — protocol math was the real risk, not plumbing.
- `solve.py`'s local path is kept for reference but `sim_test.py` + `solve_live.py`
  are the runnable artifacts.
- First live attempt crashed at round 1 JSON parsing: server prints the next
  round's prompt on the same line as the res JSON; fixed by extracting the
  `{...}` substring (live build otherwise byte-matched the file).

## Learning points
- Malicious receiver + identity public key: whenever a scheme's re-randomization
  or blinding term is `r·H` and `H` is receiver-supplied, test `H = O` FIRST —
  it is the canonical way to strip all additive noise in one move.
- "Encrypt a bit" servers that never validate that the ciphertext is a valid
  encryption let you feed any pair of points; only the component the server
  reads (here S) must be on the curve.
- Encoding two small unknowns in one group element: pick a base K > digit range
  so a single linear combination `m0 + K·(m1−m0)` is injective — a digit-CRT.

## Vulnerability (plain words)
The server performs receiver-side Oblivious Transfer over ElGamal-on-P-256 but lets *us* supply the receiver "public key" H (only check: H ≠ G) and never validates that our ciphertexts are valid encryptions. Pick H = the point at infinity O: every re-randomization noise term is r·H, so all S-component noise collapses to zero, and the server's homomorphic blend res = m0·(1−C) + m1·C arrives *noise-free*. One round then leaks BOTH of the server's digits — OT's 1-out-of-2 property relied exactly on the two things the server did not enforce (receiver can't control H; ciphertext validity).

## How the answer follows
1. Send H = O = (0,0) (pycryptodome's EccPoint identity); `assert H != G` passes.
2. Each round send C = (G, K·G) with K = 10^9 — an "encryption" of unknown r, never checked by the server.
3. Read res.S = (m0·(1−K) + m1·K)·G. On digits [0,9]² the map (m0,m1) ↦ m0 + K·(m1−m0) mod q is injective (|K·(m1−m0)| ≤ 9K ≪ q), so a 100-entry dict (precomputed once, 100 EC scalings) decodes both digits per round.
4. Echo both digits back (the liveness requirement), 128 rounds ≈ seconds → server prints the flag.
5. Validated by driving the REAL offtopic.round() in-process (128/128 accepted) and by a live fingerprint match (banner/prompts/res JSON byte-identical to the posted file) before running the live session.

## Limitations / attempts that failed
- Local subprocess harness (solve.py --local / --local-sock) died on Windows pipe/text-mode quirks (OSError errno 22, buffering) — replaced by the in-process sim; protocol math was the real risk, not plumbing.
- First live attempt crashed at round 1: server prints the next prompt on the same line as the res JSON; fixed by substring-extracting `{...}`. Attack math unchanged.

## Sources
Challenge-provided offtopic.py (server source, matches live) + the live listener only. Flag provenance: the live service's `FINAL:` line after our own derivation. No writeups, solutions pages, or description.yml consulted. pycryptodome 3.24 identity-point behavior verified empirically in the sim.
