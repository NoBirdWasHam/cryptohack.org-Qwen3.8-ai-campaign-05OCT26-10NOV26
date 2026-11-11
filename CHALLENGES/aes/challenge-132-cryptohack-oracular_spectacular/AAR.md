<!-- UPDATED by solver session 2026-10-24 (replaces backfill_docs.py stub) -->
# AAR — 132-cryptohack-oracular_spectacular: Oracular Spectacular (CryptoHack)

**Result:** SOLVED 2026-10-24 (first live attempt, 10 189/12 000 queries;
submitted via `submit_flag.py`, score_delta=+150, solved 231→232)
**Date:** 2026-10-24

## Source
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Challenge:** "Oracular Spectacular" (150 pts, slug `oracular_spectacular`), AES category
- **Server source:** `13423.py` (provided), listener `socket.cryptohack.org:13423`
- **NOT consulted:** `/solutions/`, third-party writeups (no-cheat rule). No external
  references used; strategy tuned via offline Monte-Carlo simulation only.

## The flag
`crypto{with_smart_enough_searching_you_can_learn_everything}`
(also in `flag_oracular_spectacular.txt`)

## The vulnerability / oracle model
- `message = urandom(16).hex()` → 32 ASCII hex chars = exactly 2 AES-CBC blocks,
  **encrypted without padding** (the real plaintext has no valid padding).
- `unpad` option: decrypts an attacker-chosen `iv||ct` and returns
  `{"result": good XOR (rng.random() > 0.4)}` — the oracle **lies with probability 0.6**
  (P(True|valid)=0.4, P(True|invalid)=0.6). Verified live: 200 known-invalid probes gave
  frac_true ≈ 0.635/0.535.
- Budget: 12 000 unpad queries per connection; `check` returns the flag iff the full
  32-char message is guessed (wrong guess just ends the session → reconnect).

## The attack
1. **CBC padding oracle, right-to-left, hex-charset shortcut.** To test byte `b` of a
   block, XOR the *previous* ciphertext block (c1 for block 2; the IV for block 1, sent
   as single-block `iv'||c1`) so bytes `b+1..15` decrypt to `p = 16-b`; then padding of
   length `p` is valid **iff byte b decrypts to p**. Because every plaintext byte is a
   hex char (`0-9a-f`, 16 values), only **16 candidate XOR values** exist per byte
   (vs 256) — this is what makes the 12k budget feasible. Cascade false positives are
   impossible: hex chars are ≥ 0x30 > 16, so no other padding length can match.
2. **Noisy candidate identification.** Each candidate is queried repeatedly; the answer
   is a coin correct only 40% of the time, i.e. an LLR (F−T) random walk with drift
   +0.2/query on the good candidate and −0.2/query on the 15 bad ones. Policy: greedy
   argmax-LLR, stop when top1−top2 ≥ G=24.
3. **Starvation tail + adaptive cap.** Greedy's failure mode is an unlucky early streak
   burying the good candidate; it self-corrects but needs many extra queries. Fixed caps
   (≤600) turned this into ~5%/byte errors (P(run success) ≈ 0.06–0.21). Fix: adaptive
   per-byte cap `min(1200, max(100, BUD − used − 100·remaining_bytes))` — early-finish
   bytes donate budget to starved bytes. Full-run Monte-Carlo (sim11):
   **P(success) ≈ 0.86 per connection**, mean ≈ 9.4k queries.
4. **No separate verification needed:** `check` is the verifier; a wrong message ends
   the session and we reconnect (fresh message per connection).
5. **Throughput:** both blocks recovered interleaved → 2 pipelined queries per
   round-trip (~40 ms/query amortized; ~8–10 min per connection).

## Key numbers
- Oracle truth rate 0.4 → per-query channel capacity ≈ 0.029 bits; 128 message bits
  need ≥ ~4.4k queries minimum; solver uses ~9.4k.
- G=24 gap → per-byte error ≈ 6.5e-4 on non-starved bytes; mean ~300 queries/byte.
- Sim Pareto: greedy ≫ Thompson/UCB/successive-halving/round-robin-warm; large
  adaptive cap ≫ fixed cap (P(success): 0.06 fixed-600 → 0.73 fixed-1000 → 0.86 adaptive).

## Learning points
- A lying oracle is just a noisy channel: repeat each test and let an LLR walk separate
  good from bad; the hex charset cuts candidates 256→16, which is the whole budget story.
- CBC padding-oracle byte control comes from XORing the **previous** block — XORing the
  block being decrypted scrambles it (avalanche). (Caught by local stub testing; the
  wrong variant showed frac_true≈0.6 for the *true* candidate.)
- `message` is the hex **string** itself — don't double-encode when calling `check`.
- Greedy best-arm policies have heavy tails under small gaps (0.4 vs 0.6); prefer
  adaptive budgets over fixed per-arm caps.
