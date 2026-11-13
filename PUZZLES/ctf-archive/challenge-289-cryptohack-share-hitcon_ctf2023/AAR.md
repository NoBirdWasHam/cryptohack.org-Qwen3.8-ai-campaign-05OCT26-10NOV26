# AAR — share-hitcon_ctf2023 (CryptoHack ctf-archive) — SOLVED

**Flag:** `[flag — recorded in FLAGS/ctf-archive/challenge-289-cryptohack-share-hitcon_ctf2023/flag.txt]` — submitted & verified via
`submit_flag.py` (solved count 277 → 278, 0 pts archive challenge).

## The flaw (self-derived)
`server.py` builds the Shamir polynomial with
`getRandomRange(0, p-1)`, which in PyCryptodome yields **[0, p-2]** — the
random coefficients a_1..a_{n-1} are **never ≡ p-1 mod p**. An off-by-one in
the RNG range leaks ~1/p of a bit per coefficient per round.

Attack: choose p (prime, 17..257) and n = p-1 → server returns f(1..p-2).
For each candidate r = f(0)= s mod p, the degree p-2 interpolant of
{(0,r),(1,y1),...,(p-2,y_{p-2})} is f = r·L0 + Σ y_j·L_j, so its coefficients
are **linear in r**: a_i(r) = r·L0_i + S_i. Wrong r survives a round iff
a_i(r) ≠ p-1 for all i, i.e. r ∉ K with kill-set
K = {(p-1-S_i)/L0_i : i=1..p-2}. (L_0 = (x^{p-1}-1)/(x+1)/c has all-nonzero
±1 coefficients, so K is well defined.) Each round kills each wrong
candidate with prob ≈ 1-1/p → ≈ ln(p)+margin rounds pin down s mod p;
intersect kill-sets across rounds, then CRT over ~290 bits of primes and submit.

## Performance notes (what killed the previous run)
- v1 (`solve.py`) ran a separate [flag — recorded in FLAGS/post-quantum/challenge-168-cryptohack-lwe-intro/flag.txt] per candidate: O(p⁴) —
  unusable. v2 (`solve2.py`): one Lagrange basis per prime (O(p²) precomp),
  O(p²) kill-set per round. Selftest: 662 rounds → full 256-bit secret
  recovered in **5.7s** in-process.
- **`signal.alarm(30)` = 30s total wall time per connection** (set once, not
  per loop). Send inputs per-prime in sync with reads; an unsent-then-drained
  input backlog pushed the secret compare to ~30s.
- **Protocol trap:** the server reads `p` **and** `n` before validating, so
  the exit sequence must be `4\n4\n<secret>\n` — a single `4\n` swallows the
  secret line as `n` and the final `input()` dies on EOF. This caused two
  "wrong secret" red herrings while the math was already correct.
- Wrong-residue detector: use ≈290 bits of primes (M ≈ 2^290); a bad residue
  puts the CRT result ≥ 2^256 with prob 1-2^-34 → reconnect instead of
  burning the session. margin=10 → per-attempt failure ≈ 55·e^-10.
- Windows: `python` (3.14) has no PyCryptoDome; use `python3` (3.10, Crypto
  3.24). Killed stray listener via `Stop-Process` (port 12801 verified clear).

## Live run evidence
- Probe: banner-less `p = n = ` prompt; p=17,n=16 → 15 shares (matches replica).
- Final attempt: 296 bits at t=28.2s → `secret =` → `[flag — recorded in FLAGS/ctf-archive/challenge-289-cryptohack-share-hitcon_ctf2023/flag.txt]`
  (`_live4.log`). Attempt logs: `_live2.log`, `_live3.log`.

## Files
- `solve2.py` — fast solver (selftest + live modes; `python3 solve2.py selftest` / `... live <host> <port>`).
- `_live2.log`, `_live3.log`, `_live4.log` — live run logs (4 has the flag line).
- `solve.py` (v1, kept, superseded), `_local_server.py`, `_server_local.py`, `_local.log` — prior state, untouched.

## Vulnerability (plain words)
The server builds its Shamir polynomial with PyCryptodome's `getRandomRange(0, p-1)`, which actually draws from **[0, p-2]** — so a random coefficient a_1..a_{n-1} can *never* equal p−1 mod p. Every share set therefore carries a tiny fingerprint (~1/p per coefficient). Ask many small primes for it, and a negligible range bug accumulates into the 256-bit secret.

## How the answer follows
1. Per connection choose a small prime p (17..257) and n = p−1 → the server returns f(1..p−2).
2. For each candidate r = f(0) = s mod p: the degree-(p−2) interpolant of {(0,r),(1,y1),…} has coefficients linear in r, a_i(r) = r·L0_i + S_i. A wrong r survives iff no coefficient hits p−1, i.e. r avoids the explicit kill-set K = {(p−1−S_i)/L0_i} (L0 has all-nonzero ±1 coefficients, so K is well defined).
3. Each round kills each wrong r with probability ≈ 1−1/p, so ≈ ln(p)+margin rounds per prime; intersect kill-sets across rounds → s mod p. CRT over ~290 bits of primes: a wrong residue lands ≥ 2^256 with prob 1−2^−34 → reconnect instead of burning the session; margin=10 → per-attempt failure ≈ 55·e^−10.
4. Fast implementation (solve2.py): one Lagrange basis per prime (O(p²) precomp, O(p²) kill-set per round) → selftest recovers a full 256-bit secret in 5.7 s in-process; live reached `secret =` at t = 28.2 s (296 bits), inside the one-shot 30 s alarm → flag.

## Limitations / attempts that failed
- v1 (solve.py): [flag — recorded in FLAGS/post-quantum/challenge-168-cryptohack-lwe-intro/flag.txt] per candidate — O(p⁴), unusable.
- Two "wrong secret" red herrings were pure protocol traps while the math was already right: (a) signal.alarm(30) is total wall time per connection, so input must be sent in sync with reads; (b) the server reads p *and* n before comparing, so exit must be `4\n4\n<secret>\n` — a single `4\n` swallows the secret line as n.
- Environment: Windows `python` (3.14) lacks PyCryptodome → use python3 3.10 (Crypto 3.24); a stray local listener needed Stop-Process.

## Sources
Provided server.py + live listener; the PyCryptodome getRandomRange off-by-one semantics were confirmed against the local replica. Flag came from the live service (`_live4.log`) after our own derivation. No external writeups or solutions pages consulted; Shamir interpolation/Lagrange algebra is textbook.
