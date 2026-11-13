# AAR — armory (Misc 100) — SOLVED 2026-10-20 (+100)
Flag: [flag — recorded in FLAGS/misc/challenge-186-cryptohack-armory/flag.txt]

Shamir "deterministic shares": coefs[i] = sha256(coefs[i-1]), coefs[0]=secret; poly=[s,c1,c2];
share_i = poly evaluated at x=c_i. The x-coords ARE the coefficient chain: c2=sha256(c1) known
from share.txt. One share solves s = y1 - (c2*x1 + c1)*x1 mod PRIME. "Need 3 shares" is false.
## Vulnerability (plain words)
The "deterministic-share" backup builds the Shamir polynomial by hashing: coefs = [s, c1, c2] with c1 = sha256(s), c2 = sha256(c1) — and it evaluates share i at x = c_i, so the *published x-coordinates in share.txt are exactly the polynomial's own coefficients* (c1 verbatim; c2 recomputable as sha256(c1)). The "you need 3 shares" claim assumes evaluation points are public randomness irrelevant to the polynomial; here every term except s itself is readable from one share line plus a hash.

## How the answer follows
1. Read x1 = c1 from share.txt (the x-coord IS c1) and compute c2 = sha256(c1) — both non-secret coefficients become public.
2. One share (x1, y1) then gives s directly: s = y1 - (c2*x1 + c1)*x1 (mod PRIME). No interpolation, no second or third share; the threshold is arithmetically false.
3. The recovered s passes the server check and returns flag `[flag — recorded in FLAGS/misc/challenge-186-cryptohack-armory/flag.txt]` (+100, 2026-10-20).

## Limitations / attempts that failed
- The run log is a one-paragraph AAR: no failed attempts are recorded in run logs.

## Sources
Challenge-provided files `share.txt` and server source `armory.py`. No third-party writeups consulted.
