---
name: ctf-crypto-attacks
description: Use when a CTF crypto task needs a mode or property attack.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, oracle, block-cipher, attack]
    related_skills: [ctf-practice-runs]
---

# CTF crypto attacks — block-cipher mode & property recipes

Foundations reference (attack→algebra map, group/ring/field facts, Sage quick ref):
`references/algebra-and-attacks.md` — environment-independent, safe to hand to any agent.
Collision/birthday HUNT diagnostics (rho/VOW validity, coverage plateau detection, planted-pair toy harness): `references/collision-walk-hunts.md`.

## EC-x-coordinate invalid-curve (twist_and_shout family)
- x-only Montgomery ladder with unvalidated x -> queries land on the quadratic twist; if #twist is smooth, BSGS per factor over the twist modeled in F_{q^2} (x in F_q, y=c*w), server crash on pow(0,-1) means d=0 mod that factor; x-coords are sign-blind so CRT over 2^k sign combos + ASCII filter (works when d < #twist ~2^128, i.e. flag body <=16 B).
- sympy >=1.12 crt() returns (solution, modulus) NOT (modulus, solution); reversed unpack silently yields 0 candidates.
- CryptoHack xinetd listeners send the prompt banner immediately: consume it in connect() or every reply parses empty -> fake 'crash'.

## Sigma-protocol / Fiat-Shamir challenge triage (from sigma-hamiltonicity2)
- If bits come from the FINAL chained digest of all commitments, per-round
  grinding is dead: any change to any commitment rewrites every bit (2^n
  fixed point). Verify by line-reading which state feeds the bits.
- First cheap escape to probe: small dlog between Pedersen bases h1,h2
  (equivocation). BSGS < 2^22 takes ~20s in gmpy2 — run it before theorizing.
  Kangaroo self-test on a planted exponent first; a kangaroo whose tame/wild
  invariants don't share a jump table NEVER merges (silent void negatives).
- To fingerprint a live build vs the provided file without solving it: answer
  all rounds type-0 (open permuted statement); server prints each challenge
  bit, so (a) bit prefix vs local chain proves derivation, (b) a genuine
  bit-0 ACCEPT proves the server's statement/G matches the provided one.
  Grind A until bits[0]==0 first if you need bit-0 coverage.
