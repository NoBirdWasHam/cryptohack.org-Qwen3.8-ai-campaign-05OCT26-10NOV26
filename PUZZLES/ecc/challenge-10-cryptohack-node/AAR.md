# AAR — 121-cryptohack-node: Elliptic Nodes (CryptoHack)

**Result:** SOLVED ✅ — flag `[flag — recorded in FLAGS/ecc/challenge-10-cryptohack-node/flag.txt]` (score_delta +150, ok:true, 2026-10-22)
**Account:** NoBirdWasHam · submitted via `submit_flag.py node`

## Source
- **Platform:** CryptoHack — https://cryptohack.org/challenges/ecc/ ("Elliptic Nodes", 150 pts, slug `node`)
- **Statement:** "I've included an extra layer of security by picking my own curve parameters a,b and keeping them secret." Files: `source.py`, `output.txt`.
- **NOT consulted:** `/solutions/`, `/solves/`, third-party writeups (no-cheat rule). No external references used; the singular-cubic group law was derived and verified numerically in-script.

## The vulnerability (two layers, both real)
1. **Secret parameters aren't secret.** `source.py` hides `a, b` (`from secrets import a, b`), but both `G` and `Q = dG` satisfy `y² = x³ + ax + b (mod p)`. Two points ⇒ two linear equations in `(a, b)` ⇒ solve:
   `a = (gy² − Qy² − gx³ + Qx³)·(gx − Qx)⁻¹ mod p`, `b = gy² − gx³ − a·gx mod p`.
2. **The chosen curve is singular.** With the recovered `a, b`: `4a³ + 27b² ≡ 0 (mod p)`, i.e. Δ = 0. `gcd(x³+ax+b, 3x²+a)` has common root `x₀ = −3b/(2a)` — a node. The "extra layer of security" is a nodal cubic whose nonsingular points form a group isomorphic to **F_p\*** (split node), so the ECDLP collapses to a DLP in F_p\* of order p−1.

## The attack
1. Recover `a, b` from G, Q (above). p is a 256-bit prime.
2. Confirm singularity: `f(x₀) = f′(x₀) = 0` at `x₀ = −3b/(2a)`; translate `X = x − x₀` to get `y² = X²(X + c)`, `c = 3x₀`.
3. `c` is a QR mod p ⇒ **split node**. Isomorphism φ: E_ns(F_p) → F_p\*, φ(P) = (t − s)/(t + s) where `t = y/(x − x₀)`, `s² = c`. Verified numerically: φ(kG) = φ(G)^k for k = 2, 3, 5 (script auto-falls back to the inverse convention if needed).
4. DLP: `g = φ(G)`, `h = φ(Q)`, `znlog(Mod(h,p), Mod(g,p), p−1)` in PARI/GP. `znorder(g) = p−1` (full order), so d is unique. p−1 factors as 2 · six ~2⁴² primes — Pohlig–Hellman-friendly, which is why the author could pick this p.
5. `d = 175707932493016342199601625200584496546434097133638117913010244817446203005`; check `d·G == Q` with the source's own double-and-add: **True**. `long_to_bytes(d)` = flag.

## Key numbers
- p = 4368590184733545720227961182704359358435747188309319510520316493183539079703
- recovered a = 64186688762130075872648727143532923412208390610536286437268423112
- recovered b = 32579945572763798990069104934898692239152360555014084068553395172709029894
- p−1 = 2 · 2561822865103 · 3310993114631 · 3782003969119 · 3877604210317 · 4112912710789 · 4269421018381

