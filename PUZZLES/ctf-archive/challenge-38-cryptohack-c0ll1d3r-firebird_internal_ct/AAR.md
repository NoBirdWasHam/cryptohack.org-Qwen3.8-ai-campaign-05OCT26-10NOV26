# AAR — C0ll1d3r (Firebird Internal CTF), CryptoHack ctf-archive, archive.cryptohack.org:9391

## Status: SOLVED 2026-10-25
Flag: `[flag — recorded in FLAGS/ctf-archive/challenge-38-cryptohack-c0ll1d3r-firebird_internal_ct/flag.txt]`
Verification: server printed `Congrats! firebird{...}`; `submit_flag.py
c0ll1d3r-firebird_internal_ct` → ok:true, solved 246 → 247 (archive challenge worth 0
pts, score_delta 0 as expected). NOTE: the site slug is truncated to
`c0ll1d3r-firebird_internal_ct` (data-challenge attr), NOT `..._ctf`. Despite the name,
this is NOT an MD5 collision challenge — it is a discrete-log hash by Mystiz.

## The vuln (analysis)
`hash(m) = pow(g, int.from_bytes(b'SECUREHASH_'+m,'big'), p)` with fresh random 256-bit
`g` and 256-bit prime `p` per connection; 5 lowercase-only messages; win by sending
`m != b'pleasegivemetheflag'` with `hash(m) == hash(b'pleasegivemetheflag')`.

Two weaknesses:
1. **Public parameters are recoverable from 4 oracle lines.** For same-length messages the
   prefix contributes the same `2P*256^L` to every exponent, so any byte-level relation
   `x1+x2 = x3+x4` gives `g^{e1+e2} ≡ g^{e3+e4} (mod p)` and hence `p | h1*h2 - h3*h4`
   as integers (~2^512). Two independent relations — `e_l+e_n = 2·e_m` (108+110=2·109)
   and `e_l+e_o = e_n+e_m` (108+111=110+109) — give `gcd(D1,D2) = p` (cofactors
   independent). 4 queries: `l n m o`.
2. **Collision without discrete log.** Fermat: `g^{p-1} ≡ 1`, so any lowercase `X` with
   `int(b'SECUREHASH_'+X) ≡ M (mod p-1)` collides with the target. Writing `X`'s bytes as
   `109 + d_i`, `d_i ∈ [-12,13]`, this is a modular knapsack `Σ d_i 256^i ≡ T (mod p-1)`
   with small digits → CVP in `Λ = {v : Σ v_i 256^i ≡ 0 mod p-1}` (dim L≈60, det 2^256;
   solution density 26^L/(p-1) ≈ 2^26 at L=60).

Query budget: 4 (params) + 1 (collision) = 5. Exactly fits.

## Attempts log
- (local harness `server_local.py` runs the real chall.py logic on 127.0.0.1:19391)
- p-recovery verified: recovered p == true p (logged from harness) on 4/4 connections;
  gcd(D1,D2) = p x small cofactor (strip small primes until prime).
- g recovery: use exponent of 'o' (odd, coprime to p-1 in all trials); 'l','n' end in
  even bytes -> gcd(e,p-1)>=2, skip them.
- Lattice: `CVP.closest_vector` enumeration EXPLODES (ball of radius ~box-diagonal
  contains ~2^80 lattice points). What works: BKZ-40 + plain/randomized Babai
  (`CVP.babai`), L=62..66, digits d_i in [-12,13]. LLL-only Babai gets maxd 18-26
  (need <=13); BKZ-40 reaches <=13 most of the time at L=64.
- First local e2e runs "failed" only because the client read ONE line after the final
  message; the server sends the hash line and the Congrats line as two packets. Fixed
  by draining until flag/EOF. Offline check proved the sent X collided exactly
  (server-printed hash == target hash, verified against logged true g,p).
- LIVE attempt 1 (2026-10-25): p recovered (255 bits), L=64 BKZ-40+Babai collision
  accepted -> `Congrats! [flag — recorded in FLAGS/ctf-archive/challenge-38-cryptohack-c0ll1d3r-firebird_internal_ct/flag.txt]`.

## Learning points
- `CVP.closest_vector` enumeration EXPLODES here: the l2 ball of radius ~box-diagonal
  (12.5*sqrt(L)) holds ~2^80 lattice points while the cube holds 2^26-2^40. Ball-based
  CVP is the wrong tool; BKZ-40 + (randomized) Babai is right.
