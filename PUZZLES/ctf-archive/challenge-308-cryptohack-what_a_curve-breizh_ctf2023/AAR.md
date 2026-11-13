# AAR — What a Curve! (Breizh CTF 2023, CryptoHack archive)

Status: **SOLVED** (live API solved-list confirms; submit `ok:true` HTTP 200, solved 290→291, archive points 0).
Flag: `[flag — recorded in FLAGS/ctf-archive/challenge-308-cryptohack-what_a_curve-breizh_ctf2023/flag.txt]` (derived twice independently on two connections; never copied from any external source).

Note: the parent brief pointed at "challenge-277 … what_a_curve-ut_ctf" with rank16.py pre-work — that does not exist here. Folder 277 is `offtopic-ecsc_2024_italy2024` (a different, already-solved challenge); `what_a_curve` lives in folder **308**, slug `what_a_curve-breizh_ctf2023` (verified in progress.json). No EC-over-Q / rank-16 work is relevant to this challenge.

## The challenge (server = chall.sage, genus-7 hyperelliptic RNG)
- p = 17585255163044402023 (~2^60.66, 64-bit), f ← random deg-15 poly **fresh per connection** (fresh process), C: y² = f(x), J = Jacobian.
- `RNG(seed)`: mul = seed (or random in [2024,p)); P ← random point class; each `__call__` packs Mumford coefficients u0..u6,v0..v6 of `[mul^k]P` as 14 little-endian uint64 = 112-byte blocks.
- Server prints `hex(RNG(2023) XOR (flag + " This is your final boss, enjoy it while you still can:))` — **flag is 56 B, suffix is 56 B, message = exactly one 112-byte keystream block** = coefficients of D₁ = [2023]P₀.
- Oracle loop: any hex → XOR-encrypt under a FRESH `RNG()` (random mul ≥ 2024, random point). Red herring for the keystream, gold mine for the curve.

## The break (2 ideas, zero ECDLP)
1. **Recover f from the oracle.** Every fresh-instance oracle reply (zeros as plaintext) is a *reduced* Mumford pair (u,v) on the SAME curve f for this connection: `f ≡ v² (mod u)`. Each reply contributes 7 linear equations on f's 16 coefficients → 3 replies determine f (solve as a 21×16 linear system over F_p; 4th+ replies verify). polylib.crt in the folder is buggy — use the Gaussian-elimination recovery in `frecov.py`.
2. **Byte-aligned known plaintext.** The known 56-byte suffix covers keystream bytes 56..111 = **exactly v(D₁)**, while the 56 unknown flag bytes cover **exactly u(D₁)** (0..55). So v is known and `u | (f − v²)` — a fixed squarefree degree-15 polynomial. Factor f − v² over F_p (distinct-degree + Cantor–Zassenhaus; exponent (p^d−1)/2 for degree-d splitting), enumerate its monic degree-7 divisors (~1–21 in practice), pack each candidate u as 7 uint64, XOR with C[0:56], keep printable-ASCII survivors → unique flag (≈2^80 odds for a false survivor).

Key numbers (run 2): f from 3/3 zero-queries; factorization pattern {1⁷,3,6} → 21 candidate u → 1 printable. Run 1 (offline on captured session1.json): {1,2,2,2,3,5} → 7 candidates → 1 printable, same flag.

