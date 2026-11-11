# AAR — Too Many Errors (toomany, 100 pts, post-quantum)

## Result
SOLVED 2026-10-17. Flag: `crypto{f4ult_4ttack5_0n_lw3}`
Submit JSON: `{"submitted": "crypto{f4ult_4ttack5_0n_lw3}", "submit": {"ok": true, "status": 200, ...}, "before": {"score": 8265, "solved": 171}, "after": {"score": 8365, "solved": 172}, "score_delta": 100}`

## Attack
The server (13390.py) is an LWE sample generator over Z_127: each `get_sample` draws
`a` (28 values) from `self.rand = random.Random(SEED)`, draws `e = self.rand.randint(-1,1)`,
then **reseeds `self.rand` with a fresh `getrandbits(32)`**, and with probability 1/2 overwrites
one random coordinate of `a`. `b = <a, FLAG> + e (mod 127)`.

The "fault" is not where the weakness is. The weakness is the `reset` option:
`reset` does `self.rand.seed(SEED)` — the **same** fixed seed. So after every reset, the
deterministic prefix of the PRNG stream (the 28 `a` draws **and** the `e` draw) is
**identical on every connection**. Only the post-reseed corruption is random.

Consequences:
- All clean samples (no corruption) return the **same** `a_clean` and the **same** `b_clean`
  (e is a fixed constant, never varying).
- A corrupted sample differs from `a_clean` in exactly one coordinate j (value v), and
  `b = b_clean + (v - a_j) * FLAG_j (mod 127)` — **exactly**, no error term, because e is the
  same constant in every sample.

So one corrupted sample per coordinate suffices: `FLAG_j = (b - b_clean) * inv(v - a_j) mod 127`
(127 is prime; invertible unless v == a_j). Two-or-more samples per coordinate give pairwise
solves `(b1-b2)*inv(v1-v2)` as a cross-check (all pairs agree exactly).

Recovery: 147 clean samples (all b=45), 153 corrupted samples covering all 28 coordinates
(5 and 26 had exactly one sample each — handled by the single-sample formula). All 8 known
positions (`crypto{...}`) recovered correctly — including j=5 via the single-sample fallback —
which validated the deterministic-e hypothesis before trusting the unknowns.

## Verification
- Commands:
  - `~/tools/crypto-ctf/venv/Scripts/python.exe collect2.py` (subagent, 300 samples -> samples.jsonl)
  - `~/tools/crypto-ctf/venv/Scripts/python.exe solve_final.py`
- Output (abridged):
  - `clean a count: 147 of 300`, `b_clean values: Counter({45: 147})`
  - `corrupted samples grouped: 153 unparseable: 0 coords hit: [0..27]`
  - `known-position sanity: PASS` (j=0 c=99, j=1 r=114, j=2 y=121, j=3 p=112, j=4 t=116, j=5 o=111, j=6 {=123, j=27 }=125)
  - `FLAG: crypto{f4ult_4ttack5_0n_lw3}`
  - `verification: 300/300 samples consistent with e in {-1,0,1}`
- Independent full-sample check: every one of the 300 collected samples satisfies
  `b == <a, FLAG> + e (mod 127)` for some `e in {-1,0,1}`.
- Server-accepted: `score_delta: 100`.

## Lessons
1. Read the *whole* server source before assuming the LWE equation is ever broken. Here the
   "faulty sample" still satisfies `b = <a, FLAG> + e` (corruption happens **before** b is
   computed); the real bug is the stateful RNG + a same-seed `reset`.
2. `reset` with a fixed seed turns an LWE sampler into a deterministic generator: identical
   (a, e) every time. One deterministic reference sample makes every corrupted sample a
   single unknown-byte equation with **zero** error.
3. Known-character positions (the `crypto{...}` frame) are free test vectors: recover them
   first, and only then trust the unknowns. Here the single-sample fallback was validated on
   j=5 ('o') before it was used on j=26.
4. The prior subagent's per-coordinate voting failed ("conflicts: 188, consistent: 0") because
   it collected samples **without** interleaving `reset` (so the a-vectors were independent
   random draws and the clean-reference trick was invisible) and modeled corrupted samples as
   violating the LWE equation (they don't).

## Evidence
- `samples.jsonl` — 300 raw samples (a, b)
- `collect2.py` / `collect3.py` — socket collectors (reset + get_sample)
- `solve_final.py` — recovery script (this AAR's attack)
- `13390.py` — provided server source
- `flag.txt` — exact submitted flag
