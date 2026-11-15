---
name: ctf-lattices
category: ctf
description: "CryptoHack lattice/PQ: fpylll LLL/BKZ/SVP/CVP on Windows."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, cryptohack, lattice, lwe, lll, bkz, svp, cvp, fpylll, gmp, post-quantum, knapsack, babai]
    related_skills: [ctf-answer-challenges, ctf-practice-runs, ctf-crypto-attacks, ctf-isogenies]
---

# CryptoHack Lattices & Post-Quantum — fpylll on Windows/MinGW

## When to Use
Any CryptoHack **Post-Quantum / lattice** challenge: `vectors`, `lattices`, `gauss`,
`find`, `backpack`, `toomany`, and the 9 `lwe-*` challenges
(`lwe-background`, `lwe-intro`, `lwe-high-bits`, `lwe-low-bits`, `lwe-private-public`,
`lwe-lsb-regev`, `lwe-bounded_noise`, `lwe-nativity`, `lwe-missing-modulus`, `lwe-noise-cheap`).
Also any challenge whose solution reduces to a shortest/nearest vector or an integer
knapsack. Most are **answer-type**: compute an integer or a vector, submit the bare
value (see `ctf-answer-challenges` for the wrapper rule). `lwe-background`/`lwe-intro`
are often conceptual (answer-type, no lattice needed) — read the prompt first.

## Solved so far (2026-10-13) — do NOT re-solve
`lwe-high-bits` (15) → 201 (toy LWE: x=(b−⟨A,S⟩) mod q NON-centered, m=round(x/Δ)),
`lwe-low-bits` (20) → 147 (CENTERED x mod p), `lwe-private-public` (25) → 1568 (Kyber1024 pubkey bytes),
`lwe-lsb-regev` (40) → crypto{linear_algebra_is_useful} (noise-free socket: 64 zero-encryptions →
Gauss-Jordan over GF(q) recovers FIXED S; then m=(b−⟨A,S⟩) mod q per flag char),
`gauss` (50) → 7410790865146821 (2D Gauss reduction of v=(846835985,9834798552), u=(87502093,123094980);
flag = inner product of optimal basis), `lwe-bounded_noise` (60) →
crypto{linearised_polynomials_for_bounded_errors} (binary-noise LWE, secret=flag as base-q digits,
n=25, m=625: take 25 pivot rows, s = s0 − A_I⁻¹e_I parameterized by 25 binary error bits, prune
2²⁵→~10² with ONE extra row via incremental Gray-code, full verify. LLL+Babai/CVP on the
[A^T|0]/[0..q] lattice FAILED here — that construction is wrong for mod-q LWE).

## THE tool: fpylll 0.6.4 on Windows/MinGW (build verified 2026-10-13)
fpylll wraps FPLLL (LLL/BKZ/SVP/CVP/GSO) over GMP+MPFR. On a fresh machine it is usually
the long-blocking prerequisite (pip wheels fail on Windows/MinGW — see build chain below).
Verified with a fresh interpreter — all return correct values:
```python
import fpylll                                   # 0.6.4
from fpylll import IntegerMatrix
from fpylll.fplll.lll        import lll_reduction
from fpylll.fplll.bkz        import bkz_reduction
from fpylll.fplll.bkz_param  import BKZParam
from fpylll.fplll.svpcvp     import shortest_vector, closest_vector, babai

B = IntegerMatrix(n, n)      # basis vectors as ROWS: B[i] is the i-th basis vector
B[i, j] = ...                # 0-indexed, B[row, col]
r = lll_reduction(B)         # -> reduced IntegerMatrix (rows)
b = bkz_reduction(B, BKZParam(14))        # block size 14
sv = shortest_vector(B, "proved")         # method is a STRING: "proved" or "fast"
cv = closest_vector(B, [t0, t1, ...], "proved")   # target as a Python list of ints
bb = babai(B, [t0, t1, ...])             # fast nearest-plane (no proof guarantee)
```
Run with the interpreter that has fpylll installed (on the campaign host: the crypto-ctf
venv Python 3.12 — exact path in `windows-crypto-toolchain`; NOT the system python).