- The old `probe_flip_log.txt` (frac_true=1.0000) was a counting bug: it counted
  responses containing `"result"`, not `True` results. Live rate is 0.6 for invalid.

## Limitations (honest)
- Per-attempt failure ~14% by design (Monte-Carlo); remedy is reconnect+retry, not a
  better per-byte rule. One local attempt failed post-tuning, as expected.
- Strategy is Monte-Carlo-tuned, not provably optimal; the capacity bound leaves ~2.7x
  headroom for a smarter scheme.
- Live flip rate measured 0.535–0.635 over 400 probes — consistent with 0.6 within
  sampling noise; the strategy tolerates small deviations.

## Artifacts
- `solve.py` — the solver (LOCAL=1 runs against an in-process stub of 13423.py)
- `client.py` — JSON-line client with pipelined `unpad_batch`
- `sim2..sim11.py` (+ `sim*_out.txt`) — strategy Monte-Carlo sims; sim11 = chosen policy
- `probe3.py` — live flip-rate probe; `live_log.txt` — live run log
- `flag_oracular_spectacular.txt` — flag (only if actually obtained)

## Configuration (environment for this run)
- **Host OS:** Windows 11, shell = git-bash/MSYS; user OWNER
- **Interpreter:** python3 (sympy, gmpy2, PyCryptodome)
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-132-cryptohack-oracular_spectacular`
- **Submission:** `python3 submit_flag.py oracular_spectacular "<flag>"` from workspace
  root; correctness trusted only from API score_delta > 0.
- **Network:** socket.cryptohack.org:13423 (JSON-line protocol)

## Vulnerability (plain words)
The server picks a random 32-hex-char message (urandom(16).hex() — exactly 2 AES-CBC blocks encrypted **without padding**) and offers an `unpad` endpoint that decrypts any iv||ct you choose and reports whether the padding is valid — but it lies with probability 0.6. Since every plaintext byte is a hex char (only 16 possible values), a CBC padding oracle needs at most 16 candidate XORs per byte instead of 256; repeating each noisy test until a likelihood-ratio walk separates the true candidate fits inside the 12,000-query budget. The `check` endpoint then returns the flag once the whole message is guessed.

## How the answer follows
1. Oracle model from the provided source + live verification: P(True|valid)=0.4, P(True|invalid)=0.6 — 200 known-invalid probes gave frac_true ≈ 0.635/0.535.
2. Right-to-left CBC byte control by XORing the **previous** ciphertext block (c1 for block 2; the IV via single-block iv'||c1 for block 1) so bytes b+1..15 decrypt to 16−b; then padding length 16−b is valid iff byte b decrypts to 16−b. Hex alphabet ⇒ 16 candidates/byte; cascade false positives impossible because hex chars ≥ 0x30 > 16 can't masquerade as shorter paddings.
3. Noise handling: each candidate is a biased coin (0.4 vs 0.6); repeated queries form an LLR (F−T) random walk with drift ±0.2/query; policy = greedy argmax-LLR, stop when top1−top2 ≥ G=24 → per-byte error ≈ 6.5e-4 on non-starved bytes, ~300 queries/byte.
4. Starvation fix: adaptive per-byte cap min(1200, max(100, BUD − used − 100·remaining_bytes)) so early-finished bytes donate budget to starved ones; offline Monte-Carlo (sim11) gave P(success) ≈ 0.86/connection at mean ≈ 9.4k queries. Channel floor: capacity ≈ 0.029 bits/query ⇒ ≥ ~4.4k queries for 128 message bits.
5. Both blocks recovered interleaved (2 pipelined queries/round-trip, ~8–10 min/connection). First live attempt succeeded at 10,189/12,000 queries; `check` returned `crypto{with_smart_enough_searching_you_can_learn_everything}` (score_delta +150).

## Limitations / attempts that failed
Carried from "Limitations (honest)" above: ~14% per-attempt failure by design (Monte-Carlo) — remedy is reconnect+retry; one local attempt failed post-tuning, as expected. XORing the *wrong* block for byte control (the block being decrypted) was caught by local stub testing — it showed frac_true≈0.6 even for the true candidate. An old `probe_flip_log.txt` reading of frac_true=1.0000 was a counting bug (counted "result" keys, not True values). Strategy is Monte-Carlo-tuned, not provably optimal (~2.7× headroom over the capacity bound); measured flip rates 0.535–0.635 consistent with 0.6.

## Sources
Provided server source `13423.py` + own live probes (probe3.py, live_log.txt) + own offline simulations sim2–sim11 (sim11 = chosen policy). Original AAR: no external references used; strategy tuned via offline Monte-Carlo only. No /solutions/ or writeups consulted.
