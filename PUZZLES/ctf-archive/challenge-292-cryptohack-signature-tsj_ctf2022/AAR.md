# AAR — challenge-292: CryptoHack "Signature" (TSJ CTF 2022)

## Status
IN PROGRESS (see bottom for final result).

## Challenge
Offline file challenge (statement card confirmed: files = challenge.py + output.txt only,
no remote listener — "flag given on forged sig / live port" from parent context does NOT
apply). ECDSA variant on secp256k1 with nonce `k = d XOR z` (z = raw sha256 int of 6 known
YouTube-URL messages). Public data: 6×(z, r, s) plus AES-CTR ciphertext of the flag under
key sha256(str(d))[:16]. Recover d → decrypt flag.

## The vulnerability / model
k = d XOR z = d + z − 2(d AND z). From s·k ≡ z + r·d (mod q):

    d·(s−r) − 2s·(d AND z) ≡ z·(1−s)  (mod q)

Writing d = Σ 2^j d_j, d_j ∈ {0,1}, each signature is ONE linear equation mod q in the
256 bit-unknowns:

    Σ_j 2^j·d_j·((s−r) − 2s·z_j) ≡ (1−s)·z  (mod q)

6 equations, 256 binary unknowns → expected #binary solutions = 2^(256−4·256)=~0 ⇒ unique.
Solved as CVP in the kernel lattice {w : M w ≡ 0 mod q} (det q^6) with target = sparse
particular solution x0 (free vars = 0). Model VALIDATED on simulated signatures
("model check on sim d: True") — true bits satisfy M·bits = v exactly.

## Key bug found this session (likely why earlier run "failed")
`solve.py:try_candidate` checked `r == x((d XOR z) mod q · G)`, but challenge.py multiplies
G by the UNREDUCED integer `k = d XOR z`. z is a raw sha256 value, ≥ q roughly half the
time, so k ≥ q frequently and k·G ≠ (k mod q)·G. The real r values therefore did NOT match
for the TRUE d ⇒ the 64-flip repair loop rejected the correct candidate and the run
wrongly escalated to BKZ. Fixed in solve.py (use k unreduced).

## Cost measurements (this host, fpylll)
- kernel_basis LLL (262×256, 256-bit entries): **1277 s**
- CVP.babai: 6 s
- Prior session (with buggy check): LLL+babai left only 6 nonbinary coords, then all
  64 flips "failed" — consistent with the k-reduction bug above.

## Pipeline (solve2.py, stages)
babai(+flips) → kannan-LLL(T=32 scan) → BKZ20+babai+flips → BKZ30 → exact CVP enum.
Flips now accept up to 8 bad coords (256 EC verifications).

## Session-2 continued: exact enumeration found & killed by fplll dim cap; v5 ladder
- v4 lattice = Kannan embedding of the v3 lattice: rows {(q e_i,0,0)} ∪ {(M_col_j, −e_j, 0)} ∪
  target row (v, 0²⁵⁶, 1). True solution = lattice vector (0⁶, d, ±1), norm ≈ 11.3 vs GH ≈ 230.
- MINI-SIM (q=2^127−1, N=56): plain LLL finds it (row 0) ✓; radius enumeration finds it ✓.
- FULLSCALE GATE (q=2^255−19, N=256): plain LLL misses (gap 20 < LLL Hermite at dim 263).
- fpylll exact enumeration (GSO+Enumeration.enumerate) works ≤220 dim, aborts at 256+:
  "fplll: enumerate: dimension is too high" → exact-radius enum unusable at 263 dim here.
- Serendipity: on the v4 lattice LLL takes 39 s (vs 21 min for the old kernel-basis matrix),
  so the reduction ladder is cheap. v5 = solve5.py: LLL scan → BKZ-20/30/40/60 with row-scan
  + snapshot (bbkzN.txt) after each stage. Running as proc_dc52eb88d747 → real5.log.

## Limitations / tried
- Foreground single-shot timed out at 300 s due to 21-min LLL; moved to background.
- Residual processes after backend crash inspected: none belonged to this solve
  (gateway/kernel/other-agent batch only; nothing killed).
- IntegerMatrix.dump/.load/.rows absent in this fpylll build → own CSV (save_mat/load_mat).


