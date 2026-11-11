---
name: ctf-ecc-attacks
description: "Use for ECDLP/ECC CTF tasks: smooth orders, ladder checks."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, ecc, ecdlp, pohlig-hellman, elliptic-curve]
    related_skills: [ctf-crypto-attacks, ctf-practice-runs, cryptohack-socket-challenges]
---

# CTF ECC attacks — ECDLP server recipes

## When to Use
Solving an elliptic-curve challenge: ECDH-style server (send base point(s), get x(k·P)),
Montgomery/(X,Z) ladders, or any task where the curve's group order is the attack surface.
Block-cipher/oracle recipes live in `ctf-crypto-attacks`.

## Weierstrass x-only ladder = twist oracle (twisted_mind, 80, SOLVED 2026-10-20)
A Montgomery-style (X,Z) ladder on a WEIERSTRASS curve (a=-3) with an off-curve x0
(t = x0^3+ax0+b a non-residue) computes x([k]P') on the QUADRATIC TWIST — verified
39/39 locally (work in F_p[s]/(s^2=t), P'=(x0,s); x([k]P') lands back in F_p).
WRONG prior belief that cost a whole session: "twist attacks apply only to Montgomery
form". Attack: server gives x(k·P) for 2 chosen x-coords -> pick one ON E, one OFF E.
PH on E gives k mod S (smooth part of #E); PH on E' gives k mod S' (smooth part of
#E' = 2p+2-#E). Even when BOTH have a big prime factor, lcm(S,S') > #E means the two
residues pin k uniquely in [0, N/2] — the big factors are irrelevant. Sign: x-only
=> k mod S known up to global ±; 4 CRT combos, filter by range + local check
x([c]P)==A1; get_flag attempts are usually unlimited.
F_p^2 PH: target y-lift w = sqrt(rhs(A2)/t) in F_p, Tp = (A2, w*s).
TIMEOUT DISCIPLINE: server clock starts at connect — precompute ALL BSGS tables
before connecting (base points are your choice!), live phase = queries + giant steps.

## Affine group-law gotcha that eats whole sessions (twisted_mind debugging)
In affine (x,y) mod p: P + (-P) test must be `(y1+y2) % p == 0`, NOT `y1+y2 == 0` —
reduced residues sum to p, not 0. The bug is INVISIBLE to random tests (fires only
when the sum is exactly O) and only shows as [N]P != O. ALWAYS assert #E·P == O before
trusting any PH/BSGS pipeline; cross-check vs PARI ellmul.

## Always-on workflow (in this order)
1. **Read the server source** (CryptoHack lists it in the statement). Extract p, a, b, the
   stated `order`, the key-generation line, query limit, timeout, and the verification line
   (`guess % order == privkey` ⇒ you need the FULL key, not a residue).
2. **Verify the REAL group order**: the stated `order` may be a subgroup. PARI: `ellcard(ellinit([a,b],p))`
   with a big stack (`gp64 -q -s 200000000` — default 8 MB overflows on 192-bit curves).
   PARI 2.17 / our gp64 build gotchas: `ellorder` does not exist (use `ellcard`);
   `bitnum`/`logint` fail ("not a function" / "too few arguments") — print
   `N == given` and `factor(N)` instead. Cross-check factorization with sympy `factorint`+`isprime`.
3. **Classify the order**: FIRST compare #E to p and p+1 directly: #E == p ⇒ ANOMALOUS ⇒
   Smart's attack (recipe 3) — an `assert is_prime(order)` in the source does NOT rule this
   out (p is prime!). Then split factors into smooth part S and large prime(s) Q.
   Feasibility per part: DLP mod q costs ~2^(bits(q)/2). A 37-bit factor is trivial; a
   91-bit prime is ~2^45.8 = infeasible. All factors ≤ ~45 bits ⇒ Pohlig–Hellman.
4. **Re-implement the server's ladder verbatim** and check it against a reference affine
   double-and-add (full x,y) for ~200 random scalars AND on torsion points of each small
   factor. 0 mismatches ⇒ output is exactly x(k·P); no bug to exploit. Also test edge cases:
   scalar with bit_length < 2 (loop never runs → `UnboundLocalError` on `bit` in naive code —
   measure-zero, not an attack), and Z=0 → string "Infinity" responses.
5. **Probe off-curve inputs — ALWAYS an attack vector, never noise**: any x-only/(X,Z)-style
   rational ladder evaluated OFF the curve computes a group law on the twist family (verified
   for Weierstrass a=-3, twisted_mind) or a degenerate group (Edwards on {(0,y)} = F_p^*,
   degenerate). "Pseudo-random looking output" = you are computing in a group you have not
   identified yet. Factor the twist order too; see the twist section above.
6. **Check the pairing exit**: embedding degree = ord_Q(p) (smallest k with p^k ≡ 1 mod Q;
   iterate p^k mod Q). k > ~100 ⇒ no MOV/Weil shortcut for a 192-bit p (GNFS in F_{p^k}*
   stays > 2^60).
7. Pick the attack: smooth order ⇒ recipe 1 below. Large prime part > ~46-bit sqrt ⇒ STOP:
   record the wall honestly (cf. ctf-crypto-attacks: identifying a weakness ≠ exploiting it)
   and move on.

## Recipes
1. **Small-subgroup / Pohlig–Hellman on smooth group order** (`twisted_mind`, 2026-10-19):
   Server: `pubkey = x(k·P)` for up to 2 chosen x-coordinates, 120 s, verify `guess % order == k`.
   - Order = S·Q with S 102-bit smooth and Q 91-bit prime ⇒ k mod S alone is NOT the key.
     The Q-part (2^45.8) is infeasible ON E — but the twist side closes it: see the
     twist-oracle section at the top (twisted_mind SOLVED 2026-10-20 that way).
   - **Find a point of exact order d**: `cand = pt_mul(order // d, P_random)` (NOT
     `pt_mul(d, P)` — that has order #E/gcd(#E,d): the bug that silently swaps S- and
     Q-order points!). Always verify BOTH `d·cand == O` AND `(d//q)·cand != O` for every
     prime q | d.
   - **BSGS per prime factor q** (q ≤ 2^37 ⇒ m = isqrt(q)+1 ≤ ~4.3e5 table entries, seconds
     in CPython with built-in pow for inverses): G_q = (S//q)·P_S, T_q = (S//q)·A1; table of
     i·G_q, giant steps with −(m·G_q). e_q = dlog ⇒ k mod q.
   - **CRT** over the prime factors ⇒ k mod S.
   - **x-only output ⇒ sign ambiguity**: the response fixes the point up to ±, so the true
     residue is r or S−r (a single global sign, not per-q). Keep both candidates;
     disambiguate with a second subgroup when available, or verify against the final guess.
   - **Curve-consistency probe on a live server**: the two queries double as a check that the
     live curve equals the file: lift A1, A2 from x (p≡3 mod 4 ⇒ y = rhs^((p+1)/4)); require
     A1 on curve & S·A1 = O; A2 on curve & Q·A2 = O & S·A2 ≠ O.
2. **Full DLP on a small group** (order ≤ ~2^40): plain BSGS on the full group with the
   server's own base point — no subgroup structure needed.
2b. **Bounded secret ⇒ partial PH suffices** (`micro`, 120, SOLVED 2026-10-21): if the
   secret is `getrandbits(k)` (n < 2^k), PH only needs smooth factors whose product
   S > 2^k — big prime factors of #E are irrelevant. x-only ± ambiguity dies to the
   same size bound: r < 2^k ⇒ n = r, else n = S − r (needs S > 2^(k+1)). Sign of the
   lifted partner point never matters: x(n·(−B)) = x(n·B).
3. **Anomalous curve, #E == p (Smart's attack)** (`exceptional`, 100, SOLVED 2026-10-20;
   works at 512-bit p in seconds): lift to E~ over Z/p². For P=(x,y): y~ = y + t·p with
   t = ((x³+ax+b − y²)/p)·(2y)⁻¹ mod p (exact lift mod p²). λ(P) = t([p]P̃)/p mod p where
   t = −x/y: compute [p]P̃ in JACOBIAN coords over Z/p² (no inversions; Z ≡ 0 mod p),
   rescale Z→p via λz = (Z/p)⁻¹ mod p², X'=λz²X, Y'=λz³Y, λ = −X'/Y' mod p.
   Then n = λ(Q)·λ(P)⁻¹ mod p. Validate the whole λ pipeline on a SMALL anomalous curve
   first (scan: gp `forprime(p=749,2000,for(a=1,3,for(b=1,5,...ellcard(E)==p...)))` —
   p=1039,a=2,b=5 works; the textbook p=751 example is NOT anomalous).
   gp gotcha: forprime/for take (var=lo,hi,body) — NOT a vector; multi-line loops piped to
   stdin can fail 'unexpected end of file' — use one line or a .gp file.

## Edwards law on off-curve points = multiplicative group (degenerate, 100, SOLVED 2026-10-20)
"Edwards Goes Degenerate": twisted Edwards −x²+y²=1+dx²y², compressed base (1,11) whose
xsqr is a NON-residue -> recover_x returns 0 -> base point (0,11) is OFF the curve. The
complete Edwards addition law is CLOSED on {(0,y)}: (0,y1)+(0,y2) = (0, y1*y2 mod p) —
the whole "ECDH" is DLP in F_p^* with base 11. p−1 was smooth (2 · ten ~2^25 primes, gp64
factor in seconds) -> PH+BSGS -> n_a; secret = y_b^{n_a}; done. Red herrings: prime
`order` in keygen (never the real group), #E of the actual curve (irrelevant — the points
never live there). Checklist: after decompressing ANY point, verify the curve equation;
if x=0 came from a failed sqrt, hunt the degenerate group the formulas induce.

