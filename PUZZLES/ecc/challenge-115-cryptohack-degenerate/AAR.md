# AAR — 115-cryptohack-degenerate: Edwards Goes Degenerate (CryptoHack)

**Result:** SOLVED — submitted, API-verified (`score_delta +100`, 9275→9375, 182 solved).
**Date:** 2026-10-20 (UTC). Offline challenge (captured `output.txt` + `source.py`).

## Sources
- **Platform:** CryptoHack — "Edwards Goes Degenerate" (slug `degenerate`, 100 pts)
- **NOT consulted:** solutions page / writeups (no-cheat rule)

## The flag
Recorded in `FLAGS/ecc/challenge-115-cryptohack-degenerate/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## Problem
- "Twisted Edwards" −x²+y² = 1+dx²y², p ≈ 2^256, base point compressed (1, 11),
  two public keys (xbit, y), AES-CBC flag under sha1(str(shared_secret))[:16].
- Server `order` = 254-bit PRIME (red herring); real Edwards #E = 2·3²·5²·q₁·q₂·q₃
  (q₃ ≈ 2^152) — ECDLP on the curve would be hard.

## How it was solved
1. `recover_x(1, 11)` FAILS (xsqr non-residue) → returns 0 → base point is **(0, 11),
   NOT on the curve**. Public keys also decompress to x=0.
2. The Edwards addition law is closed on {(0,y)}:
   **(0,y₁)+(0,y₂) = (0, y₁y₂ mod p)** — the "curve" degenerates to the MULTIPLICATIVE
   GROUP F_p^* with generator y₀ = 11. (Same family as twisted_mind: the law evaluates
   wherever the formulas are defined.)
3. So y_a = 11^{n_a}, y_b = 11^{n_b} in F_p^*. **p−1 is smooth** (2 · ten ~2^25 primes —
   gp64 `factor` in seconds) → Pohlig–Hellman + BSGS per factor → n_a mod (p−1),
   verified 11^{n_a} == y_a.
4. shared_secret = y_b^{n_a} mod p; key = sha1(str(secret))[:16]; AES-CBC → flag.

## Bugs found (documented)
- **BSGS sign**: with table g^j and walk h·(g^m)^i, the exponent is **x = j − m·i**, not
  j + m·i. Caught by the per-prime projection assert (gq^xq == hq) — always assert it.
- gp64 `ellinit` needs the 2-slot short-Weierstrass form [A,B] (Montgomery → SW by
  x = X − A₂/3 first); 5/6-slot vectors error in this build.

## Learning points
- **Check that the base point is actually ON the curve.** A complete-looking addition law
  on off-curve points can hide a much weaker group (here: F_p^*, and p−1 was smooth).
- Edwards/Montgomery laws are rational functions — off-curve input evaluates a *different*
  group law (twist family / degenerate conic), never "fails loudly".
- A prime `order` handed to keygen means nothing if the real group is different.

## What I did / did not do
- Pure offline computation; no live service contact; no writeups consulted.

## Limitations
- None material; flag verified by submission (+100).

## Configuration (environment for this run)
- **Date:** 2026-10-20 ~15:40 UTC · **Host OS:** Windows 11, git-bash/MSYS · **User:** OWNER
- **Interpreter:** venv `~\tools\crypto-ctf\venv\Scripts\python.exe`; PARI/GP `~\tools\gp64.exe`
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-115-cryptohack-degenerate`
- **Agent:** Hermes Agent (desktop, qwen3.8-flash-next-unsloth-ud-q4_k_xl @ qwen3-8-flash)
- **Artifacts:** `source.py`/`output.txt` (provided), `ordcheck.py` (off-curve discovery),
  `solve.py` (working), `card2.gp`/`fac.gp`/`facp1.gp` (#E, #E factors, p−1 factors)