## Result — SOLVED, flag accepted (solved count 279→280 on cryptohack.org)
Flag (from own derivation; service-verified):
TSJ{who_needs_gaussian_elimination_when_you_have_LLL?_https://github.com/jonasnick/ecdsaPredictableNonce}

- d = 113469799004661487320247409448796883146298153010773207076143627146899378821364
  (recovered by LLL row scan on the v4 Kannan lattice; verified 6/6 r AND s with two
  independent EC implementations).
- Second, independent twist: the flag ciphertext carries **no nonce** — the generator's
  pycryptodome (≥3.21 behavior, reproduced locally on 3.24.0) does NOT prepend the random
  8-byte CTR nonce. Recovered the nonce by KPA: ks0 = 'Congrats! This i' ⊕ ct[:16], then
  AES-ECB-decrypt under key → counter block b78f8ad1071b1e3f‖0⁸ → full decrypt.
  (8 zero bytes under a wrong key would be a 2^-64 coincidence — decisive diagnostic.)
- Full reproducible pipeline: `solve5.py` (loads cached LLL basis b262v4.txt; recompute by
  deleting it) → d → solve.decrypt() incl. KPA-nonce path.

## Learning points
1. r/s verification is blind to k→k±q and to wrong *bit patterns* of the same integer;
   always verify the s-equation too, and treat decimal-string keys as a separate secret.
2. uSVP needs the SHORTNESS to live in the lattice coordinates (Kannan embedding of the
   bit vector), not in a CVP target inside a kernel lattice — v1/v2 geometry was hopeless.
3. On this fpylll build: Enumeration hard-caps at dim ≤255; LLL on a Kannanized lattice
   is ~20x faster (39s vs 21min) than on the [M;qI] kernel basis; snapshot bases to disk
   (IntegerMatrix has no dump() here) — crashes after a 20-min LLL burned ~40 min.
4. When decryption yields garbage under all layouts, inverse-AES the known-plaintext block
   to read out the counter block directly — it exposed the missing nonce instantly.
5. pycryptodome changed CTR auto-nonce semantics across versions (prepend vs drop); a
   generator's version matters and is recoverable via KPA, not just guessing.


## Session-2 analysis: why the CVP pipeline can't work (v2 abandoned)
Empirically reproducible: kernel-basis LLL + babai leaves 250 exactly-binary coords and 6
non-binary; none of the 64 flips verify even with the k-reduction bug FIXED. Root cause:
solve.py's lattice rowspan([M; qI]) ⊂ Z^256 drops the tracking coordinates, so the binary
constraint is not encoded as SHORTNESS. In the CVP-on-K view the true d sits at distance
~sqrt(6)·q/2 while λ1(K)~250 — the ball around the target contains ~2^63000 junk lattice
points; no amount of BKZ or exact enumeration returns the binary one. Kannan-LLL scan
confirmed empirically (no usable rows).

## v3 correct construction (solve3.py, running)
L = { (M·a + q·u, −a) } ⊂ Z^{262}, det q^6 (GH ≈ 230). Because M·d ≡ v mod q exactly,
the true bits d appear as lattice vector (0⁶, −d) of norm √128 ≈ 11.3 — a unique-SVP with
~20× gap. Attack: LLL → BKZ20 → BKZ30 → BKZ40, after each stage scan all rows whose first
6 coords are 0 and last 256 are 0/−1, EC-verify via try_candidate. Basis cached to
b262.dump so restarts skip the ~21-min LLL. Verification is self-authenticating
(6 EC r-checks + AES "Congrats" plaintext), so no sim round-trip needed.

## Vulnerability (plain words)
ECDSA on secp256k1 where the nonce is k = d XOR z (the private key XOR the message hash). XOR equals addition minus twice the bitwise AND, so the nonce equation s·k ≡ z + r·d collapses to ONE linear equation mod q in the 256 unknown *bits* of the private key: Σ_j 2^j·d_j·((s−r) − 2s·z_j) ≡ (1−s)·z. With 6 signatures the expected number of binary solutions is 2^(256−4·256) ≈ 0 — uniqueness is free; the whole job is pulling the binary vector out with lattice reduction.

## How the answer follows
1. Build the 6 equations from output.txt's (z,r,s) triples; model validated on simulated signatures (true bits satisfy M·bits = v exactly).
2. Correct geometry: lattice L = {(M·a + q·u, −a)} ⊂ Z^262 (Kannan-style, det q^6, GH ≈ 230). Since M·d ≡ v mod q exactly, the true bits appear as the lattice vector (0⁶, −d) of norm ≈ √128 ≈ 11.3 — unique-SVP with a ~20× gap; the binary constraint lives in the SHORTNESS.
3. Ladder LLL → BKZ-20/30/40, after every stage scan all rows with first 6 coords 0 and last 256 coords in {0,−1}, EC-verify candidates. d came from the LLL row scan of the v4 lattice (113469…1364).
4. Verify: 6/6 r AND s with two independent EC implementations — r checked with the UNREDUCED k = d XOR z (challenge.py multiplies G unreduced; the original verifier bug that rejected the true d). Then AES-CTR under sha256(str(d))[:16]; the ciphertext carries no nonce (pycryptodome ≥3.21 semantics) — recovered by KPA: ks0 = 'Congrats! This i' ⊕ ct[:16], AES-ECB-decrypt → counter block b78f8ad1071b1e3f‖0⁸ → flag.
5. Repro: solve5.py (cached LLL basis b262v4.txt) end-to-end; flag accepted (solved 279→280).

## Limitations / attempts that failed
- v1/v2 CVP-on-kernel-lattice was structurally hopeless: rowspan([M;qI]) drops the tracking coordinates, so binarity is not shortness; the target ball holds ~2^63000 junk points and the 64-flip repair loop can't succeed (proven empirically, then abandoned).
- The k→k mod q verification bug made the correct candidate look wrong and escalated the earlier run needlessly to BKZ.
- fpylll exact enumeration hard-caps at dim ≤255 → radius-enum unusable at 263; kernel-basis LLL cost 21 min vs 39 s Kannanized; IntegerMatrix has no dump() in this build → own CSV snapshotting.

## Sources
Provided challenge.py + output.txt only. The GitHub URL inside the recovered flag string (jonasnick/ecdsaPredictableNonce) is a flag payload reference, not a consulted solution artifact; per the run logs nothing there was read as a writeup. Lattice modeling derived in-session (uSVP/Kannan embedding); pycryptodome CTR auto-nonce behavior reproduced locally on 3.24. No CryptoHack solutions pages consulted.