## CRITICAL API signatures (do NOT guess — these cost real time)
- **`IntegerMatrix` construction**: `IntegerMatrix.from_iterable(nrows, ncols, flat_list)` is the
  only reliable ctor. `IntegerMatrix(list_of_rows)` raises `TypeError: Parameters arg0 and arg1
  not understood`. No `.num_rows`/`.num_cols` — use `.nrows`/`.ncols`. Element access `B[i,j]`
  works; rows via `B[i]`.
- **`closest_vector(B, target_list, "proved")` returns a FLAT vector** (index `w[i]`), NOT a
  1-row matrix (`w[0][i]` raises `TypeError: 'int' object is not subscriptable`).
- **CVP pitfall**: the textbook lattice `[A^T_i|0] + [0..0|q]` with target `(b,0)` only encodes
  the EXACT (noise-free) relation. For mod-q LWE it returns garbage (error coords ~q/2). For
  small-noise mod-q LWE, parameterize + enumerate + verify instead (see solved list above).

## CRITICAL API signatures (do NOT guess — these cost real time)
- **`lll_reduction(M)`** is the module function in `fpylll.fplll.lll`. There is NO
  `IntegerMatrix.lll()` method and no top-level `fpylll.lll` function in 0.6.4.
- **`bkz_reduction(B, o)`** where `o` MUST be a `BKZParam`. Build it as
  `BKZParam(block_size)` (e.g. `BKZParam(14)`). Passing an int `14` raises
  `TypeError: Argument 'o' has incorrect type (expected BKZParam, got int)`.
  `BKZ().reduction(...)` also exists but the module fn is simpler.
- **`shortest_vector(B, method="fast")`** / **`closest_vector(B, target, method)`**
  take a **string method** (`"proved"` or `"fast"`), NOT an int. `shortest_vector(B, 1)`
  raises `ValueError: Method '1' unknown`. Use `"proved"` when you need a guaranteed
  shortest vector (needed to trust an answer before submitting).
- `closest_vector(B, target_list, "proved")` target is a **list of Python ints**.
- A rank-1 lattice (`IntegerMatrix(1, d)`) is a degenerate case: SVP returns the
  generator, CVP can error. Test CVP on a rank >= 2 basis.

## THE Windows runtime gotcha (the #1 failure mode — learned 2026-10-13)
The fpylll `.pyd` files link against MinGW runtime DLLs, but **Windows does NOT search
a `.pyd`'s own directory** for its runtime deps. A bare
`import fpylll` dies with `OSError: ... [WinError 126]` (missing `libstdc++-6.dll`).
Two things make it work (both already applied to the installed package):
1. **Copy the MinGW runtime DLLs into the fpylll package dir**
   `venv/Lib/site-packages/fpylll/`: `libstdc++-6.dll`, `libgcc_s_seh-1.dll`,
   `libmcfgthread-2.dll` (the transitive dep — easy to forget, this winlibs build is the
   "mcf" variant), `libwinpthread-1.dll`, `python312.dll`. Source: the MinGW toolchain's
   `bin/` dir and the CPython install dir.
2. **`fpylll/__init__.py` must call `os.add_dll_directory()`** on the package dir + the
   venv Scripts dir BEFORE the C-extension import. (Already patched.)
If you ever rebuild or the import breaks again: re-copy those DLLs and confirm the
`__init__.py` `add_dll_directory` block is present.