## Files
- `cantor2.py` — self-contained genus-7 Mumford/Cantor arithmetic (Sage-faithful port of Kohel's cantor_composition/reduction_simple found in jm97.py); smoke-tested vs small-curve group laws (2P/3P, 2-torsion, P+(-P)=0). Fixed infinite loop in pdivmod when remainder hits [0] with constant modulus.
- `frecov.py` — linear f-recovery (the correct replacement for broken polylib.crt).
- `attack.py` — factorization + degree-7 divisor enumeration + ASCII filter; `attack(C,f)` returns printable candidates.
- `solve_live.py` — full pipeline in one connection (capture C → recover f → decrypt → flag_candidate.bin/solved1.json).
- `probe1.py`, `session1.py/json`, `test1*.py`, `inspect*.py` — server-behavior probes + capture used for offline validation.

## Limitations / honest notes
- Attack requires the message (flag+suffix) to fit exactly one block (112 B) so the suffix lands on v and the flag on u. A longer flag (v-region partially masked by flag bytes) would break the alignment — untested fallback.
- If f − v² were non-squarefree (prob ≈ 1/p, didn't occur) `factor_monic` raises; a squarefree-decomposition fallback is not implemented.
- Candidate uniqueness rests on the printable-ASCII filter (7–21 candidates/conn); no structural filter enforcing "D₁ = [2023]·(a point)" was implemented — deemed unnecessary given 56 ASCII bytes and the identical flag on two independent connections.
- Parent brief's "rank-16 EC over Q" resume-state matched nothing on disk (rank16.py absent; folder 277 is a different challenge). Treated as stale metadata and re-derived everything from statement + live server.
- EdZ textbook reference used: von zur Gathen & Gerhard, Modern Computer Algebra (distinct-degree + equal-degree factorization); Mumford representation per standard hyperelliptic literature. No writeups consulted.

## Vulnerability (plain words)
A genus-7 hyperelliptic "RNG" streams the 14 Mumford coordinates of Jacobian points as keystream, XORed with (flag + fixed 56-byte suffix). There is no discrete log to break: the message fits EXACTLY one 112-byte block, and the known suffix covers keystream bytes 56..111 = precisely the v-coordinates of D₁ = [2023]P₀, while the unknown flag covers precisely the u-coordinates. Reduced Mumford pairs obey f ≡ v² (mod u), i.e. u divides f − v². The server's XOR oracle (fresh RNG per query, SAME curve for the whole connection) donates as many reduced (u,v) pairs as needed to recover f by linear algebra — after which the flag's u is just one of a handful of degree-7 divisors of the known polynomial f − v².

## How the answer follows
1. Three zero-plaintext oracle queries → each gives 7 linear equations f ≡ v² (mod u) on f's 16 coefficients → 21×16 [flag — recorded in FLAGS/post-quantum/challenge-168-cryptohack-lwe-intro/flag.txt] over F_p recovers f (p ≈ 2^60.66); 4th+ queries verify (frecov.py replaces the buggy polylib.crt).
2. Known suffix ⇒ v(D₁) known exactly → build f − v² and factor over F_p (distinct-degree + Cantor–Zassenhaus, exponent (p^d−1)/2 per degree).
3. Enumerate the monic degree-7 divisors (pattern {1⁷,3,6} → 21 candidates), pack each as 7 little-endian uint64, XOR with C[0:56], keep printable-ASCII survivors → one unique flag; independently reproduced on a second connection (offline capture gave the same flag from 7 candidates).

## Limitations / attempts that failed
- The break needs the exact 56+56-byte one-block alignment (suffix on v, flag on u); a longer message breaks the split — no fallback implemented or tested.
- Non-squarefree f − v² (prob ≈ 1/p, didn't occur) raises in factor_monic; squarefree-decomposition fallback not implemented.
- Candidate uniqueness rests on the ASCII filter + two-connection agreement; no structural test "D₁ = [2023]·(a point)" was implemented.
- Cantor arithmetic ported from Kohel's algorithms (found in folder's jm97.py) needed an infinite-loop fix in pdivmod (zero remainder with constant modulus); smoke-tested against small-curve group laws.
- Parent brief's "rank-16 EC over Q / folder 277" resume state matched nothing on disk (stale metadata — folder 277 is offtopic); everything re-derived from statement + live server.

## Sources
chall.sage + the live oracle only. References named by the original AAR: von zur Gathen & Gerhard, Modern Computer Algebra (distinct-degree + equal-degree factorization); Mumford representation from standard hyperelliptic literature. No third-party writeups consulted; flag derived twice independently and submitted ok:true.