## Invalid-curve oracle with PER-CURVE sign ambiguity (checkpoint, 150, SOLVED 2026-10-21)
ECDH server, no point validation, key=sha256(str(x(s·Q)))[:16] + known-plaintext test
message => oracle for x(s·Q). Send order-m twist points (m ~2^20 smooth part of random
b' curves, PARI ellcard), enumerate r<m => s = +/-r mod m. CRITICAL: each curve's sign
is INDEPENDENT (x(rQ)=x(-rQ) per curve, not one global ±): all-positive CRT is a
mixed-sign mongrel that passes small-prime overlap consistency (± agree mod 2) yet is
NOT s — every KDF/point variant then fails and "secret must be huge" looks true.
- Build the KDF-free self-check into the collector: recovered_x * G == server_pub
  (banner pub). It separates "scalar wrong" from "KDF wrong" and proves bit-sufficiency.
- Save RAW per-curve (b,m,r); merging per prime destroys per-curve sign coherence.
- Sign search: pick ~16 curves with no shared prime >2 (~320 bits > any 256-bit s),
  enumerate 2^16 signs, CRT over distinct max prime powers, verify x*G==P. Linearize if
  slow: x(mask)=x_base-2*sum C_i, precompute x_base*G and C_i*G (17 pmuls), ~8 padds/mask.
- All residues must come from ONE session (s is per-session); a reconnect invalidates all.
- PARI gp files: LF-only (CRLF in a generated .py string survives newline="\n" — strip \r),
  and top-level multi-statement for-bodies need the if(1, ...) idiom.
- CBC single-block oracle match: ECB-DECRYPT(C1) xor IV == plaintext[:16] exactly (not
  startswith of a 19-byte constant; not ECB-encrypt).

## Pitfalls
- **Jacobian doubling: Z3 = 2YZ** (with X3 = M²−8XY², Y3 = M(S−X3)−8Y⁴). Writing 4YZ is a
   classic typo — it silently computes wrong points. Cross-check Jacobian mul vs affine mul
   mod p for n = 2,3,5,17 before ANY p² / formal-group work.
- **BSGS sign**: table g^j + giant walk h·(g^m)^i gives x = **j − m·i** (mod q), not j+m·i.
  Always assert g^xq == hq per prime factor before CRT (this assert caught the bug).
- **`pt_mul(d, P)` ≠ order d.** It is `pt_mul(#E//d, P)` for full-order P; verify exact
  order both directions or the whole PH runs on the wrong subgroup (selftest symptom:
  S·A1 ≠ O despite A1 = x(k·"P_S")).
- **The stated `order` is for key folding/verification, not DLP difficulty.** Difficulty is
  set by the orders of points that exist (divisors of #E). Check #E itself.
- **Key folding** `min(k, order−k)` gives a uniform key in [0, order/2) — 191 bits when
  order is 192 bits; a residue mod a 102-bit S is NOT the key.
- **CryptoHack listener banner is raw text** ("Welcome!\nYou can submit...") before the
  JSON protocol — read lines until a JSON object arrives; don't `json.loads` blindly.
- **Python BSGS memory**: 2^23+ entries ≈ several hundred MB; fine to ~2^24, then switch to
  C or a distinguished-point Pollard rho.
- **No writeups** (standing rule): solve from first principles; when stuck, the deliverable
  is the wall-analysis (tried / ruled out with reasons / the exact mathematical obstacle).

## Canonical references (owner list 2026-11-02)

[R45] Galbraith, 'Mathematical Foundations of Public Key Cryptography', Cambridge 2012, ISBN 9780511591702 (Vol. I repackaging — cite edition+ISBN). https://www.cambridge.org/9780511591702 | [R46] Menezes-OKAMOTO-Vanstone, 'Reducing elliptic curve logarithms to logarithms in a finite field', IEEE TIT 39(5):1639-1646, 1993 — MOV = Menezes-Okamoto-Vanstone (NOT Oesterle/Voloch); embedding degree k=ord_l(q) defined here. https://doi.org/10.1109/18.259647 | [R47] Blake-Seroussi-Smart, 'Elliptic Curves in Cryptography', Cambridge 1999. https://doi.org/10.1017/cbo9781107360211 | [R48] Jao, 'Elliptic Curves in Cryptography' course notes 2007. https://math.uwaterloo.ca/~djao/co789.2007/co789.pdf
