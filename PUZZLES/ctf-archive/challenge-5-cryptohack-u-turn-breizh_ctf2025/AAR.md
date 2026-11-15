# AAR — u-turn-breizh_ctf2025 (Breizh CTF 2025 "U-turn")

## Vulnerability
The "hash" is linear over Z/256 on balanced-quinary digits: h = A*x mod 256 with
x_i ∈ {-2,-1,0,1,2} (l=50), A public (48x50). Finding a second preimage = finding
the unique small-coordinate point in a coset of the lattice
L = {(x,y) ∈ Z^98 : second block = A*x + 256y} near target (0, h).
Lattice params: det = 256^48 = 2^384, n=98 → GH ≈ 36; true distance ‖x‖ ≤ √(50·4) ≈ 14.1
→ unique-CVP regime.

## Attack
1. Build basis rows [e_i | A_col_i], [0 | 256 e_j]; target t = (0^50 | h).
2. fpylll BKZ-40 (auto-abort) + CVP (closest_vector).  [RESULT PENDING — see run3.log]
3. Digits → val = Σ x_i 5^i; truncation lost high digits, so out = val + c·5^50,
   c < 2^128/5^50 ≈ 4100 candidates.
4. Undo PKCS7 XOR-fold using known structure flag = BZHCTF{hex16} (24 chars →
   2 blocks, b2 tail = hex[9:16]+"}"+0x08×8): recover 16 hex chars; verify hash(flag)==h.

## Notes / pitfalls hit
- fpylll 0.6.4 API churn: LLL.lll / M.lll gone; use fpylll.algorithms.bkz2.BKZReduction
  (.lll_obj(), __call__(BKZ.Param(block_size=..., max_time=...))); CVP.closest_vector has
  no max_nodes kwarg. Plain LLL+Babai insufficient in the 98-dim projection formulation
  (run2.log: babai ok: False); BKZ-40 ~200s; CVP enumeration there did not finish <30min.
- This host's gp64 (PARI 2.17.4 minimal build) LACKS matinv, vecconcat, vecabs, mathide,
  calle (use matadjoint/matdet, matid...). GP matrix literals need ';' row sep WITHOUT
  inner brackets; Mat(list-of-vectors) treats vectors as COLUMNS.
- sympy: Matrix.rows()/rows are property vs row(i) method confusion; hermite_normal_form
  rejects rank-deficient input; sequential .rank() loops explode (coefficient blowup).
- Hensel bit-lifting to get a particular solution xp mod 256 works (rank(A mod 2)=47,
  3 free vars/level; only ~33k partials at level 6, first consistent lift gives xp).
- Reformulation used (plan E): R = rowspace([A;256I]) ⊂ Z^50; since 256Z^50 ⊆ R,
  L = {x : Ax≡0 mod256} = rowspace(256·R^{-1}) EXACTLY (integral basis).
  det L = |im(A mod 256)| ≈ 2^384 → det^(1/50) ≈ 205, GH ≈ 350 vs true ‖x‖≈10-14:
  unique-CVP with huge margin → Babai on LLL-reduced 50-dim basis expected to hit.
- x digits then recover out = Σ x_i 5^i + c·5^50 (c < 2^128/5^50), undo known-plaintext
  PKCS7 XOR-fold of BZHCTF{...} 24-char flag; verify hash(flag)==h.

## Outcome — SOLVED
FLAG: [flag — recorded in FLAGS/ctf-archive/challenge-5-cryptohack-u-turn-breizh_ctf2025/flag.txt] (derived offline; hash(flag)==h verified; accepted by site,
solved count 286→287). Final script: solve_j.py; log: runJ.log; flag: flag_u-turn-breizh_ctf2025.txt.
Kannan embedding (W=3, BKZ-60, 51-dim, seconds) gave W·x_true at norm² 810/9=90 (unique in box);
c·5^50 completion scan (c<3831) + known-plaintext decode + hash check → exactly 1 candidate.

## Root cause of the decode failure (the "broken glue")
chal.sage does `FLAG = FLAG.strip("BZHCTF{}")` — strip() removes a CHARACTER SET, so the
hashed message is the BARE 16-hex-char string (exactly one block) → PKCS7 appends a FULL
0x10 block → fold = hx ^ 0x10×16. All earlier attempts assumed the 24-char "BZHCTF{...}"
string was hashed (→ 0x08 tail, mixed XOR structure) — that's why the c-scan found 0 hits
while the lattice part was correct all along. Caught by fuzzing the decode against
deterministic ground truth (glue_test.py / inline tests), per brief's glue rule.

## Limitations
- Plain LLL+Babai and 98-dim CVP enumeration failed earlier (run2/runH logs); the
  50-dim kernel reformulation + Kannan embedding was what worked.
- Hensel particular-solution xp (xp.json) was a prerequisite from an earlier session, not re-derived here.

## Sources
Provided materials only; AAR records an in-campaign earlier-session prerequisite. Disclosure wording preserved verbatim:
> Hensel particular-solution xp (xp.json) was a prerequisite from an earlier session, not re-derived here.