## Learning points
- Two distinct points on `y² = x³ + ax + b` always determine `(a, b)` — "secret curve parameters" with a published base point + public key provide **zero** security.
- Whenever you recover curve parameters, **check the discriminant first** (`4a³ + 27b² ≠ 0`). A singular curve silently still "works" with naive group-law code (the source's `assert check_point` passes — the node lies on the curve), but the group collapses to (F_p, ×) and DLP becomes easy.
- Split vs non-split node decides the target group: `c = 3x₀` QR ⇒ F_p\* (order p−1); non-QR ⇒ norm-1 subgroup of F_{p²} (order p+1). Here p−1 was smooth-ish by construction.
- PARI `znlog`/`znorder` need `Mod(x, p)` elements, not bare integers (bare ints error into a break loop).

## Limitations / honest notes
- A prior session left this challenge OPEN with a generated stub AAR and no notes; nothing was reused from it beyond the downloaded `source.py`/`output.txt`.
- First `znlog` invocation failed (bare ints → GP break loop → `AttributeError` on the output regex); fixed by wrapping args in `Mod` — no math was wrong.
- The φ homomorphism was validated empirically (k = 2, 3, 5) rather than proved in-script; the final `d·G == Q` check under the source's own group law is the real proof of correctness.
- Did not need SEA point counting or fpylll; no failed mathematical avenues beyond the znlog arg bug.

## Configuration (environment for this run)
- **Host OS:** Windows 11, shell = git-bash/MSYS · **User:** OWNER
- **Interpreter:** plain `python3` (sympy, gmpy2, PyCryptodome); PARI/GP `~\tools\gp64.exe` (2.17.4)
- **Submission:** `submit_flag.py node <flag>` (cookie + requests; correctness from score delta +150)

## Artifacts
- `solve.py` — full reproducible solve (recovers a,b; verifies singularity + homomorphism; PARI znlog; checks d·G=Q; writes flag)
- `recover_ab.py`, `check_singular.py`, `factor_pm1.gp`, `dl.gp` — step scripts
- `flag_node.txt` — the flag

## Vulnerability (plain words)
Two independent flaws stack. First, "secret" curve parameters are not secret: the published points G and Q = dG both satisfy y² = x³ + ax + b (mod p), which is two linear equations in (a, b) — solving recovers the curve exactly. Second, the recovered curve is singular: 4a³ + 27b² ≡ 0 (mod p), a nodal cubic. The nonsingular points of a nodal cubic form a group isomorphic to F_pˣ (split node), so the "ECDLP" is really a discrete log in F_pˣ — and the author chose p with p−1 smooth, so even that DLP is easy. The naive point-checking code never notices the singularity (the node lies on the curve), so the "extra layer of security" silently provides none.

## How the answer follows
1. Solve for the parameters from G, Q: a = (gy²−Qy²−gx³+Qx³)·(gx−Qx)⁻¹ mod p, b = gy²−gx³−a·gx mod p. Recovered a = 64186688762130075872648727143532923412208390610536286437268423112, b = 32579945572763798990069104934898692239152360555014084068553395172709029894 for p = 4368590184733545720227961182704359358435747188309319510520316493183539079703 (256-bit).
2. Confirm singularity: gcd(x³+ax+b, 3x²+a) has common root x₀ = −3b/(2a) (f(x₀)=f′(x₀)=0); translate X = x−x₀ ⇒ y² = X²(X+c), c = 3x₀.
3. c is a QR mod p ⇒ split node. The isomorphism φ(P) = (t−s)/(t+s), t = y/(x−x₀), s² = c, maps E_ns(F_p) → F_pˣ; validated numerically: φ(kG) = φ(G)^k for k = 2, 3, 5 (script auto-falls back to the inverse convention).
4. DLP: g = φ(G), h = φ(Q), `znlog(Mod(h,p), Mod(g,p), p−1)` in PARI/GP; znorder(g) = p−1 ⇒ d unique. p−1 = 2 · 2561822865103 · 3310993114631 · 3782003969119 · 3877604210317 · 4112912710789 · 4269421018381 (six ~2⁴² primes — Pohlig–Hellman-friendly by construction).
5. d = 175707932493016342199601625200584496546434097133638117913010244817446203005; re-checked d·G == Q with the source's own double-and-add → True; `long_to_bytes(d)` = `[flag — recorded in FLAGS/ecc/challenge-10-cryptohack-node/flag.txt]` (score_delta +150, ok:true).

## Limitations / attempts that failed
A prior session left this folder OPEN with a generated stub AAR — nothing reused from it beyond the downloaded source.py/output.txt. One tooling failure logged: first `znlog` call passed bare ints (GP break loop → AttributeError on the output regex); fixed by wrapping args in `Mod` — no math was wrong. The φ homomorphism was validated empirically (k = 2, 3, 5) rather than proved in-script; the authoritative proof is the final d·G == Q check under the source's own group law. No failed mathematical avenues beyond that (SEA point counting / fpylll never needed).

## Sources
Provided `source.py` + `output.txt` only. Per the original AAR: no external references used — the singular-cubic group law was derived and verified numerically in-script ("self-derived per logs"). `/solutions/`, `/solves/` and third-party writeups NOT consulted. PARI/GP gp64.exe 2.17.4 as a tool.
