# AAR — 116-cryptohack-exceptional: Exceptional Curves (CryptoHack)

**Result:** SOLVED — submitted, API-verified (`score_delta +100`, 9375→9475, 183 solved).
**Date:** 2026-10-20 (UTC). Offline (`source.sage` + `output.txt`).

## Source
- **Platform:** CryptoHack — "Exceptional Curves" (slug `exceptional`, 100 pts)
- **NOT consulted:** solutions page / writeups (no-cheat rule)

## The flag
Recorded in `FLAGS/ecc/challenge-8-cryptohack-exceptional/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## Problem
- 512-bit Weierstrass E/F_p, `assert is_prime(E.order())` ("protected against Pohlig–Hellman").
- ECDH: prints G, A = nA·G; flag AES-CBC under sha1(str(x(nA·B)))[:16].

## How it was solved
1. `is_prime(order)` passes for ANY prime order — including the **anomalous** case.
   gp64 `ellcard` (SEA, ~1 min at 512 bits, 2 GB stack): **#E == p** → Smart's attack.
2. Smart/formal-group lift: E~ over Z/p², lift P~=(x, y+tp) with
   t = ((x³+ax+b − y²)/p)·(2y)⁻¹ mod p; λ(P) = t([p]P~)/p mod p where t = −x/y;
   n = λ(A)·λ(G)⁻¹ mod p. Pure-python Jacobian coords over Z/p² (no inversions).
3. Validated the whole λ pipeline **20/20 on a small anomalous curve first**
   (p=1039, a=2, b=5 — found by gp scan; classic p=751 example is NOT anomalous).
4. nA recovered, verified nA·G == A, S = nA·B, AES-CBC → flag.

## Bugs found (documented)
- **Jacobian doubling Z3 = 2YZ, not 4YZ** (X3 = M²−8XY² needs Z3²=4Y²Z²). Caught by
  cross-checking Jacobian mul vs affine mul mod p at n=2,3,5,17 — always do this.
- gp one-liners: `forprime(p=A,B,…)` takes bounds, not a vector; multi-line loops from
  stdin can hit "unexpected end of file" — write single-line or a .gp file.

## Learning points
- **`assert is_prime(order)` ≠ safe.** Prime order kills Pohlig–Hellman but not:
  anomalous (#E=p → Smart), supersingular (MOV), or trace-2 (#E=(p+1)²-ish) cases.
  ALWAYS compute #E and compare to p, p+1, and factor it — "prime" is one check of many.
- Smart's attack is O(1) group laws over Z/p² — trivially cheap even at 512 bits.
- Validate exotic attacks on a tiny instance found by brute-force scan before pointing
  them at 512-bit targets (the p=751 "textbook" anomalous example is wrong — scan your own).

## What I did / did not do
- Pure offline; no writeups consulted.

## Limitations
- None material; flag verified by submission (+100).

## Configuration (environment for this run)
- **Date:** 2026-10-20 ~16:10 UTC · **Host OS:** Windows 11, git-bash/MSYS · **User:** OWNER
- **Interpreter:** venv `~\tools\crypto-ctf\venv\Scripts\python.exe`; PARI/GP `~\tools\gp64.exe`
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-116-cryptohack-exceptional`
- **Agent:** Hermes Agent (desktop, qwen3.8-flash-next-unsloth-ud-q4_k_xl @ qwen3-8-flash)
- **Artifacts:** `source.sage`/`output.txt` (provided), `smart_test.py` (validated Smart lib),
  `solve.py` (working), `card.gp`/`anom.gp` (#E==p proof; small anomalous scan)