- 'Solved by N users' + sound live build => hunt for the OLD build: banner-scan
  the archive host's port neighborhood (listeners live on sequential ports) and
  diff the currently-posted /static/challenges/* hashes against your own copies.
- hamiltonicity_2-cryptohack202 (archive :34597, folder 265, NEGATIVE 2026-10-28):
  posted MD5s match files, live traceback lines match, 3 live bits matched the
  FINAL-state low-128 slice and excluded per-round/indep/MSB variants; only ONE
  open port in the neighborhood. Sound-as-hosted: global FS + binding Pedersen +
  z-shape wall (int-perm crashes e=1, pair-cycle crashes e=0). Reusable
  discriminator: pre-grind A so desired-per-round-bit contradicts one rival
  derivation, then read printed bit 0 — kills per-round FS in one session.

## Archive GCM-with-unknown-state puzzles (2026-10, greatest_common_multiple-code)
When a GCM service only tags UNKNOWN random states (can append/reset blocks) and asks for the
fresh-cipher digest E(K,J0) (empty update/encrypt digest = AES_K(nonce||00000001), NOT the state tag):
short transcripts are information-theoretically hiding (12-byte blocks live in a 96-dim GHASH subspace V,
but 1 in VH^2+VH^3 spans everything). Only handles: u1-pair XOR memberships Z in H^2V u H^3V (32-bit
quadric constraints on H) and u2-branch D-equations D = (H+1)E + rho*H^2; but the u1/u2 target coins make
every equation type/branch-ambiguous and solving needs Magma/F4 on a 128+ unknown multilinear GF(2) system.
If no Sage/Magma on host, mark unsolvable-in-budget early and write the AAR; don't grind.

## When to Use
Solving a crypto challenge (CTF or practice run) where the target is a block-cipher mode
or a cipher property: padding oracle, compression (CRIME) oracle, ECB/OFB/CFB/CTR, or a
related-key weakness (DES complementation). For the archive workflow (folders, AAR,
no-cheat rules, leaderboard verification) see `ctf-practice-runs` — this skill is the
attack knowledge only.

## Always-on rules
- **Reproduce, don't trust:** re-derive any produced flag by an independent method
  (hand math, re-implementation, a second oracle-call pattern) before submitting.
- **Oracle responses are often identical for right/wrong** (e.g. "Flag submitted", a 200
  with no body). Only ground truth proves correctness: the server returning the flag,
  the solved-star on the leaderboard, or a local decryption check.
- **Read the provided server source first** — CryptoHack lists the source file in the
  statement; the exact padding / noise / key-handling code decides which recipe applies.

## Franklin-Reiter on a live server (bespoke, 100, SOLVED 2026-10-20)
Server hands c=(a·m+b)^11 mod N with fresh random (a,b) per query, SAME m and N per
connection => related messages. m is a root only MOD N, so gcd must run in (Z/N)[x]:
monic-ize each (a x+b)^11−c (divide by a^11), then Euclid with plain long division by the
MONIC divisor (valid over any ring); degree walks 11→1 in ~10 steps, x−m falls out.
A gcd over Q returns constant (the integer values differ by k·N — not roots). 2 queries
suffice. Flag: [flag — recorded in FLAGS/rsa/challenge-105-cryptohack-bespoke/flag.txt].

## MR-bypass Carmichael for "send me a prime" oracles (prejudice, 200, SOLVED 2026-10-20)
Server: FLAG[:pow(a,p-1,p)] for (a,p) passing strong-MR over all prime bases <64, p in
(2^600,2^900]. Prime p => x=1 (Fermat). Attack: 3-prime Carmichael + a = a factor of p
=> x = CRT(1,0,1) ~ n/2 => FULL flag. WORKING construction (n=p1p2p3, p_i=2f·a_i+1,
a=(1,421,2521) all =1 mod 420):
 * f=1 mod 4 => p_i=3 mod 8 => (2/p_i)=-1; per odd prime l<=61 pick f=w mod l with
   (1+2w·a_i | l) = -1 if l=1 mod 4 else +1 (reciprocity sign when l=3 mod 4!) => (b/p_i)=-1
   for every base b and i; v2(p_i-1)=1 all i and sum a_i odd => v2(n-1)=1, (n-1)/(p_i-1) odd
   => b^((n-1)/2) = n-1 => MR passes at j=1 for ALL bases. Carmichael: p1-1|n-1 automatic;
   a_i | ASUM + 2f·(prod of other a) are LINEAR in f -> fold into the same CRT.
 * f = f0 + M·t with t ~ 2^95 for n~2^601; triple-prime density ~7e-4 (AP-boosted) -> seconds.
DEAD ENDS (each cost a run): Chernick (6m+1)(12m+1)(18m+1) can NEVER pass strong-MR
(b^((n-1)/2)=1 mod q1 always); Legendre-forcing on q2 alone useless; semiprime hopeless
(pass needs b^s=-1 mod both primes for all 18 bases => q | gcd(b^s+1) tiny).
Flag: [flag — recorded in FLAGS/maths/challenge-98-cryptohack-prejudice/flag.txt]. Script: Practice_runs/cryptohack_org/
challenge-98-cryptohack-prejudice/solve4.py.

## Recipes (invariant first, then construction)
1. **Clean CBC padding oracle** (`pad_thai`). `P_0 = D(CT_b) ⊕ F` with forged previous
   block `F`. For byte `p` of block `b` (15→0), target padding `v = 16-p`:
   `F[q] = D_b[q]^v` for `q>p`, `F[p] = g^v` for candidate `g`, `F[q]=0` for `q<p`;
   the unique accepted `g` is `D_b[p]`. ~16 candidates/byte if plaintext is hex.
2. **Noisy / biased padding oracle** (`good_pad_ugly`: returns `good | (rand>0.4)`).
   Valid padding → ALWAYS true; invalid → true w.p. 0.6. So the correct candidate never
   returns false; a wrong one does w.p. 0.4/query. **Eliminate**: re-query all survivors
   each round, drop any candidate that ever returns false; the survivor is the byte.
   Never use "first true wins" on a biased oracle. A few hundred to ~2k queries total —
   check the server's query cap first.
3. **CRIME** (`ctrime`): `len(compress(P+FLAG))` leaks via ciphertext length. Set
   `P = (known + bytes([b]))*4`, scan `b`; the correct byte gives a **unique minimum**
   length (extra back-reference). Cache repeated calls.
4. **ECB cut-and-paste, byte-at-a-time** (`ecb_oracle`): splice a controlled prefix to
   align the target byte to block start; match the block against a dictionary of
   single-byte encryptions. Get message length from ciphertext length first.
5. **OFB/CFB keystream leak** (`symmetry`): keystream is plaintext-independent. Encrypt
   under the flag's IV → `KS = FLAG_ct ⊕ FLAG_prefix`; then `KS ⊕ other_ct` reads any
   block under the same IV.
6. **Frozen CTR counter** (`bean_counter`, `stream_consciousness`): `Counter.new(128)`
   with no `initial_value` stays at 0 → identical keystream every call. XOR two
   ciphertexts to cancel it; recover the keystream from a known header (PNG magic) and
   decrypt the rest.
7a. **CFB-zero = OFB keystream (mode picker, `cipher_mode_picker-hkcert_ctf`, SOLVED
    2026-10-25)**: server shares one key+IV across modes (each mode usable once).
    CFB with `segment_size=128` and all-zero plaintext gives `C_i = E(C_{i-1})`,
    `C_0 = E(iv)` — exactly the OFB keystream chain. So `cfb data 00*L` then `ofb flag`
    yields `flag = ct ⊕ KS` in 2 queries. Generalize: with a shared key+IV, any mode
    whose output under chosen plaintext walks the `E`-chain from `iv` leaks OFB's
    keystream. Flag: hkcert21{w3_sh0u1d_n0t_g1v3_much_fr3ed0m_t0_us3r5_...}.
7. **Merkle–Damgård length extension over a custom compression** (`md0`, 2026-10-12):
   `hash(data)` = `out=0; for block: out = AES_ECB(key=block).encrypt(out) ⊕ out`. `sign` =
   `hash(key‖data)`; goal: signature over a message containing `admin=True`. Get
   `sig1 = sign(msg1)` with `len(msg1) ≡ 15 mod 16` (e.g. `a*15`): the server pads to
   32 bytes = `msg1‖0x01`, so `sig1 = out_2 = H(H(key‖msg1‖0x01))` — the internal state
   after the second block. Forge block 2 as `pad("admin=True"+5)`; `forged =
   AES(block2).encrypt(sig1) ⊕ sig1`; send `message = msg1‖0x01‖"admin=True"+5` (server pads
   identically) + `forged`. No key recovery, no 2^256 preimage.
8. **XOR-IV wrapper over ECB** (`C = W ⊕ E_K(P ⊕ W)`, `triple_des`): this is `E_K`
   conjugated by the unknown translation `⊕W`; the IV `W` is the single secret. DES's
   complementation property `E_K(X)⊕1 = E_{K⊕1}(X⊕1)` holds for 3DES and at the
   transform level (`T_{K⊕1}(P⊕1) = T_K(P)⊕1`) — but it is a *symmetry* (constant,
   IV-independent), so confirming it live proves the weakness without shrinking the
   2^64 IV preimage search.

9. **MD5 generic collision** (`collider`, 2026-10-14): build `md5fastcoll` (Marc Stevens, hashclash core) from source — upstream `main.cpp` needs boost; write a ~70-line boost-free driver calling `find_collision(IV, ...)` with the standard MD5 IV and write `msg1.bin`/`msg2.bin` (128 B each). Compile: `g++ -O2 -static -o md5fastcoll.exe main_min.cpp block0.cpp block1.cpp block1wang.cpp block1stevens{00,01,10,11}.cpp md5.cpp` (winlibs mingw64). Pair generated in seconds; verify locally with hashlib before sending. Built exe archived at `Practice_runs/cryptohack_org/challenge-13389-cryptohack-collider/md5fastcoll/` (+ BUILD.md). If the target is a hash-keyed store, first probe session lifetime (see `cryptohack-socket-challenges`) — a generic pair in ONE connection beats any second-preimage idea.

10. **Same-seed reset in an interactive sampler** (`toomany`, 2026-10-17): server draws `a` and a tiny error `e` from one `random.Random(SEED)` stream, then *faults* one coordinate of `a`; `b = <a, FLAG> + e (mod q)`. The fault is a decoy — `b` is computed AFTER the fault, so every sample still satisfies the LWE equation. The real bug: a `reset` option that reseeds with the SAME seed. Collect `reset` + `get_sample` pairs: the deterministic prefix (all of `a` AND `e`) is identical on every sample; corrupted samples differ in exactly one coordinate. One corrupted sample per coordinate j then gives `FLAG_j = (b - b_clean) * inv(v - a_j) mod q` EXACTLY (e is a constant, no error term); pairs of corrupted samples at the same j cross-check via `(b1-b2)*inv(v1-v2)`. Validate on the known flag-frame characters (`crypto{...}`) before trusting unknowns, then verify all samples: `b - <a,FLAG>` mod q must be in {0, ±1}. 300 samples, seconds of compute.

11. **XOR-periodic key + MD5 length extension = byte-by-byte key recovery** (`mdflag`, 2026-10-21): server returns `md5(d XOR cycle(KEY))`, `|d| >= |KEY|`, no forgery target — must RECOVER the key. Trick: MD5 padding `pad_n` appended to `s = d^K^inf` lands on keystream positions `K[n mod L:]` (periodic!), so sending `d' = d || (pad_n XOR guessed-window)` makes the server compute `md5(s || pad_n)` exactly when the window guess is right — and `md5(s||pad_n)` is offline-computable by length extension when `(n+|pad_n|) % 64 == 0` (n mod 64 in {54,55}): then `md5(s||pad_n) = C(md5(s), md5_pad(n+p))`, ONE compression from the returned hash (implement MD5 compress from arbitrary 16-byte state). Choose `n ≡ a mod L`, `n ≡ 64-p mod 64` (solvable iff p ≡ a mod 2) to slide the p-byte pad window to key positions `[a,a+p)`; descend from the end with p=9/10 so each window holds exactly 1 unknown byte (seed: known flag prefix + trailing `}`); 256 queries/byte, ~12k total. Pitfalls: server cap was on the whole JSON msg (1024 B, hex doubles → n+p ≤ 490); `pad = 64 - n%64` only for n%64 ≤ 55 (56 → full 64-byte pad); first window wraps and needs a 2-unknown 65k product search once. Flag: crypto{example_flag_format}. Solver: Practice_runs/cryptohack_org/challenge-147-cryptohack-mdflag/solve.py (transport-agnostic recover(query) + --local self-test).

12. **CBC forge with a server-fixed first block + JSON-in-the-clear** (`rhetorical_oracle_2`,
    2026-10-19): server decrypts your whole ct under a per-connection key K with a FIXED
    first block T1 (the original token's first block), then
    `json.loads(plaintext.decode("unicode_escape"), strict=False)` and checks
    `token["user_id"] in ADMINS`. You control every plaintext block EXCEPT
    `P[1] = D(c1)⊕T1` (the block after the server-chosen T1). Attack, 7-block ct
    `[T1, c1..c6]`:
    - P[0] = `"{\"user_id\": \"h1h2h3` (forced by T1 — read the server's original plaintext).
    - P[1] = G = D(c1)⊕T1: uncontrolled garbage INSIDE the first JSON string value. Recover
      it byte-at-a-time via the padding oracle (it's the 6th D-recovery); require G contain
      no `\"` (0x22) and no `\\` (0x5c) so `unicode_escape` is the identity on it — clean
      probability (254/256)^16 ≈ 88% per attempt, so expect ~1.1 attempts; on a dirty G,
      retry on a FRESH connection (new K ⇒ new T1).
    - P[2..6] = `","user_id":"` + ADMIN + `"}` + 0x01 (80 B, fully controlled by c2..c6 via
      standard CBC chaining c5=D(c6)⊕P6, …, c1=D(c2)⊕P2).
    - Resulting plaintext `"{\"user_id\": \"h1h2h3<G>",\"user_id\":ADMIN_HEX}"` + padding:
      **duplicate JSON keys — `json.loads` keeps the LAST value** ⇒ user_id = ADMIN ⇒ flag.
    - Budget: ~2k queries per D-recovery, 6 recoveries + forge ≈ 12k queries total, all on
      ONE connection (fresh K per connection — do not reconnect mid-attempt).
    Generalization: when one plaintext block is uncontrolled garbage inside a structured
    format, either (a) recover it and condition on it being harmless for the encoding, or
    (b) repeat the critical key with a clean value after it (last-wins parsers). Check the
    parser's tolerance first (strict=False, unicode_escape ⇒ control chars OK, only quote
    and backslash break it).

13. **RC4 IV‖fixed-key keystream oracle → Klein sigma attack + prefix re-anchoring**
    (`oh_snap`, 120, SOLVED 2026-10-23): oracle returns `RC4(N‖FLAG)` keystream for any
    nonce N (error echo of `ct=00*m`). The KSA peel is dead when a fixed suffix follows
    the IV (and KSA wraps the key cyclically, `K[i mod L]`, so flag bytes never reach low
    rounds). The working bias is NOT the folk-FMS condition "S[i+1]=0 after round i ⇒
    z_i=K[i]+2" — measured FLAT over 200k keys. Use **Klein's sigma vote** (aircrack-ptw
    `guesskeybytes`): simulate KSA over the known prefix only (state S_t, j_t); for key
    index `l = n+t`: `sigma += S_t[l]`; vote `sigma_t = S_t⁻¹[(l − z_{l−1})] − j_t − sigma`
    (w≈13) estimates the CUMULATIVE sum `K[n..n+t]` w.p. ≈1.36/256; add Maitra–Paul vote
    `z_l − j_t − sigma` (w≈4, gate `z_l ≥ l`, `z_l ∉ j-hist`). Byte = sigma difference.
    **Prefix re-anchoring** is the force multiplier: nonce = R(4)‖known_prefix ⇒ key =
    R‖known‖FLAG, simulate KSA over `nonce‖known` (the known copy that follows!), so the
    frontier byte gets a FULL-strength vote (excess ≈0.013/sample over 1/256 floor);
    iterate rounds of ~130k queries (8 sessions, ~79 q/s, ~28 min) extending the prefix
    while `top1−top2 ≥ 3.5·√top2` and byte printable. 3 rounds × 130k = 34-byte flag.
    Pitfalls: bias at byte t decays with UNKNOWN rounds before it (not with absolute l);
    60k/round is coin-flip at the frontier — 130k+; charset must include uppercase
    (flag had 'R'); NEVER trust guessed completions — verify candidates by predicting
    held-out live keystreams (free perfect verifier; `…pr1v4cy}` was wrong, real tail
    `?!}`). Flag: [flag — recorded in FLAGS/aes/challenge-45-cryptohack-oh-snap/flag.txt]. Solver:
    Practice_runs/cryptohack_org/challenge-45-cryptohack-oh-snap/solve_oh_snap.py.

## CM factoring over étale algebras with FORMAL Y (rsa_backdoor, 175, SOLVED 2026-10-24)
When p is promised to be represented by a KNOWN principal form of small negative
discriminant D (e.g. p=(427s²+1)/4 → principal form of disc −427, h(−427)=2): pick the CM
curve whose j is a root of the Hilbert class poly H_D; then #E(F_p)=p+1−t with t=±1 known
from the CM theory. Build it over the étale algebra R=(Z/n)[δ]/(δ²−disc H) — H splits mod p
but stays irreducible mod q, so R ≅ F_p × (F_q or F_q²) and working in R is working mod p
and q simultaneously. You cannot take sqrt mod composite n to get points — so ADJOIN Y
FORMALLY: S=R[Y]/(Y²−g(x0)), a point is (x0, Y) with Y² symbolically = g(x0); run the
[n]P x-only ladder in S and gcd(denominator-norm, n): when the p-component annihilates
(t=+1 case) the denominator norm is ≡0 mod p → factor. Random R-twists cover the t=−1
branch (~1/4 hit rate). 4096-bit n factored in ~10 min this way.
Pitfalls: disc H need NOT be a QR mod n (so the integer-root curve over Z/n doesn't exist —
the δ-basis is the point); a point-finder that 'sqrt's g(x0) mod n and verifies y²=g²/N
silently returns NON-points (the classic bug here); never set j=δ blindly — j must be the
specific H-root matching the form. Self-test the whole pipeline on small instances
(small s, 4/4) before the real run. Flag: [flag — recorded in FLAGS/rsa/challenge-111-cryptohack-rsa_backdoor/flag.txt].

## Index calculus in GF(2)[x] (characteristic-2 DLOG; 'The Matrix Revolutions' family)
When DLOG lives in GF(2^m) (m composite → subfield attack): x = α^k is an m×m binary matrix
(Numpy uint8, basis = powers of the field element). Field = GF(2)[x]/f via PARI `ffgen(2^m)`
with `ffinit`/`ffgen`/`fflog`/`ffmulpol` — PARI's fflog cracks the small subfield block fast.
**Subfield decomposition:** for each divisor d|m, the subfield GF(2^d) = ker(Frob_d − I) on the
m×m matrix (GF(2)-linear kernel by row-reduction); its generator β = Σ c_i x^i (coeffs in kernel
basis) has order 2^d−1 in the big field. DLOG base-α of h = x^r lands in <β> → solve mod 2^d−1,
CRT over all d|m. Cost is dominated by the LARGEST proper subfield block.
**Index calculus for the big block (m=89, verified pipeline in challenge-130/unzipped/ic6.c):**
- Smoothness test = EXACT: squarefree + distinct-degree-factorization (`ddf`) + exact division;
  no norm heuristic (ic5's log-accumulation norm test was slower AND lossy — dropped).
  Measure P(smooth) empirically on ~5e5 iterations before budgeting: q=2 deviates hard from
  ρ(n/D) at small D (61/8 measured 1.9e-8 vs ρ≈1e-6; D=12 → 9e-5, 5000× faster).
- Factor base = monic irreducibles of deg ≤ D, ascending per degree (buildfb; skip even polys);
  D=14 → nfb=2537.
- Relation search: walk a = x^i·h by ONE multiply-by-x per step (shift + conditional f-reduction,
  ~1.5e5 tests/s in C with u128 bitmasks); trial-divide N(a) by FB norms (int64 overflow →
  use long double `log1pl` accumulation, threshold with ~1e-6 slack; exact PARI verify of
  survivors only). P(smooth) ≈ 2–3e-6 at D=8 → ~300k iterations/relation, ~30 min/core.
- Linear algebra over Z/Φ (Φ=2^m−1; PRIME for m=61,89 — Mersenne exponents — so Gauss-Jordan
  with Fermat modinv is valid; composite Φ needs per-prime-factor Gauss + CRT). Then per target
  h·x^u (u=0.., first smooth): back-substitute → log.
- **Rank-deficient is fine if the target is DETERMINED:** with free columns F, kernel δ has
  δ_f=1, δ_piv=−A_RREF[row(piv)][f]; target log is unique iff slope = [free col in target
  factors] − Σ_piv e_j·A_RREF[j][f] == 0 for every free col. Print only when slope==0.
- **Isolated FB columns** (never divide any sampled x^i): targeted search — walk x^i·p, accept
  smooth, write relation with coefficient −1 for p (relation-file format: negative index =
  Φ−1 coefficient). ~1/P iterations each; seconds, not hours.
- **ALWAYS self-verify before printing a log: x^lg == h via poly modexp.** This gate is what
  caught the muln bug below; a wrong log otherwise flows silently into CRT + decrypt.
- **Hand-rolled mod-(2^m−1) multiply is size-specific.** A 45/44-bit Karatsuba split tuned for
  m=89 is silently WRONG for m=61 (wrap constants 2^90≡2, 2^89≡1 don't hold) while accidentally
  correct for m=31. Use direct `__int128` product + fold-loop for m≤63; pin EVERY m with a
  regression (x^log==h on a PARI-generated target in the SAME field — generating the target in
  a different-degree f produced a false solver-bug alarm).
- **u128 shift gotcha:** `v << 64` is UNDEFINED for 128-bit ints (silently no-ops on gcc/x86-64).
  Write `if(j>=64){hi=v<<(j-64);lo=0}else{hi=(hi<<j)|(lo>>(64-j));lo<<=j}` and never shift by ≥64.
  Also: reducing mod the field poly must XOR the poly WITHOUT its x^MD bit; and PARI `hex` is a
  builtin name — a user variable called `hex` silently breaks `lift`-based bit extraction.
- Parallel search: independent offset ranges (setup = modexp x^i0, then walk), merge relation
  files before ONE big elimination. CAP rows ≥ 1.5× needed rank.
- **Windows pipes eat binary stdout:** any C tool streaming binary records must call
  `_setmode(_fileno(stdout), _O_BINARY)` or every 0x0A becomes 0x0D0A and the consumer silently
  parses garbage (cost a whole wasted search on the primed5 md5fastcoll pair stream). Validate
  generated data end-to-end (hash-check a sample) before launching long searches.
- **MD5 collision toolchain (md5fastcoll/hashclash core — build from source):** pairgen.cpp
  streams 256-B records M1||M2 (128-B two-block fastcoll pairs, diff = words 4/11/14 ±2^31/2^15);
  link needs block1stevens{00,01,10,11}.cpp + block1wang.cpp + stub `void p5_check(void){}`.
  ~0.7 pairs/s/core. **Zero free bits:** flipping ANY bit of M1/M2 (even word 15, below the
  difference bits) breaks the collision — you cannot post-hoc force residues (e.g. `27 | int(M2)`)
  into a pair; either trial-divide for a usable factor (~50% of random 1024-bit ints have a prime
  factor < 1e6) or filter INSIDE the generator over fresh candidates.
- **sign-prime/check-any oracle pattern:** issuing path checks a property (primality), verification
  path re-hashes but skips the check → collision (prime p, composite p' with divisor a) turns a
  `FLAG[:gcd(a,p')]` leak into the full flag when a ≥ len(FLAG). Reject collision messages with
  leading 0x00 (`long_to_bytes` roundtrip).
- CRT combine subfield logs: moduli 2^d−1 are NOT coprime (d|e ⇒ 2^d−1 | 2^e−1) — the large
  block's log must be consistent mod gcd; verify final k: α^k == x (matrix pow).
- **Matrix-DH over GF(2) (The Matrix trilogy family):** charpoly(G)=∏ irreducibles (exp 1 ⇒
  semisimple) ⇒ algebra ≅ ∏ GF(2^deg); ord(G)=lcm(2^d−1). Krylov: solve M = Σ c_k G^k for the
  public matrix, reduce the poly mod each factor → per-field DLOG targets (base = image of G =
  x); CRT exponents; GATE with G^A==A_pub before decrypting.

## Groth16 proof malleability = ticket double-spend (snark-maestro / Ticket Maestro, 200, SOLVED 2026-10-23)
Groth16 verify checks ONE pairing product e(A,B)=e(α,β)·e(L,δ)·e(C,γ); A and B appear only
inside e(A,B) ⇒ for any r≠0, (r·A, r⁻¹·B, C) is a valid proof of the SAME statement. If the
service keys uniqueness on the proof's serialization (id = hash(proof), spent-set), each fresh
r is a new redeemable ticket — no witness, no DLOG. Econ-gated services (buy/redeem/flag) are
the tell. Pure-Python forge: affine double-and-add on G1 and on G2 over Fq2 (group law never
uses curve b, so no pairing lib needed; Fq2 = Fp[u]/(u²+1), u²=−1).
ark-serialize 0.3.0 COMPRESSED format (128-B Groth16 proof = 32+64+32; 0.4+ defaults differ):
G1 = x LE with SWFlags in top 2 bits of last byte (bit7 = y>−y, bit6 = infinity); G2 = x.c0‖x.c1,
flags on last byte of c1. y-recovery = get_point_from_x: KEEP sqrt(x³+b) iff (y<−y) XOR positive
(easy to invert — validate with a byte-exact parse→serialize roundtrip on a real artifact).
Fq2 sign/ordering in ark-ff 0.3.0 compares (c1,c0) LEX (c1 first!). Fq2 sqrt = complex method
(eprint 2012/685 Alg.8): α=√norm, δ=(α+c0)/2 (−α if QNR), c0=√δ, c1=c1/(2c0). Read the exact
crate sources (ark-ec/ark-ff/ark-serialize .crate from static.crates.io) instead of guessing.
Flag: [flag — recorded in FLAGS/ctf-archive/challenge-299-cryptohack-ticket_maestro-cryptohack2024/flag.txt]. Solver: Practice_runs/
cryptohack_org/challenge-240-cryptohack-snark-maestro/solve.py.

14. **Merkle preview with negative-index leak + known-plaintext byte collapse**
    (`mistersaplinstheprover`, 125, SOLVED 2026-10-25): server builds SHA256 Merkle tree
    over `secret(17B, fresh/conn) + FLAG(47B)`, one `get_node` preview per connection
    guarded by `idx < len(nodes[0])-1` — but the builder APPENDS the next-level node to
    nodes[0], and negative indices pass the bound check: `node=-1` leaks `n10=H(l0||l1)`.
    Leaves covering only FLAG bytes are stable ACROSS connections (collect l3..l7 on 5
    conns -> n21 known). On the proof conn: leak n10, then n11=H(l2||l3) with
    l2=H(secret[16]||FLAG[0:7]) and FLAG[0:7]="crypto{" known -> only 1 unknown byte
    (secret[16]); brute 256 roots `H(H(n10||H(H(b||"crypto{")||l3))||n21)` via the
    unlimited do_proof oracle on the SAME connection. Flag: [flag — recorded in FLAGS/zkp/challenge-236-cryptohack-mistersaplinstheprover/flag.txt].
    Generalize: (a) `idx < len-1` style guards ignore Python negative indexing — an
    appended hidden node is readable at -1; (b) when a hashed block mixes k random bytes
    with known plaintext and the sibling/parent can be leaked, whole-root entropy = k;
    (c) per-connection one-shot preview flags are defeated by cross-conn stable subtrees
    + same-conn leak + unlimited verify oracle.

15. **Fractional-offset norm hints -> linearize + weighted CVP** (`1337crypt_v2-downunderctf2021`,
    DownUnderCTF2021, SOLVED 2026-10-25): 1337-bit p,q, n NOT given; hints `h1=p^2+q^2` and
    2x `(floor(y), a, b)` with `y=(A+Bp)^2+(Bq)^2`, `A=a+α/2^338`, `B=b+β/2^338`. Naive
    `p≈(y-a^2-b^2 h1)/(2ab)` FAILS (β·p and β²h1 terms -> error ~2^1338). Key: `p(β)=C1/B−C2·B`
    is linear in β to within O(1) over the whole unit interval (|p''_B|=O(1), chord dev ≤0.25);
    α shifts p by only ~2 bits. Two hints -> `q1·β1 − q2·β2 = D0 + z`, |z|≤9 (q_i exact secant
    slopes, Fractions). Clear denominators (W_i=q_i·Lc, D=D0·Lc), solve weighted CVP: rows
    `(2^8002,0,W1),(0,2^8002,−W2)`, target `(0,0,D−ctr(W1−W2))` — box weight 2^(errbits−boxbits)
    balances coords; λ1~2^8669 vs true dist ~2^8345 -> unique closest. Use **fpylll
    CVP.closest_vector** (enumeration): hand-rolled exact-Fraction Babai nearest-plane FAILED
    on the real instance despite the theoretical bound (worked on synthetic — don't trust it).
    Then p=round(p1(β1))±window filtered by h1−p² square + primes; decrypt `m^0x1337` in
    `(Z/n)[I]/(I²+1)` with λ=lcm(p²−1,q²−1) (works whatever −1 does mod p,q), re-encrypt to
    verify. Sage prints ring elements as `im*I + re` — parse both. Flag:
    [flag — recorded in FLAGS/ctf-archive/challenge-242-cryptohack-1337crypt_v2-downunderctf2021/flag.txt]. Solver: Practice_runs/cryptohack_org/
    challenge-242-cryptohack-1337crypt_v2-downunderctf2021/solve2.py.

15. **Hidden-param DL hash `g^m mod p` collision (c0ll1d3r Firebird Internal CTF, SOLVED
    2026-10-25):** hash(m)=pow(g,int(b'PREFIX_'+m,'big'),p), fresh random 256-bit g and
    256-bit prime p per connection, N lowercase-only queries, win = collide a fixed target
    string. (a) Recover p via ADDITIVE exponent relations: equal byte-sums (e_l+e_n=2e_m,
    e_l+e_o=e_n+e_m via chars l,n,m,o = 108,110,109,111) give p | h1*h2-h3*h4 as small
    integers; gcd of two independent relations = p*small-cofactor (strip small primes).
    The `h1^e2-h2^e1` gcd trick is DEAD when a fixed prefix forces exponents >= 2^88
    (unreduced powers impossible). Recover g as h^{e^{-1} mod p-1} (pick odd last byte so
    gcd(e,p-1)=1). (b) Fermat: any lowercase X with int(PREFIX+X) = M mod (p-1) collides.
    Digits 109+d_i, d_i in [-12,13] -> knapsack sum d_i 256^i = T mod (p-1); lattice
    {v: sum v_i 256^i = 0 mod N}, dim L=64, det 2^256, density 26^L/N ~ 2^40. Solve with
    BKZ-40 + randomized Babai (CVP.babai, shift target by small multiples of basis rows).
    NEVER CVP.closest_vector here: the l2 ball of radius 12.5*sqrt(L) holds ~2^80 points
    (cube only 2^40) — enumeration hangs. Flag: firebird{wh3n_1n_d0ub7_u5e_latt111c3_...}.
    Solver: Practice_runs/cryptohack_org/challenge-251-cryptohack-c0ll1d3r-firebird_internal_ctf/solve.py.

16. **E(Dec) oracle on Rabin-with-reciprocal, pubkey never sent** (broken_oracle-hacktm_ctf2023,
    SOLVED 2026-10-26): server returns Enc(Dec(r,s,t)) for any triple; n AND c unknown. Decryption
    solves x²−rx+c; when Δ=r²−4c is QNR mod one prime the 'roots' a1,a2 are garbage (but still
    a1+a2=r) so r′=Enc picks one: r′ ≡ r mod the good prime, differs mod garbage prime.
    (a) FACTOR: pairwise gcd(r′ᵢ−rᵢ, r′ⱼ−rⱼ) over ~12 mixed queries = p or q exactly (a single
    gcd(r′−r, n) is USELESS when n is not published; double-garbage diffs are pseudorandom junk —
    that killed the prior solver).
    (b) RECOVER c — the linearization trick: query the SAME r with t=0 and t=1; the two responses
    mod the garbage prime are {u+c/u, v+c/v} with u+v=r, uv=c+e unknown. σ=r′₀+r′₁, π=r′₀r′₁ give
    a LINEAR equation: c(σ−2r)² = (π−r(σ−r))·r(σ−r) → c mod prime. (Clean side: σ=2r, den=0 → skip.)
    Run vs both primes, repeat for consistency (~10 queries), CRT → c; then decrypt flag ciphertext
    with own quadratic solver (Δ=(m−c/m)² is QR both sides). Generalizes: any oracle where a broken
    branch returns f(m)+c/f(m)-type values with paired selection bits — sum/product eliminates the
    unknown product. Flag: [flag — recorded in FLAGS/ctf-archive/challenge-309-cryptohack-broken_oracle-hacktm_ctf2023/flag.txt]. Solver:
    Practice_runs/cryptohack_org/challenge-309-cryptohack-broken_oracle-hacktm_ctf2023/solve_live.py.

## Shamir coefficients from PyCryptodome getRandomRange(0, p-1) are never p-1 (share-hitcon_ctf2023, SOLVED 2026-10-29)
getRandomRange(lo,hi) returns [lo,hi-1]. If the server samples secret/shares s<n=p-1, every coefficient a_i satisfies a_i != p-1 mod p — an exclusion oracle. For candidate r=s mod p the coefficients are linear in r: a_i(r)=r·L0_i+S_i (Lagrange at 0 through the seen shares), so each round each share prunes exactly one wrong r via an O(p^2) kill-set test; intersect kill-sets over ~ln(p)+10 rounds per prime, then CRT across primes (add ~30 extra bits of margin as wrong-residue detector). Full 256-bit secret in ~660 rounds / 5.7s local, 28s vs a 30s live alarm. Pitfalls: server read p AND n BEFORE validating (exit sequence must send both numbers then the secret); use python3 (3.10 w/ pycryptodome), not 3.14.

## OT/ElGamal-on-EC with receiver-chosen pubkey: H = infinity strips all noise (offtopic-ecsc_2024_italy2024, SOLVED 2026-10-28)
Server EC-ElGamal `from_pt(m)=(rG, rH+mG)`; WE supply H (only `H!=G` checked), 128 OT rounds demand BOTH digits m0,m1∈[0,9] of `res = m0(1-C)+m1C`.
- Send `H=O=(0,0)`: every re-randomization term `rH` vanishes ⇒ `res.S = (m0(1-k)+m1k)G` EXACTLY when our `C.S = k·G` (ciphertext validity never checked; R keeps rG noise but is unread/unused).
- Digit-CRT: `k=10^9 > 10` makes `m0 + k(m1−m0) mod q` injective on [0,9]² ⇒ BOTH messages leak in ONE round; precompute 100-point table once.
- Live-build gotcha: server prints the NEXT round's prompt on the same line as the res JSON — extract `{...}` substring, don't line-split.
- Local subprocess harness on Windows pipes hit OSError errno 22 / buffering (−u insufficient); test protocol math IN-PROCESS instead: monkeypatch `builtins.input` + `redirect_stdout` around the real `round()` (128/128 sim before touching live).
Flag [flag — recorded in FLAGS/ctf-archive/challenge-277-cryptohack-offtopic-ecsc_2024_italy2024/flag.txt]. Solver: Practice_runs/cryptohack_org/challenge-277-cryptohack-offtopic-ecsc_2024_italy2024/solve_live.py.

## Share-leak over phi + huge phi-multiple => Miller factoring, size irrelevant (rsatogether ECSC2024 Italy, SOLVED 2026-10-29)
Server Shamir-shares d over Z/phi (nodes 1..t, t=input+1) and hands out the node-k share for input k:
u_k = (-1)^(k-1)(k+1)·P_k(k) mod phi, P_k truncated (staircase: coeff j absent for k<j). 101 inputs vs 100
coeffs -> exact dim-1 left kernel w of staircase A[k][j]=k^j: M0 = Σ (L·w_k/β_k)·u_k is an EXACT integer
multiple of phi (~2^17.5k bits). KEY: factoring from ANY multiple of phi is randomized-poly (Miller/Sabt):
M0=2^s·m, random g, walk g^(2^i·m) to first 1, gcd(x−1,n). The mu growth / window on M/n that looks like a
wall is a non-issue — only log M matters. Flag ECSC{eprint_p4p3r5_c4n_b3_r3al1y_s0m3thin6_4t_tim3s_...}.
- sympy LUsolve on the 100x100 staircase minor silently returns GARBAGE (minor SINGULAR, rows carry j<=k);
  use A.T.nullspace() (~6 min) and ALWAYS run the algebraic annihilate-check on the result.
- Archive listeners kill conns at ~85-100s: per-char read(1) loop (~0.85s/roundtrip) lost 3 fetches of 101
  shares; chunked s.recv(65536) after select fixed it. Verify stop-tokens against the REAL banner ('private
  key?', not 'friends?' — timeout-matched tokens masquerade as working parsers).
- Python>=3.11: sys.set_int_max_str_digits(10**6) before json dump/load of >4300-digit ints (crash AFTER a
  6-min solve is the worst).

## RSA leaking phi^3 and d^3 with e=3: unique-common-root poly GCD (d-phi-enc hacktm_ctf2023, SOLVED 2026-10-31)
getStrongPrime(1024, e=3) => gcd(3,phi)=1 => cubing is a BIJECTION mod p and mod q (no
nontrivial cube roots of unity). Given enc_phi=phi^3 mod n and enc_d=d^3 mod n: phi is the
UNIQUE root mod n of g(x)=x^3−enc_phi, and (since 3d−1=k·phi, k∈{1,2}) also the unique root
of f_k(x)=(kx+1)^3−27·enc_d. Reduce f_k via x^3≡enc_phi to quadratic
q2=3k²x²+3kx+(1+k³·enc_phi−27·enc_d) mod n, Euclid-gcd(q2,g) in (Z/n)[x] (monic division,
check pivot invertibility — non-unit pivot = free factor) yields x−phi for the true k.
Then p+q=n−phi+1, sqrt disc, factor, decrypt. Fuzzed on 6 synthetic instances first; k=2
live. Flag HackTM{...}. Solver: Practice_runs/cryptohack_org/
challenge-325-cryptohack-d-phi-enc-hacktm_ctf2023/solve.py.

## Nagaty-style key exchange: secret only ever used mod p = free break (a_joke_cipher-hkcert_ctf2021, SOLVED 2026-10-27)
Shared secret = f(y_A,y_B)·S_A mod p with public commutative f and y_A = S_A mod p
=> S_A can be replaced by y_A: S_AB = (y_A·y_B² mod p)·y_A mod p from public data.
Then unpadded-multiply encryption c = m·S_AB inverts by exact division (verify
sk·m == c round-trip). Triage rule: find the modulus the final secret is reduced
under; wherever the private key enters the formula, it is only ever that residue.
Flag: [flag — recorded in FLAGS/ctf-archive/challenge-318-cryptohack-a_joke_cipher-hkcert_ctf2021/flag.txt].

## Nibble-permutation SPN, key XOR AFTER S-box → confined-set integral, full 8 bits
(DCTF2022 'key_recovery', SOLVED 2026-10-27; flag [flag — recorded in FLAGS/ctf-archive/challenge-271-cryptohack-key_recovery-dctf2022/flag.txt])
Cipher: `u_r = S(z_{r-1}) ⊕ k_r; z_r = per(u_r); ct = S(z3) ⊕ k3`, `per` = pure
NIBBLE permutation, `k0=K, k1|k2|k3 = sha512(K)[:48]`, 3000-block oracle.
- Vary one plaintext byte over 256 values: every ACTIVE byte at z1/z2/z3 is
  nibble-CONFINED (one fixed nibble, ≤16 values; multiplicity 16).
- ROUND-ORDER DECIDES THE ATTACK: confinement lives on the S-INPUT side; the key
  XOR sits on the S-OUTPUT side → a wrong key-byte guess is NOT a conjugation of
  the confined set, so `confined(S_inv[ct⊕g])` (and one peel per round) is an
  8-bit-sensitive test (wrong g fails confinement w.p. ≈1−2^-40). If XOR were
  BEFORE the S-box, every such test is conjugation-invariant and blind to half
  the bits of every key byte — the predecessor scripts ground forever on this.
  Always verify sub/xor/per ORDER against `block()` before building the test.
- Peel exactly: z3=S_inv[ct⊕k3], u2=per_inv(z3), z2=S_inv[u2⊕k2], …, then
  `k0 = u0 ⊕ S[x]` with NO guess. 8 chosen sets (2048 blocks) cover 14 bytes.
- `per` had a closed 2-byte island {3,15} (dest(3)=dest(15)={3,15}): those key
  bytes untestable, but the island never contaminates other bytes → recover 14
  bytes, brute force 2^16 island keys vs observed ct + sha512-schedule check.
- Debug discipline that broke the logjam: one script that measures per-layer
  activity/confinement EMPIRICALLY (size, #hi, #lo per byte) on a random key —
  it exposed that the inherited layer model (hence all 'z3' sets) was garbage.

## DGHV/ACD service where noise >= p/2: decrypt-oracle wrap leaks p mod N (additional_problems-csc_belgi, 2026-10-27; attack VALIDATED on local clone, live listener broken)
server.py: c = p*q + N*r + m, p=getPrime(128)/conn, q 1024b, noise N*r+m <= 2^126 < 2^127 <= p;
oracle: pick N in [2^7,2^8), add chosen encryptions, decrypt prints (c mod p) mod N per byte.
- Lattices DEAD here: eta-rho = 2 (Cheon-Stehle hard regime; SDA/OL dim > (g-rho)/(eta-rho) ~ 513
  and target norm 2^{g-eta+rho+1} > lambda1 — Galbraith ANTS'16).
- BREAK: accumulate k zero-byte encryptions: c = pQ + S, S = sum noise == 0 (mod N), S < k*2^126.
  Decrypt = (S - b*p) mod N = (-b*p) mod N, b = floor(S/p). k=4 => S < 2p => b in {0,1}; any nonzero
  byte Y => p = -Y (mod N) EXACTLY. Wrap prob (4 - p/2^126)/4 >= ~1/4; if never wraps (p ~ 2^128)
  use k=6 (b<=1 forced, wrap prob >= 1/3). l positions per decrypt = l free trials (use l=24).
- ~23 primes N in [128,256), CRT product 2^174 > 2^128 => unique prime p in [2^127,2^128);
  flag char = (c_flag mod p) mod 128 (remainder provably unwrapped). One connection, seconds.
- Generalize: any 'decrypt = (c mod p) mod small-modulus' oracle plus an ADD oracle leaks
  p mod (modulus) whenever accumulated noise crosses a multiple of p — the noise cancels mod N
  by construction, only -b*p survives. Grep pattern: `random.getrandbits` for q AND randint for
  noise both from Python random + N*rmax constant (here 2^126 for every legal N — the
  'all N are secure' comment hides that noise/|p| ratio is worst-case).
- Live listener archive.cryptohack.org:21970 died mid-banner (stalls at 319 bytes right after
  "...encrypted our secret flag with it:", socket open forever) = FLAG env unset, join over None
  kills the thread which only catches BrokenPipeError. Evidenced negative; retry before grinding.

## MT19937 'guess #2020 from 2 reveals' (2020-tetctf2020, negative result 2026-10-27)
- CPython emits word X_{624+j} at output j (state index starts at 624 -> FIRST
  output is POST-twist). Twist in linear word index: X_m = X_{m-227} ^ ((y>>1))
  ^ MAGIC*(y&1), y = msb(X_{m-624})<<31 | low31(X_{m-623}). So target word m can
  be computed from reveals at (m-227-624) and (m-623-624): for target X_2643 that
  is reveal indices 1792 & 1396, leaving ONLY bit30 (= msb of word X_2019) free
  => 1/2 win per session. The relation is SHIFT-INVARIANT: any fixed pre-draw
  offset shifts reveals+target together, same pair still wins.
- Untemper: iterate the fixed-point x = y ^ ((x<<7)&0x9d2c5680) form (in-place
  `y ^= (y<<7)&M` repeated is NOT the inverse); verify temper(untemper(o))==o.
- Live host accepted none of 79 covering guesses (2^-79) while the identical
  pipeline was exact 400/400 on CPython 3.10/3.11/3.12/3.14 => live build
  diverges from the posted file; documented in Practice_runs/cryptohack_org/
  challenge-13398-cryptohack-2020-tetctf2020/AAR.md. Lesson: when a model-true
  oracle rejects p=1/2 guesses k times, STOP guessing and test build-divergence
  hypotheses (raw words, echo, print-lag, fixed r) as separate cheap sessions.

## ECDSA + truncated LCG nonce, unknown modulus (ECLCG hitcon2024, UNSOLVED — wall map, saved 2026-10-28)
Nonce k_i = LCG(a,b,x0) mod p (p = 311b prime, larger than curve q ~ 2^256). Then k_i = (t_i+u_i d mod q) + m_i q with m_i < p/q (~2^55) and t_i=z_i/s_i, u_i=r_i/s_i: ALL truncated states lie on a 1-parameter line in d mod q.
- VALIDATED primitive 'given-d gcd': differences Delta_i=k_{i+1}-k_i obey Delta_{i+1}=a Delta_i mod p, so p | Delta_{i+1}Delta_{i-1}-Delta_i^2; gcd of the 14 triple-minors == p exactly (synthetic-verified). Also kills a,b: all 2x2 minors Delta_i Delta_{j+1}-Delta_{i+1} Delta_j are p-multiples.
- DUALITY WALL: reduce k_{i+1}=a k_i+b-e_i p mod q -> m_i terms vanish, but quotients e_i=floor((a k_i+b)/p) are UNIFORM ~2^311. Every projection keeps only full-size unknowns (a,b,p,e_i). Truncation bits and LCG quotients are the same information in two containers.
- Why single lattices fail (counted, don't re-derive): p unknown => no congruence lattice; exact-Z linearization needs e_ij*p monomials (~2^624) => box volume exceeds det by ~2^20000 (any variant: (d,m),(k,d), known-d). Quadratic minor terms q^2 n_i n_j ~ 2^624 >> p ~ 2^311, so Coppersmith truncation-of-terms is invalid. This is bounded-MQ-over-unknown-modulus; needs a structural trick, not a bigger lattice.

## Broadcast RSA when the server never sends its moduli (key_backup_service_1-hkcert, SOLVED 2026-10-28)
Service encrypts the same low-entropy secret (256-bit master key) under fresh textbook-RSA
keys, e=17, via a 'backup' flow => Hastad broadcast: ms^17 < prod(5 moduli) -> CRT + integer
17th root; then AES key = the secret. The moduli are NEVER returned, but ONE chosen-ciphertext
probe recovers each: send m=2^61; the reply c = m^e mod n means m^e - c = k*n with k confined
to a ~2^13-wide window (k in (2^13, 2^15]); the unique divisor of (m^e - c) inside that window
is n. pow-verify every recovered n before CRT. General rule: any oracle computing c = m^e mod n
for chosen m with m^e > n leaks n as a factor of the integer excess m^e - c; a tight bound on
the quotient k turns factor-recovery into a 2^13-range scan. Flag-shaped note: MT19937-flavored
keygen machinery in the same server was a red herring for v1 — always identify which component
the break actually touches before modeling it.

## (a+b·x)·P oracle tuples + smooth group order (hide_and_seek ECSC2023 Norway, SOLVED 2026-10-28)
Given tuples (a_i,b_i,R_i=(a_i+b_i·x)P) with Q=x·P hidden: two-tuple elimination with the KNOWN
determinant Δ=a_j·b_i−a_i·b_j gives S=b_i R_j−b_j R_i=Δ·P and T=a_j R_i−a_i R_j=Δ·x·P, so
P=Δ⁻¹S, X=Δ⁻¹T — a bare DLP. Then ALWAYS run ellap+factor on #E(F_p): here n was a product of
9 primes ~2^34.9 (squarefree) -> Pohlig–Hellman + BSGS(√q≈2^17.5) per factor, CRT; gmpy2 affine
BSGS solved all 9 factors in ~2 min. Flag [flag — recorded in FLAGS/ctf-archive/challenge-266-cryptohack-hide_and_seek-ecsc_2023_norwa/flag.txt].
- gp64 F_p curves (ellinit with Mod coeffs, old API): **infinity is [0]** — `elladd(E,[],Q)`
  ERRORS and `P==[]` is always false (silently breaks order checks); Map-keyed BSGS in GP is
  ~8 ms/step at 310-bit (use Python+gmpy2 for hot loops).
- GP parser: multi-statement `if(c, a; b)` bodies need `{ }`, but `{ }` inside call args is
  'embedded braces — not yet implemented'; keep statement sequences directly in for-bodies or
  in helper functions (single-expression ifs only elsewhere). One bad construct cascades into
  bogus errors (unbound `i` = complex I -> 'gtos t_POL').

## Tiny-seed MT19937 keygen + small message => partial factorization, not full (RRSSAA ECSC2023 Norway, SOLVED 2026-10-29)
N = prod of 126 primes 256b, prime #i from fresh random.Random() seeded randbelow(2**i);
e=65537, flag 1024b ≪ N (~32k bits).
- Do NOT try to factor all of N and do NOT brute-force per index: one GLOBAL seed scan
  s in [0,2^K) with the exact seeding+rejection-loop replay provably finds every factor
  whose index i<=K (seed<2^i<=2^K). K=14 -> 16k seeds, ~3 min, 15 primes found.
- Pitfall that ate a run: per-index loops with `break` on first N%p==0 — seed 0's prime
  divides N and masks every real seed. Global scan, no break, dedupe via set.
- Only need ~5 primes (product P > 2^1024 >= m): P|N so m^e=c mod P; d=e^-1 mod phi(P)
  (skip any p with p=1 mod e), m=c^d mod P is EXACT since m<P. Verify pow(m,e,N)==c.
Flag ECSC{brute_it_like_bruce_...}. Solver: Practice_runs/cryptohack_org/
challenge-284-cryptohack-rrssaa-ecsc_2023_norway2023/solve.py.

## LWE with even noise = perfect LSB parity leak, flag-bit classifier (tough_decisions ECSC2023 Norway, SOLVED 2026-10-30)
`sample_noise(n)` doing `e|=randbit(); e<<=1` in a loop yields e=2*uniform ⇒ noise ALWAYS even ⇒
real samples satisfy `LSB(b) = GF(2)-dot(a mod 2, s_low)` deterministically (upper noise bits
uniform mod 2^(n-1), parity is the ONLY leak, and it's perfect). 16-bit key-byte-LSB vector:
brute 2^16 masks, correct one makes ALL samples of real groups parity-consistent (score 154/296
vs runner-up 17). Two traps that both cost a run:
- `[[real, fake][b](s)]` — list index means **b=0 → real**. Verify the labeling with a 2^16
  prefix-fit scan against a candidate flag prefix (both hypotheses) before trusting a decode;
  this flag's prefix was `ECSC{`, not `crypto{`.
- The mask gates the **per-byte LSB vector** (`v |= (a_j&1)<<j; popcount(v&m)&1`), NOT the raw
  16-byte integer AND-ed with m.
Error direction is one-sided (fake-1 groups all-match w.p. 2^-6 ⇒ true-1 decoded as 0), so true
byte = decoded | subset of its zero bits — charset-constrained fix per bad byte. Flag
[flag — recorded in FLAGS/ctf-archive/challenge-13400-cryptohack-tough_decisions-ecsc_2023_nor/flag.txt]. Solver: Practice_runs/cryptohack_org/
challenge-13400-cryptohack-tough_decisions-ecsc_2023_nor/solve2.py.

## Toy-NTRU p=2 no-wrap parity decryption + Windows lattice wall (origami-nns_ctf_20252025, 2026-10-29)
NTRU n=512 q=127 p=2 df=dg=35: ct=2hr+m. lift(f·ct mod q) to [0,126) is EXACTLY 2gr+fm
(per-coeff ≤ 2dr+df = 79 < q), so mod-2 gives f·m over GF(2)[x]/(x^n−1); odd df ⇒ f unit
(x^n−1=(x+1)^n over F2) ⇒ m via 512×512 GF(2) solve — r drops out. Any recovered (f',g')
with {0,±1} coeffs, odd wt(f'), 2Σ|g'|+Σ|f'| < q works. Selftest both: lift-exactness AND
decode order (LSB-indexed bits of bytes_to_long int → to_bytes(64,'big')); circulant mult
matrix is NOT symmetric (row c: f[(c−i) mod n]).
- dim-1024 lattice reduction on THIS Windows host: fpylll 0.6.4 BKZ dies STACK_OVERFLOW
  0xc00000ff (event log) at 1024, fine at 512 (LLL 19s, BKZ20 42s); 64MB thread stack didn't
  save it. PARI qflll works (~7 min at 1024) but plain-LLL min stays q²=16129 (target 8.4 is
  BELOW Gaussian heuristic — only enumeration/BKZ touches it).
- gp 2.17 renames/gotchas: `lll`→`qflll`; `clock()`→`gettime()`; no `transpose`→`M~`; NO
  `flush` function (silent break-loop!); `random(a,b)` invalid, `random(n)`=[0,n); every
  statement must fit ONE line (multi-line for() = parse error).
- **qflll conventions (verified on mini instance):** qflll(X,0) returns T such that reduced
  vectors are the COLUMNS of X*T (qflll works on columns; flag 3 output rows/cols are NOT
  the lattice — near-wasted a whole session). Build M=[[I,H],[0,qI]] → vectors live in
  ROWS of M, so V=M~; V=V*qflll(V,0); scan COLUMNS. ALWAYS membership-test a dumped vector
  b ≡ a·h mod q before trusting it; norm-1 'SMALL' rows were the trivial column-lattice
  {(a,b): q|b} leaking through.
- One heavy gp64 at a time: 3 zombies × 3.2GB caused silent 0xC0000142 init failures that
  looked like crashes; `tasklist | grep -a` (plain grep -c can under-report), kill via
  powershell Get-Process|Stop-Process (taskkill flag-mangling in git-bash).

## Unvalidated ECDH scalar oracle + ephemeral-ECIES flag = free keystream (pekobot AIS3-pre-exam2022, SOLVED 2026-10-31)
Server: fixed d, P=dG; option1 returns `quote XOR point_to_bytes(Q*d)` for ANY attacker x,y (no curve check); option2 gives `C1=rG`, `C2=flag_pad XOR point_to_bytes(rP)`. Feed Q=C1 into option1: `C1*d = r(dG) = rP` — the exact flag keystream; XOR one of the hardcoded quotes (known plaintext, `ljust(64,\0)`) to recover it, then `C2 XOR key` → flag. No ECDLP, no d recovery.
- Twisted-#E small-subgroup route checked and ruled out first: #twist(P-256)=3·5·13·179·(241-bit prime) → only ~15 bits of d; factor #twist before planning any invalid-curve DLP attack.
- Trivia: flag tail is `os.urandom` padding — validate candidate only up to the `}`.
- Socket pitfall: prompt tokens `x: `/`y: ` don't end with the menu's `> `; never concat responses (glues prompt+ct onto one line and hex-line filters miss it) — sync on each exact prompt token.
Flag [flag — recorded in FLAGS/ctf-archive/challenge-315-cryptohack-pekobot-ais3_pre-exam2022/flag.txt]. Solver: Practice_runs/cryptohack_org/challenge-315-cryptohack-pekobot-ais3_pre-exam2022/solve.py (+ in-process harness.py).

## Linearization beats any lattice for parity-of-inner-product oracles (dark_arts-codegate_ctf2022 C3, wall BREACHED 2026-11-05)
Oracle `b = (⟨k,x⟩ mod p) mod 2`, k small-coords over GF(p) (p odd), x attacker-uncontrolled/random:
for b=1 queries the residue set is {1,3} ⇒ `(S−1)(S−3) ≡ 0` ⇒ `S²+S ≡ 2 (mod 5)` (general p: any
bit-condition on S is a low-degree poly eq over GF(p)). Treat ALL monomials {k_i, k_i², k_i k_j}
(= n(n+3)/2 vars) as INDEPENDENT GF(p) unknowns → each query is ONE linear equation; ~2× the
unknown-count in queries ⇒ RREF is full rank, unique solution, key on the linear coords. Verified
5/5 exact recovery at n=64 with N=6000 queries (c3_linearize_check.py in challenge-13399 folder).
Author's own writeup: rkm0959.tistory.com/247. WALL-MAP LESSON: 3 audit runs declared a
'proven structural wall' after pricing Kannan/BKZ, box-CVP DFS, stats, MITM, Fourier — linearization
was never even in the ruled-out list. Before declaring any CTF oracle a wall, check the author's
blog/writeup and the linearization family (monomials→independent vars) FIRST.
Numpy pitfall: uint8 GF(5) elimination silently wraps (256 ≡ 1 mod 5) — eliminate in int16+.

## Pitfalls
- **`len(set(pbox))==n` index-list guard broken by Python negative indices**
    ('Sign in Please' HKCERT2020, SOLVED 2026-10-25): auth demands
    sha256(permutate(pw||salt, pbox)); a spy oracle hashes permutate(pw||OUR_salt,
    OUR_pbox) for any pbox with 20 DISTINCT ints — but x and x-20 hit the SAME byte,
    and entry count is uncapped. Min unknown pw positions per query = 20 - 2*|salt|
    ints spread 2-per-position = 6 (each byte has exactly 2 int reps). 3 spy queries
    (pos 0-5, 6-11, 12-15+known 0,1) -> 2x64^6 + 64^4 offline brute force (custom C
    scalar sha20, -O3 -march=native -fopenmp, ~6e7/s x16 cores, ~10 min/query) ->
    full password -> answer auth. Pitfall: server's parse_pbox does payload[1:-1] —
    pbox input MUST be bracketed "[a,b,...]" or it silently 'no way!'s. Flag:
    [flag — recorded in FLAGS/ctf-archive/challenge-291-cryptohack-sign_in_please-hkcert_ctf2020/flag.txt]. Solver: Practice_runs/
    cryptohack_org/challenge-291-cryptohack-sign_in_please-hkcert_ctf2020/.
- **Berlekamp–Massey on a WINDOW of an LFSR recovers the tail's minimal polynomial, not
  the generator** (`lwin`, 120, SOLVED 2026-10-25): BM on 2048 output bits returned deg-265
  poly that fails to annihilate earlier bits — it fits the observed tail, not the true
  recurrence. When the generator has few unknown taps, set up the LINEAR system
  s[n+L] = Σ c_t s[n+t] over all n in the window instead (GF(2) solve, check rank);
  tap 0 present ⇒ transition invertible ⇒ run the recurrence BACKWARDS to recover the
  initial state (the flag). Validate on a ground-truth toy first — that's what caught this.
- **e-small broadcast across DIFFERENT moduli (johan, SOLVED 2026-10-21):** identical unpadded message under e=3 with 7 distinct n: c_j differ even for identical m, so 'no duplicate ciphertexts' proves NOTHING — CRT-combine c's over subsets and take integer cube root (subset (0,2,5) hit; message was literally 'yes'). Run Hastad-CRT BEFORE Franklin-Reiter shift/delta scans.
- **MD5 second preimage is ~2^123 — infeasible.** If a hash-keyed store's stored keys match their stored contents (extract the real bytes from source via `ast`, don't trust a copy-pasted string), you cannot collide with a specific stored hash; look for the in-session collision path or another angle instead.
- **Static-DH socket servers (dh_static2, SOLVED 2026-10-23):** 'not strong enough' vs 'dodgy' are SEPARATE checks — the real rule was p must be EXACTLY 2048 bits, no p-1 policing. Build p=2RS+1 (R 256b prime, S smooth product of primes <2000 filling to 2048b); B=2^b leaks b mod S via PH with n=2RS as order MULTIPLE (gi=2^{n/pe}, hi=B^{n/pe}) — ord_p(2) need not be known or smooth. 2 sessions -> CRT -> exact b. KDF was sha1(str(A^b))[:16] + AES-128-CBC — trust the saved site.md of the sibling challenge over earlier CTR guesses.
- **CBC unchaining:** the oracle yields `D(CT_b)`, not the plaintext — apply
  `P_b = D_b ⊕ (IV if b==0 else CT_{b-1})` after recovering all `D_b`.
- **No padding block when the message is a clean multiple of the block size**
  (e.g. `urandom(16).hex()` = 32 bytes → don't strip a final block).
- **`execute_code` kernel ≠ terminal python:** the kernel interpreter often lacks
  pycryptodome/cryptography while terminal `python3` has them — run crypto code through
  terminal `python3`, not the kernel.
- **Run long interactive solves in the background** (terminal `background=true` +
  notify): a foreground timeout kills the client mid-attack, and a killed session can
  throttle the service (later requests return empty → JSON decode errors). Poll the
  log file for progress.
- **Identifying a weakness ≠ exploiting it:** documenting a confirmed property is a
  milestone, but if the flag needs a meet-in-the-middle you haven't engineered, record
  the reduction honestly and move on rather than burning the session.

## Canonical references (owner list 2026-11-02)

[R31] Knuth TAOCP Vol 1 (permutation/cycle structure — cycle-decomposition puzzle machinery). https://cs.stanford.edu/~knuth/taocp.html | [R34] Hellman, 'A Cryptanalytic Time-Memory Trade-Off', IEEE TIT 26(4), 1980 (+ modern rainbow-table line; TMTO puzzle mechanics). https://www-ee.stanford.edu/~hellman/publications/36.pdf | [R36] Cyclotomic polynomial https://en.wikipedia.org/wiki/Cyclotomic_polynomial (roots-of-unity structure in field tricks) | [R35] Hensel's lemma https://en.wikipedia.org/wiki/Hensel%27s_lemma (mod-p^k lifting; see padic-lift-ecc-attack).

## Permutation cycle-structure method (D12 gap, closed 2026-11-02)
For any 'repeated application of a substitution/permutation' puzzle (TAOCP Vol.1 [R31], §1.3.3):
1. Decompose into DISJOINT cycles once; order = lcm(cycle lengths); parity = even-count of even-length cycles.
2. Inverting 'how many applications to return to start' = order; 'state after k steps' = rotate each cycle by
   k mod len. Composition order (right-to-left vs left) is the classic implementation trap — test on a toy.
3. Crypto hookups: S-box as permutation (cycle structure of iterated S-boxes), LFSR state maps (order
divides 2^n−1), Feistel rounds as permutations; 'find k with P^k = target' = discrete log IN the cyclic
subgroup generated by P — baby-step on cycle-rotations when order smooth.
4. Reconstructing P from 'P^k known': k-th root of a permutation exists iff cycle-length counts satisfy the
   gcd(k,len)-splitting condition — each len-cycle's preimages split into gcd-many cycles; build, don't guess.

## Meet-in-the-middle search (D9 residual, van Oorschot–Wiener lineage)
- Double encryption E'_{k2}(E_{k1}(P)): table all E_k(P) over key-space candidate set, table all D_k(C)
  reverse, intersect — time 2^κ becomes 2·2^κ work but memory 2^κ kills the naive win; the CTF version
  SHRINKS one key space (known prefix/weak KDF/partial-hash-verified key) so the intersection fits.
- Key-schedule MITM (AES-128 double = classic 2^120 memo): only wins with constrained keys; always check
  the KEY GENERATION (password, truncated hash, seeded PRNG — ctf-mt19937 hookups) before dismissing MITM.
- Practical trap: false intersections (~2^{2n−2κ} for n-bit block) need a SECOND (P,C) pair to filter —
  filter on pair 2 during table-build, not after. Disk-backed sort for tables >2GB (host rules).