## THE Windows build chain (only if you must rebuild fpylll from source)
Use a dedicated build dir. Chain order:
**GMP 6.3.0 -> MPFR 4.2.1 -> FPLLL 5.5.0 -> fpylll 0.6.4**, all compiled with
MinGW (winlibs) into `<build>/prefix/` (libgmp.a, libmpfr.a, libfplll.a all present).
Non-obvious requirements (each is a trap):
- **GMP MUST be configured with `--disable-assembly`.** The MinGW `.asm` (nasm) path is
  broken here: it produced an empty 8-byte `libgmp.a` (libtool convenience-archive step
  hit a BFD `cache.c` internal error; objects were fine, the `ar` repacking failed).
  Pure-C GMP emits all 196 `mpn` functions. (The `__gmpn_*` symbols are internal/static
  in GMP 6.3 — a missing-symbol grep on `libgmp.a` is NOT a reliable health check; the
  real proof is that fpylll imports and LLL works.)
- **PATH prefix** for every build step (git-bash): `export MSYS_NO_PATHCONV=1
  MSYS2_ARG_CONV_EXCL='*'`; put a `fakebin` dir FIRST on PATH, then the winlibs `bin`.
  `fakebin` holds pathfix shims (ar.exe/ranlib/m4/cc/g++/make) so MSYS path
  translation doesn't corrupt the toolchain's own args (shim source: `windows-crypto-toolchain`).
- Build fpylll with a custom build script that patches the MinGW compiler into sysconfig
  (sets CC/CXX + prefix; Cython 3.3.0). The `.pyx` compile is the slow step.
- Native tools (git/rg/nm/objdump) do NOT accept MSYS `/c/...` paths when auto-conv is
  disabled — pass `C:/...` forward-slash native paths to them.

### fpylll build errors hit (2026-10-13) + fixes — only if rebuilding from source
The installed site-packages fpylll already works; these only matter if you re-run
the custom build script. Three distinct failures, each with a real fix:
- **`'M_LN2' was not declared`** (fplll `nr/dpe.h:706`). MinGW does NOT define the
  `M_*` math constants by default in C++. Add **`-D_GNU_SOURCE`** to fpylll's CXXFLAGS
  (the .pyx compile that includes fplll headers).
- **`undefined reference to mpfr_init`** (linking the `.pyd`). Library **link order** is
  wrong: dependents must come first. Correct order is **`-lfplll -lmpfr -lgmp`** (fplll
  uses mpfr, mpfr uses gmp). A line with `-lgmp -lmpfr -lfplll` fails.
- **`undefined reference to WinMain`**. The target is being linked as a **console exe**,
  not a DLL. The build must emit a shared `.pyd` (`-shared`), not an exe — this is a
  build-script entry-point/`-shared` flag bug.
- **`Compiler.link_shared_object() got an unexpected keyword argument 'extra_objects'`**
  and **`MinGW.link_shared_object() missing 1 required positional argument:
  'output_filename'`** — both are custom-`MinGW`-wrapper signature mismatches vs the
  installed setuptools' `build_ext` calling convention (it passes `extra_objects=` and
  positional args the wrapper doesn't declare). Fix in `fpylll_build_win.py`: make the
  wrapper's `link_shared_object` accept the full setuptools signature
  (`objects, output_filename, output_dir, libraries, ... , extra_objects=None, **kw`)
  and forward appropriately. (The final working build fixed these.)
- **Verifying a freshly built source tree (not the installed pkg):** the source
  `fpylll/__init__.py` is NOT the patched one, so a bare `import fpylll` from the source
  tree fails with `WinError 126`. Pre-load the DLL dirs first:
  `os.add_dll_directory(...site-packages/fpylll)` (holds the MinGW runtime DLLs) + the
  source-tree `src/fpylll` and `src/fpylll/fplll` dirs, and `sys.path.insert(0, src)`
  so the source build is imported. Then SVP/BKZ run normally.
- **`error: Microsoft Visual C++ 14.0 or greater is required`** — a MISLEADING error.
  It means the compiler selection fell through to distutils' default Windows path
  (`compiler_type == 'msvc'` → MSVC version probe → hard error) — the MinGW patch was
  NOT in effect for that run. Two observed triggers: (a) running bare `setup.py build_ext`
  (distutils ignores `CC`/`CXX` env vars on Windows entirely — can never work here), or
  (b) `fpylll_build_win.py` itself, when its compiler patch fails to apply (setuptools
  version drift, stale state). Diagnose by grepping the log's compile lines: if they show
  `winlibs\mingw64\bin\g++.exe` the patch worked; if you see the MSVC probe or a bare
  `cl.exe` path, the patch missed. Do NOT install MSVC Build Tools as a "fix" — the
  MinGW path is the one that works.

