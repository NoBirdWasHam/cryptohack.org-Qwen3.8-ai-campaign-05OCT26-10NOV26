# Course lesson — ProSign 3 (Elliptic Curves)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Elliptic Curves as challenge `ps3`.
**Status:** completed 2026-10-07 · **Points:** 100 · **Site:** https://cryptohack.org/challenges/ps3/
**Ledger row:** `course__prosign_3` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — ProSign 3 (ps3), CryptoHack Elliptic Curves course

**Status:** SOLVED + API-verified (count 82→83, score 3320→3420, 2026-10-07)
**Flag:** ``flag — recorded in FLAGS/ecc/course-ps3/flag.txt``
**No writeup consulted.** Vulnerability read directly from the challenge's own provided source.

## The bug

In the provided `source.py` the signing path does:

```python
now = time.localtime()
m, n = int(now.strftime("%m")), int(now.strftime("%S"))   # n REBOUND to seconds (0..59)
sig = self.privkey.sign(bytes_to_long(hsh), randrange(1, n))
```

The module-level curve order `n = curve192.order()` is **clobbered** by the `m, n = month, seconds`
unpack. So the ECDSA nonce is `k = randrange(1, n)` with `n` = the current **seconds** (0–59),
not the curve order. The nonce `k` is therefore drawn from `[1, seconds]` — a tiny nonce (≤ 58).

Two tells confirm it while probing:
- Connections at seconds 0/1 die with `ValueError: empty range in randrange()` (`randrange(1,0)`/`randrange(1,1)`).
- Signatures arrive fine at other seconds, but `k` is bounded by the second.

## Why small k is fatal

ECDSA: `s = k⁻¹ (z + r·d) mod n` (z = message hash, d = private key). Rearranged:

```
d = (s·k − z) · r⁻¹ mod n
```

With `k ∈ [1, S−1]` (S = seconds of the signed message), brute-force each `k`, compute candidate
`d`, form `Q = d·G`, and keep the `k` where `Q` **verifies the real signature** (the server's own
`verify` identity): `X = u1·G + u2·Q`, `u1 = z·w mod n`, `u2 = r·w mod n`, `w = s⁻¹ mod n`;
accept iff `X.x() % n == r`. Exactly one `k` verifies. That `d` is the true private key.

## Attack (solve.py)

1. Open socket 13381, send `sign_time`, read `(msg, r, s)`; parse `S` = seconds from `"Current time is MM:SS"`.
2. For `k in [1, S-1]`: `d = (s·k − z)·r⁻¹ mod n`; if `d·G` verifies `(r, s)` on `z` → key found.
3. Sign `"unlock"` manually with a fresh random nonce: `R = k2·G`, `r2 = R.x() % n`, `s2 = k2⁻¹(z2 + r2·d) mod n`.
4. Send `{"option":"verify","msg":"unlock","r":hex(r2),"s":hex(s2)}` → server returns the flag.

Live run (first try): `S=15`, recovered `k=4`, `d=2207347349610933765218396063101890730684612430616369489492`,
flag returned.

## Learning / takeaways (for the skill)

- **Variable shadowing is a real crypto bug.** Rebinding a symbol named after a curve parameter
  (here `n`, the group order) to something else (seconds) silently corrupts every later use — the
  nonce range, the verify bounds. When auditing signing code, grep for where the order/range
  variable is assigned, not just where it's used.
- **Tiny/non-random ECDSA nonce ⇒ private key.** `k` bounded by a small value (seconds, low counter,
  biased RNG) makes `d` brute-forceable in ≤ 58 iterations. Same root family as nonce-reuse.
- **The verify identity as an oracle.** You don't need the private key to *test* a candidate key —
  a candidate `Q` is confirmed iff it verifies the leaked signature. This is the same
  "recover/confirm public key from one signature" primitive used in many ECDSA challenges.
- **py-ecdsa API gotchas** (cost time this session): on `NIST192p`, `order`/`generator`/`curve` are
  **attributes**, not methods; point-at-infinity is `.x() is None`; `Point.mul_add` signature is
  `(self_mul, other, other_mul)` i.e. `self*self_mul + other*other_mul`; ECDSA verify uses
  `u2 = r·w` (NOT `s·w`).
- **ecdsa library rejects degenerate sigs** (`1 ≤ r,s < n` enforced), so the `r=n,s=0`
  "0=0" verification bypass does not work here — noted and ruled out empirically.

## Verification (no cheating)

- Flag returned by the **live server** over the socket (not guessed/leaked).
- Submitted via the logged-in flag form; API `/api/user/NoBirdWasHam/` shows "ProSign 3" in the
  solved list, count 83, score 3420.


## Limitations / attempts that failed
- Ruled out empirically: the r = n, s = 0 "0=0" verification bypass — py-ecdsa enforces 1 ≤ r,s < n
  and rejects the degenerate signature, so it cannot work here.
- py-ecdsa API gotchas cost time (attributes vs methods on NIST192p; `Point.mul_add` argument order;
  u2 = r·w in verify) — tooling friction, not attack failures. The key-recovery loop solved on the
  FIRST live run (S = 15, k = 4).
- Single-session evidence: flag came from one live server interaction; recovered d confirmed by the
  server's own verify on "unlock".

## Sources
Provided `source.py` (bug read directly from it: module-level curve order `n` clobbered by
`strftime("%S")` rebinding); live socket 13381; self-derived; no writeups consulted.