- Additive relations among exponents (equal sums) give p-divisible COMPUTABLE integers
  when exponents are too big for unreduced powers (the `h1^e2 - h2^e1` gcd trick is dead
  when a fixed prefix forces exponents >= 2^88).
- g recovery: pick a message whose exponent is coprime to p-1 (odd last byte); 'l','n'
  end in even bytes -> gcd(e,p-1)>=2.
- Site slugs can be truncated to 29 chars — trust the data-challenge attribute.

## Limitations
- Babai success is probabilistic per connection (most succeed at L=64; one local p
  needed all L fallbacks). Mitigated by reconnect-retry + L in {64,66,62,68,60,70}.
- First live attempt took ~10 min wall-clock (L^2 bigint ops per Babai randomization);
  optimized post-solve to single-basis-vector shifts (solve.py carries the fast version;
  the flag was won by the pre-optimization run).
- No third-party writeups consulted; method = standard BKZ/Babai CVP (fpylll 0.6.4).

## Files
solve.py (live solver), chall.py (server), statement.txt, server_local.py (harness),
test_{lattice2,precovery,inproc}.py, flag_c0ll1d3r-firebird_internal_ct.txt,
live_solve.log + local_solve*.log (evidence).

## Vulnerability (plain words)
Not an MD5 collision: hash(m) = pow(g, int.from_bytes(b'SECUREHASH_'+m,'big'), p) with fresh random 256-bit g and 256-bit prime p per connection, 5 lowercase-only messages. Two breaks: (1) the oracle leaks the PARAMETERS -- same-length messages share the prefix exponent 2P*256^L, so any byte relation x1+x2=x3+x4 gives p | h1*h2 - h3*h4 as a computable ~2^512 integer, and two independent relations gcd to p (g recovered via a message whose exponent is coprime to p-1); (2) no discrete log is needed to collide: Fermat gives g^(p-1) = 1, so any lowercase X with int(b'SECUREHASH_'+X) congruent to the target mod p-1 collides -- writing bytes as 109+d_i, d_i in [-12,13], that is a small-digit modular knapsack sum d_i*256^i = T (mod p-1), a CVP.

## How the answer follows
1. Four queries 'l n m o'; relations e_l+e_n = 2*e_m (108+110=2*109) and e_l+e_o = e_n+e_m (108+111=110+109) -> gcd(D1,D2) = p x small cofactor (strip small primes until prime); recovered p == true p on 4/4 harness connections. Query budget 4 params + 1 collision = 5, exact fit.
2. Lattice Lambda = {v : sum v_i*256^i = 0 mod p-1}, dim L=64 (fallbacks 62..70), det 2^256, solution density 26^L/(p-1) ~ 2^26 at L=60; BKZ-40 + plain/randomized Babai reaches max digit <=13 (LLL-only Babai stuck at 18-26).
3. LIVE 2026-10-25: p recovered (255 bits), L=64 collision accepted -> [flag — recorded in FLAGS/ctf-archive/challenge-38-cryptohack-c0ll1d3r-firebird_internal_ct/flag.txt]; submit ok:true, solved 246->247 (archive, 0 pts). Note the site slug truncates to c0ll1d3r-firebird_internal_ct.

## Limitations / attempts that failed
- CVP.closest_vector enumeration EXPLODES here: the l2 ball of radius ~box-diagonal (12.5*sqrt(L)) holds ~2^80 lattice points while the cube holds 2^26-2^40 -- ball-based CVP is the wrong tool; BKZ-40 + (randomized) Babai is right.
- First local e2e "failures" were client-side only: server sends the hash line and Congrats line as two packets; fixed by draining until flag/EOF; offline check proved the sent X collided exactly (server-printed hash == target hash, vs logged true g,p).
- g recovery: 'l','n' end in even bytes -> gcd(e,p-1)>=2, skip; use the odd-exponent message 'o'.
- Babai success is probabilistic per connection (one local p needed all L fallbacks); mitigated by reconnect-retry + L in {64,66,62,68,60,70}. First live attempt ~10 min wall-clock before the post-solve single-basis-vector-shift optimization.

## Sources
Provided chall.py + live listener + local harness running the real chall.py logic (server_local.py); own solve.py, test_lattice2.py, test_precovery.py, test_inproc.py + logs (live_solve.log, local_solve*.log). Method = standard BKZ/Babai CVP (fpylll 0.6.4); AAR states no third-party writeups consulted.