## The solved intro block (2026-10-12) — do NOT re-solve
`vectors` (10) → 702, `basis` (15) → 9, `gramschmidt` (30) → 0.91611 (5 sig figs),
`lattices` (40) → 255 (|det| of the 3x3 basis, `isogeny_answers.py`), `lwe-background` (5)
→ `Oded Regev`, `lwe-intro` (10) → `Gaussian elimination`. All BARE answer-type (no wrapper).
What remains in Post-Quantum: `lwe-high-bits` (15), `gauss` (25), `lwe-private-public` (25),
`lwe-lsb-regev` (50), `lwe-bounded_noise` (75), `lwe-nativity` (80), `lwe-missing-modulus` (90),
`lwe-noise-cheap` (100), `backpack` (100), `toomany` (120), `find` (10) — the real
LWE/knapsack attacks (recipes below).

## Hidden-number-in-sum-of-sqrt (eisenstein, 150, SOLVED 2026-10-20)
h = Σ ord(c_i)·√p_i over distinct primes, ct = floor(h·2^256) — recover chars. CVP in the
rank-m lattice {(z, Σz_j·round(S√p_j))} via KANNAN EMBEDDING (rows (e_j,v_j,0) + (0,w,D'))
+ fpylll lll_reduction — LLL alone suffices (gap ~2^20). TWO pitfalls that cost hours:
(1) SCALING BALANCE: S must satisfy S·(interval width) ≲ |z| — S=2^340 for a 2^-256 interval
makes the last coord ~2^84 and the target stops being shortest; S=2^264 (width→16) works.
D' ≈ expected norm (2^85). sympy Babai via B⁻¹t rounding FAILS (huge coeffs) — use fpylll.
(2) VERIFY IN THE ORIGINAL ARITHMETIC: the challenge used Decimal prec=100, so ct is the
100-digit-ROUNDED value — exact mpfr recon is off by ±1 ulp and 'fails'. Re-run the provided
Decimal code with the candidate flag; that's the ground truth, not exact math.
Flag: crypto{r34l_t0_23D_m4p}. Read-off: reduced row with |last coord|=D' → z = −row[:m].

## Common CryptoHack lattice attack patterns
- **the `find` challenge / intro vector finds**: given a basis, find the shortest / a specific vector.: given a basis, find the shortest / a specific vector.
  `lll_reduction` then read off the answer; `shortest_vector(B, "proved")` for the
  guaranteed shortest. Often the answer is a component of the reduced basis.
- **`gauss` / `lwe-*` (LWE)**: the core LWE setup is `b = a·s + e (mod q)` over
  `s ∈ {0,1}` (or small). To recover a secret bit / the full secret, build a lattice
  whose short vectors encode the error `e`, then:
  1. `lll_reduction` (and/or `bkz_reduction(B, BKZParam(k))`) on the lattice basis.
  2. Recover `e` as the short-vector components; solve for `s`.
  - Low-noise / small-q cases: **Babai nearest-plane** (`babai(B, target)`) on an LLL-
    reduced basis is often enough and far cheaper than SVP/CVP "proved". Reach for
    `closest_vector(..., "proved")` only when Babai is wrong or the problem demands it.
  - `lwe-lsb-regev`: the least-significant bit of the secret; `lwe-high-bits`/`lwe-low-bits`
    expose partial secret bits — set up the lattice with the known bits fixed and solve
    for the rest.
  - `lwe-noise-cheap`: noise is small/structured — exploit the structure (e.g. a fixed or
    sparse `e`) before falling back to generic SVP.
  - `lwe-missing-modulus`: multiple ciphertexts mod different moduli — combine them
    (CRT-style) before the lattice step.
- **`backpack` (SOLVED 2026-10-24) → crypto{my_kn4ps4ck_1s_l1ghtw31ght}** — THE low-density
  knapsack recipe (9 prior tries failed on formulation, not tuning):
  (1) Mine known bits from the source (flag prefix/suffix + ASCII MSB=0) to cut n and push
      density n/log2(max a) below ~0.646 (272→182 unknowns took 0.72→0.48).
  (2) **HALF-INTEGER TARGET CVP**: rows `(2e_i, 2a_i)` (m×m+1), target `(1^m, 2t)` where
      `t = ct − Σ known-1-bits`. dist² = Σ(2x_i−1)² + (2(a·x−t))² is 182 (=m) for ANY 0/1
      exact solution and strictly larger otherwise → message is the UNIQUE closest point.
      LLL + `babai(B, T)` solved it in 3 s (no BKZ/CVP enum needed). Verify by recomputing ct.
  (3) WHY the obvious lattices FAIL: CLOS rows `(e_i, Wa_i)+(0,Wt)` contain kernel relations
      `(w,0)` SHORTER than the message (norm² 46 vs 91) → SVP/BKZ row-scan can never return
      the message. Target `1^m` (unscaled) is biased: `(x_i−1)²` rates x=0/2 like shifted 1s,
      so non-0/1 solutions beat the message. Min-‖x‖ on the solution coset is also wrong
      (⟨m,w⟩<0 shortens m+w). The objective must be ‖x−½‖, flat on {0,1}.
  `toomany` (120) likely same family — reuse solve10_halfcvp.py.
  knapsack solve.

## Popcount/MSP integer systems (Unfairhamming family; failproof_revenge-sekaictf202, NOT solved 2026-10-28)
c = popcount(A_j & m) with random padding: 256 eqs on 512 bits => unique 0/1 sol (≈4.3 bits/eq).
Pipeline that WORKS (toy-verified): PARI matsnf(A,1) kernel V-cols + qflll; particular m0=V*(U c/d);
Kannan rows (2K|0)+(T|23), T=1-2*m0; sol = row with |last|=23, norm2=n+529; v=(T+raw)/2 if last<0
else (T-raw)/2; m=m0+v. Reduce dim first (known prefix / ASCII-MSB / zero-padding columns).
BUT on this host the final step is solver-capped: gap ≈ λ1(2K)/32 ≈ 20 at dim 201-249.
Measured ceiling (fpylll 0.6.4 Win build): LLL 3.3e6 -> BKZ-15 4.3e5 (45s) -> BKZ-20 3.6e5 (131s)
vs target 985; BKZ-25+ >400s/stage; CVP.closest_vector('fast') hangs (Babai radius explosion);
raw Enumeration(0,n,986.0,0) after BKZ-20 >16min; SVP.shortest_vector(preprocess=0,pruning=True)
SEGFAULTS (EXIT=127). Don't burn budget: if uSVP gap>10 at dim>150, escalate tools (Sage BKZ-50)
or file evidenced-negative fast. GP-build traps: Mat(t_VEC)=ROW (column=Mat(v)~), MAT*t_VEC invalid,
no listincludes/vecnorm, Str(huge matrix) unusable (write per-row Str(Vec(row))).

## Unknown-modulus divisibility systems (ECLCG-hitcon_ctf2024 wall, evidenced-negative 2026-11-01)
Truncated/hidden-value LCG or ECDSA-with-LCG-nonces where p|F(x) for unknown prime p:
- **Vacuity test BEFORE any Groebner/F4 attempt**: if your "bounded MQ" model introduces
  cofactor vars (F_i = c_i·pp), the ideal ⟨F_i − c_i·pp⟩ ∩ k[originals] = {0} OVER ANY FIELD
  (set pp=1, c_i=F_i). Divisibility-by-unknown-p is integrality content, invisible to ideal
  membership — Groebner/F4/msolve can NEVER encode it; only Coppersmith-after-knowing-p can.
  These problems are Hidden-Common-Divisor families: no poly-time attack when cofactor dust
  (|F_i|/p) is ~sqrt(|F_i|)-sized.
- **gcd-of-minors primitive (works given the 1-parameter family)**: for LCG diffs
  D_i=x_{i+1}−x_i mod p, p | D_{i+1}D_{i−1}−D_i² and gcd over ≥3 minors == p exactly
  (machine-verified at 311-bit p). Exact side-identities: D_{i+1}=a·D_i−f_i·p and
  M_i = p·(f_{i−1}D_i − f_i·D_{i−1}) with f_i=⌊(a k_i+b)/p⌋−⌊(a k_{i−1}+b)/p⌋ — the
  cofactor is a cancellation residue, never zero. Hard part = recovering the affine
     parameter that lets you BUILD the D_i; truncation-bits and LCG-quotients are dual
     stores — reducing mod q moves, not removes, the unbounded unknowns.
  - **"Given d" resolution (planted-toy study 2026-11-05, nn=257, folder toy_nn257/ — do NOT
     re-test)**: given d you know only 17 base-q-truncated states (55 MSBs hidden), p,a,b secret.
     Measured outcomes at the real 311/256 ratio: (1) given (d,p,a,b) ALL 17 hidden digits are
     trivial — textbook known-modulus BDD, dim 18 Kannan+LLL, margin λ1/dist = +233 bits,
     wrong-param control rejects; the Stern/C-S DIGIT regime is not the wall. (2) p-first from
     the d-view alone fails three ways: no computable integer combination of the c_i is a
     p-multiple (best gcd 2^17 over 30k combos + Gram-LLL shortest combo ≈2^510 > p — vacuity,
     ~2^311 availability gap); linearized-minor CVP dim ≤40 (monomials ν,ν²,νν,gp over
     difference-digits) has 2^2473 spurious in-box points at full scale and the planted point
     sits +93 bits ABOVE λ1 (not short; +210 spurious bits per added equation — linearization
     cannot enforce rank-1 consistency); guess-and-gcd needs 4 full states = 2^224 brute
     (mechanism exact: 1/194481 hits at nano, zero false hits). ECLCG-family negatives stand;
     remaining open core is acquiring p, not the digits.
- **msolve 0.11.0 windows build is BROKEN**: prints `[-1]:` (unit ideal) for every input,
  incl. control ⟨x−2⟩ over F_p. Always run a known-answer control before trusting any
  CAS/F4 binary's negative result.

## Big-dim NTRU key recovery: engine ladder + block-size math (Origami/NNS-2025, dim 1024, 2026-11-03)
- **Block-size math BEFORE burning time**: uSVP gap g = λ2/λ1 (here GH≈87 vs ‖(f,g)‖≈8.4 ⇒ g≈10.4)
  ⇒ core-SVP dim ≈55-60 ⇒ BKZ with β<~55 finds the secret in NEVER, any number of hours
  (explains 40h mpfr BKZ-20/25/30/45 producing a perfectly flat profile). Compute d_core(g,δ0(β))
  first; pick β ≈ d_core+5.
- **In-process fpylll on Windows dies at dim 1024 for EVERY float_type** (d/ld/mpfr): hard process
  kill, exit 127, no catchable exception. The working engine is the **fplll CLI out-of-process**
  (prefix2 mpfr/longdouble; prefix3 adds dd).
- **QD double-double build (fplll `-f dd`, ~10x faster than mpfr-200 at big dim)**: MSYS2 gcc-16
  in C++11 mode REJECTS hex-float literals with signed exponents (`0x1p+53`, `0x1p-53` = "exponent
  has no digits") — this silently killed QD 2.3.24 configure. Fix: sed `0x1p+`→`0x1p`, `0x1p-53`→
  `1.1102230246251565404236316680908203125e-16` in dd_inline.h/td_inline.h. Also: `make -C src &&
  make src/.libs/libqd.a` then hand-copy lib+headers (top-level `make install` dies on missing
  latex); delete any stale `<prefix>/include/qd` that shadows fresh headers; PATH must have
  `msys64/ucrt64/bin` FIRST. fplll configure then needs `--with-qd=<qd-prefix>`; verify
  `#define FPLLL_WITH_QD 1` in config.h AND `-f dd` on a toy ("Compiled without support for BKZ
  reduction with dd" = stale-object lie: use `make clean` after reconfigure, deps are untracked).
- **fplll CLI quirks**: `-bkzmaxtime` hit exits **rc=7 but stdout STILL has the reduced basis** —
  chain gate must be "output row-count in file", never `rc==0` — `-bkzmaxloops N` likewise
  exits rc=8 with a fully valid stdout basis. `-bkzdumpgso` SEGFAULTS (rc=139) with
  `-f dd` at dim 1024 (dim-128 toy fine) — omit dumpgso, use per-slice basis scan as heartbeat.
  Chain pattern: `fplll -a bkz -b K -nolll -f dd -bkzmaxtime SLICE < cur.fplll > next.fplll`,
  mv next→cur, scan, repeat 24x — survives crashes/timeouts, resumable. Escalation
  scheduling from measured dim-512 dd tour costs: beta40 ~30 s/tour, beta50 ~3 min,
  beta60 ~13 min, beta70+ 40 min–2 h under contention.
- **GS profiling + progress metric on dd chains**: classical longdouble GS drifts on
  deeply dd-reduced bases — profile with exact Bareiss minors. Min-row norm pins at q²
  (q-rows); the progress metric is best NON-q-row norm, never the raw min.
- **Validate the DECRYPT half on a planted toy FIRST** (toy_decrypt_check pattern): planted NTRU
  lattice (row-found gate) + planted-message encrypt/decrypt roundtrip through the exact solver
  code. Both gates passed for Origami while the real dim-1024 β60 dd chain grinds — that way a
  hit on the real lattice cannot fail on a silly downstream bug (message bit-width overflow in a
  ring of n coefficients was one real catch).

## Flag format (per `ctf-answer-challenges`)
- "Find the shortest vector" → submit its **coordinates** (check the prompt for the exact
  format: space/comma separated, or a single component). Confirm with `shortest_vector
  (B, "proved")` so the answer is provably shortest before submitting.
- LWE "what is the secret bit / flag is the secret" → submit the recovered bit/vector as
  the prompt asks (often a bare int or a comma list).
- Run the reduced-basis / SVP result through a second independent check (e.g. verify the
  vector is actually in the lattice and has the expected norm) before submitting.

## Pitfalls
- **fpylll BKZ "instant convergence / plateau" = AUTO_ABORT artifact.** `BKZ.EasyParam` sets flags=32 (AUTO_ABORT, (scale=1.0, max_no_dec=5)): a tour ABORTS after ~5 non-improving blocks, so dim-249 "tours" return in 5-50s having touched ~6 of 205 blocks — plateau data from EasyParam defaults is worthless. Disable by XOR: `BKZ.EasyParam(beta, delta=0.99, flags=BKZ.AUTO_ABORT)` (flags 32->0; Param attrs are read-only). Honest no-abort result on the failproof_revenge dim-249 coset lattice (run#4, 2026-11-01): BKZ-35/45 'd' flat-to-DECAYING profile (min||b*||^2 30->10, no spread gain over 8x240s tours) and honest B45 tours SILENTLY KILL the process (~16-25 min, no traceback); mpfr precision must be >= log2(max entry) (~1188 there) and even mpfr-1400 buys zero flattening. Oracle-class dead end on that build — escalate engine, don't add time.
- **High-dim BKZ/enumeration HARD-KILLED mid-run = wrong float backend, not OOM or slow.**
  On ill-conditioned lattices (dim ~700+), fpylll's `d` (auto default) and `dpe` float
  backends silently terminate the process inside enumeration (~60–120 s in, no traceback,
  no Windows error-report event). `float_type='mpfr', precision=200` survives the same
  BKZ-20 slice; dims ≤ 512 are fine with defaults. Control test before hunting for
  memory/wall-clock culprits: run the identical pipeline at a smaller dim — if it works,
  the killer is the float backend. Exit code 127 through bash is NON-DIAGNOSTIC (clean
  fplll errors surface as 127 too). mpfr is ~10x slower — budget slices accordingly and
  checkpoint between them.
- **fpylll 0.6.4 API gaps:** `IntegerMatrix` has no `.dump` / `.rows` (serialize manually);
  raw `Enumeration` is HARD-CAPPED at dim 255 — above that, route through
  Kannan-embedding + LLL/BKZ row-scan instead of CVP enumeration.
- **`OSError WinError 126` on `import fpylll`** = the Windows DLL-dir gotcha. Re-copy
  the MinGW DLLs (esp. `libmcfgthread-2.dll`) + confirm `add_dll_directory` in `__init__.py`.
- **`TypeError ... expected BKZParam, got int`** = pass `BKZParam(block_size)`, not an int.
- **`ValueError: Method '1' unknown`** = SVP/CVP method is the string `"proved"`/`"fast"`, not 1.
- **`lll_reduction` is a module function** in `fpylll.fplll.lll`, not a method. Top-level
  `LLL.reduction(M)` / `BKZ.reduction(M, BKZParam)` class attributes also work in 0.6.4
  (bare `LLL(M)` raises `TypeError: LLL() takes no arguments`).
- **Exact Gram determinant (Bareiss) is det(Λ)²** — halve log2 before using it as
  log2 det(Λ), else every λ1/margin estimate is inflated 2x (caught by sanity: λ1 must
  exceed no vector in the basis you fed in).
- Don't use the system `python`; use the fpylll-installed venv interpreter
  (`windows-crypto-toolchain` has the host path).
- Don't grep `libgmp.a` for `__gmpn_lshift` as a health check — GMP 6.3 keeps those
  internal; the real proof is a working `import fpylll` + a correct LLL result.
- `lwe-background`/`lwe-intro` may be conceptual (no lattice math) — read the prompt
  before reaching for fpylll.

## Canonical references (owner list 2026-11-02)

[R18] Lenstra-Lenstra-Lovasz, 'Factoring polynomials with rational coefficients', Math. Ann. 261, 1982 (LLL). https://link.springer.com/article/10.1007/BF01457454 | [R19] Kannan, 'Minkowski's Convex Body Theorem and Integer Programming', Math. Oper. Res. 12(3), 1987 (BKZ generalization + MSP). https://pubsonline.informs.org/doi/10.1287/moor.12.3.415 | [R20] fpylll docs https://fpylll.readthedocs.io/ | [R36] Cyclotomic polynomial https://en.wikipedia.org/wiki/Cyclotomic_polynomial (power-of-two rings for ring-LWE/NTT) | [R23] see ctf-lcg skill for FHKLs. | [R43] Joux-Stern 'Lattice Reduction: A Toolbox for the Cryptanalyst', J. Cryptology 1998 — LLL bound |b1|<=2^((n-1)/2)det(L)^(1/n); Stern truncated-LCG route: recover deg O(sqrt(log m)) poly P with P(a)=0 mod m => recover modulus m, then a. https://link.springer.com/article/10.1007/s001459900042 | [R44] uSVP cost refinement https://hal.science/hal-02886638v1/file/uSVP.pdf ; uSVP<->BDD equivalence https://cseweb.ucsd.edu/~vlyubash/papers/uSVP-BDD.pdf (block-size pricing for target-norm attacks).

## fplll runtime-budget pitfall (measured 2026-11-06)
- `-bkzmaxtime` is ROUND-granular, not wall-clock: dim-1024 BKZ-60 deep-deletion kept
  running 23.4 CPU-h against a 43200 s limit (single enumeration exceeds it). Never use
  it as a hard cap; use an external deadline + kill, and KNOW fplll prints no partial
  basis on external kill (SIGINT-save not injectable from a detached Windows console).
