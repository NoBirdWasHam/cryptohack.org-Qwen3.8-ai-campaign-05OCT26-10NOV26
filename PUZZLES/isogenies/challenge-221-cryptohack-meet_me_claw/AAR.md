# meet_me_claw (CryptoHack, isogenies, 120 pts) — AAR

## The challenge
SIDH key exchange, p = 2^35·3^29 − 1, E0: y²=x³+x over F_{p²}=F_p[i].
Public: 2^35-basis P2,Q2 and 3^29-basis P3,Q3 of E0, Alice's curve EA, Bob's secret
sB = 495832856, and AES-CBC(iv,ct) of the flag keyed by SHA256(str(shared_secret)).
Alice's torsion images phiA_P3, phiA_Q3 are MISSING ("Alice forgot to send me her
torsion data!"). Goal: recover the shared secret j(E_AB) from EA alone.

## Note on the orchestrator's genus-2/Richelot steer
The statement is plain elliptic-curve SIDH (no genus-2 curves, no Richelot/Igusa
objects anywhere in source.sage), so the Donagi–Livné / CLAW genus-2 steer does NOT
apply and was ignored, per its own instruction. The "claw" here is a meet-in-the-middle
claw in the 2-isogeny graph over F_{p²}.

## Attack: MITM claw on Alice's 2^35 walk
Alice's public curve EA = E0/⟨P2 + a·Q2⟩ for secret a ∈ Z/2^35. The torsion images are
NOT needed: recovering a (equivalently the full 35-step Vélu-2 chain) lets us compute
phiA(P3), phiA(Q3) ourselves, then the shared secret the standard way.

MITM split 35 = 23 + 12:
- FORWARD: binary tree of depth 23 over a mod 2^23. Node (i, a mod 2^i) = curve
  E_i = E0/⟨2^{35-i}(P2+aQ2)⟩; children kernels u and u+w where
  u = 2^{34-i}(p2_i + a·q2_i), w = 2^34·q2_i (tracked incrementally). 2^23 j-values
  stored in a hash table.
- BACKWARD: 2-isogeny tree of depth 12 from EA. Children = quotients by each
  F_{p²}-rational order-2 point; rational 2-torsion x-coords = rational roots of
  x³+Ax+B found by Cantor–Zassenhaus gcds in F_{p²}[x]/(f). NOTE: off-path curves
  generally have only ONE rational 2-torsion point (the dual kernel) — the cubic has
  one root in F_{p²} and a conjugate pair in F_{p⁴}; roots3() returns 1 or 3 roots.
- Collision j(E_23 fwd) == j(E_12 bwd) pins a mod 2^23; brute-force the top 12 bits by
  extending the forward chain (4096 × 12 Vélu steps) and checking j(E_35) == j(EA).

Then: full walk tracking P3,Q3 → phiA(P3), phiA(Q3); H = phiA(P3) + sB·phiA(Q3)
(order 3^29 on EA); kill ⟨H⟩ with a 29-step Vélu-3 chain → E_AB; shared = j(E_AB);
key = SHA256(str(j)) (Sage format "<im>*i + <re>"); AES-CBC-decrypt.

## Engine validation (all done BEFORE the live run)
- velu2 codomain/map: matches hand example (kernel (0,0) → −4x) and the book-verified
  two_isogenies example (kernel (i,0) → 11x+14i); homomorphism + on-codomain tests pass.
- velu_odd (3-isogeny): closed form x' = x + u/d² + t/d, y' = y(1 − t/d² − 2u/d³),
  t = 2(3xQ²+a), u = 4yQ², codomain a'=a−5t, b'=b−7(xQ·t+u) — verified pointwise
  against PARI `ellisogeny`/`ellisogenyapply` (both coordinates matched exactly).
- Full pipeline (MITM + both shared-secret paths agreeing) verified end-to-end on a
  toy instance p = 2^8·3^5−1 (toy.py): recovered a == true a, Alice-side j == Bob-side j.

## Key numbers
- p = 2^35·3^29 − 1 ≈ 2.36e24 (81 bits); j(EA) = 274136031475621789081632*i + 394101024018039228107979
- forward table: 2^23 entries; backward: ≤3^12 nodes; top-bit brute: 2^12.

## Bugs found the hard way (each silently produced wrong math)
1. finv() dropped the norm-inverse factor on the imaginary part → every division wrong.
2. eadd doubling slope missing the +a term (3x²+a).
3. Poly-mod reduction off-by-one degree (x³ = −Ax−B shifts by 3, not 2).
4. Vélu "by-definition" map via x(P+Q)+x(P−Q)−x−2xQ is WRONG (mis-remembered formula);
   the closed form (PARI-verified) is right. Memory alone ≠ safe; PARI cross-check = safe.
5. E(F_{p²}) exponent is p+1 (trace 0) — toy basis multipliers must be 3^eb / 2^ea, not
   (p+1)²/2^ea.
6. Off-path curves have only 1 rational 2-torsion point; a "3 roots" assumption hangs or
   crashes (TS sqrt on non-residue).

## Result (SOLVED, flag accepted, score_delta +120)
- Forward table: 2^23 entries, ~3.6h (672µs/node — dominated by one modular inverse per
  point op; mpz/gmpy2 or inv-free projective coords would cut this ~3x).
- Backward tree: 3^12 nodes, 1630s, EXACTLY 1 match (no twist false positives).
- Recovered Alice secret a = 12988567850 (0x3062dd12a), 35 bits.
- j(E_AB) = 1015221285446986714363788*i + 2287090753163042176093763
- Key string (Sage str of F_{p²} element): "<im>*i + <re>" — first candidate tried.
- FLAG: crypto{clawing_our_way_to_victory}  (submitted; score 16800→16920, 238→239 solved)

## Limitations / lessons
- 3.6h forward pass is slow: budget compute BEFORE launching (or split 24+11 / use
  gmpy2). A subagent with a call budget must chain fwd→bwd→final into ONE background
  runner (run_all.sh) and poll cheaply — that pattern survived the wait.
- WorkingSet64 lies (OS trims); use PrivateMemorySize64 to track progress.
- The orchestrator's genus-2 Richelot steer was correctly ignored (see note above).

## Sources
Sources: challenge-provided materials plus a cross-check the run log cites only as "the book-verified two_isogenies example" (book title not recorded); no prior writeups per log.
