# AAR — unevaluated-tetctf2021 (TETCTF 2021, CryptoHack ctf-archive)

## Challenge
"Complex Diffie-Hellman": group = units of Z[i]/(p^2), p 128-bit prime, p≡3 mod 4.
Given g, order = p*q*r (q=(p-1)/2, r=(p+1)/12, both prime; p=2q+1 safe prime), n=p^2,
pub = g^k mod n with k = 32 random bytes, and AES-ECB(flag) under key = k bytes.
Solve DLP to get k exactly.

## Attack (derived from source, first principles)
1. n is a perfect square → p = isqrt(n). Verified p*q*r == order, p≡11 mod 12 branch.
2. Group structure: (Z/p^2)[i]* ≅ μ_{p^2-1} × (1 + p·F_{p^2}). The p-Sylow
   {1+p·u} is additive F_{p^2}: (1+pu)(1+pv)=1+p(u+v), so the p-part DLP is a LINEAR
   equation: X = pk^(order/p) = 1+p·k·u_g  ⇒  k0 = k mod p = u_X·u_g^{-1} in F_p[i].
   DONE, verified (check True in solve1.py output).
3. T = pk·g^{-k0} = g^{p·c1}, c1 = (k-k0)/p < 2^256/p ≈ 2^128.6.
4. T^r = (g^{p r})^{c1}: both sides are Teichmüller lifts of F_p elements (im≡0 mod p),
   so the DLP reduces to F_p^*: base a = (g^{p r} mod p) real, target = T^r mod p real.
   This gives c1 mod q. One 128-bit prime-field DLP (safe prime p-1=2q) — subexponential
   NFS territory, generic (rho/BSGS ≈ 2^63.5) is infeasible.
5. After c1 mod q: c1 = (c1 mod q) + q·t with t ∈ {0..5} (c1max/q ≈ 5.45). Enumerate,
   k = k0 + p·c1, AES-ECB decrypt, keep plaintext matching flag/padding (solve_final.py).
   (The r-subgroup DLP is NOT needed — the 256-bit bound on k + q-part pins k.)

## Key numbers
p = 3.4e38 (128 bits), q=(p-1)/2, r=(p+1)/12 both prime; order 378 bits.
k0 (k mod p) = computed, 127 bits, verified u_X = k0·u_g in F_p[i].
q-DLP instance: p = 340347... (see solve1 output), base a = g^{p r} mod p = 163720576515724884349491368582227595136, target = 3321385147483577619458640425416114852.

## Toolchain plan for the 128-bit NFS-DLP
No WSL/docker/msys2/cygwin on host; yafu 1.34.5 (2013) has no prime-field NFS-dlog.
Plan: portable MSYS2 (fork-emu) + CADO-NFS dlp mode (prime field, --dlp -t target p).

## Toolchain saga for the 128-bit NFS-DLP (documented for AAR)
- No WSL (not installed, WSL1 unsupported), no docker, no msys2/cygwin initially, no sage (conda solve failed per tools/sage_install.log).
- yafu 1.34.5 (2013, latest official SF binary): no prime-field NFS-dlog → unusable.
- Portable MSYS2 (2026-09-27 sfx) installed at ~/tools/msys64.
  - pacman python lacks flask/requests (pip wheel-install is broken in msys pip:
    'pip._internal.operations.install.wheel' missing) → pure wheels fetched straight
    from PyPI JSON API and zipfile-extracted into site-packages; gmpy2 built from
    sdist via `pip wheel` + manual extraction; mpfr-devel + mpc-devel needed.
  - CADO-NFS master build fixes needed on msys: CXXFLAGS="-fpermissive -D_GNU_SOURCE"
    (mp_limb_t = unsigned long long vs C++ unsigned long strictness; asprintf),
    and one-line patch linalg/bwc/flint-fft/mpn_extras.h prototype
    mp_bitcnt_t -> flint_bitcnt_t (flint shim ulong alias).
- CADO DLP invocation: cado-nfs.py -dlp -ell q target=tgt,base p (logs in arbitrary
  base; c1 = Lt * La^{-1} mod q), see run_dlp.sh.

## Status
IN PROGRESS — CADO building on MSYS2; reduction chain fully validated E2E on small
params (test_e2e.py: "k0 ok", "c1q check: True").

## RUN 2026-11-02 (final DLP step)
- Live service: N/A — site.md/statement confirm OFFLINE instance (static output.txt
  + source.py only, no listener). Archived output.txt IS the authoritative input.
- CADO build state found: build/WORKSTATION CMake dir configured WITH documented
  fixes (CXXFLAGS="-fpermissive -D_GNU_SOURCE -Wno-format"; flint-fft patch already
  applied — no mp_bitcnt_t left), 285 .o present but bin/ empty (link never ran).
  Resumed `cmake --build . -j2` (host-load rule: 2 threads), log ~/cado_build.log.
- DLP instance (validated chain, run_dlp.sh): p=206109322179011817882783419945552366363,
  ell=q=103054661089505908941391709972776183181, target=3321385147483577619458640425416114852,
  base=163720576515724884349491368582227595136; c1 = Lt*La^{-1} mod q; k = k0 + p*c1.
- README.dlp confirms `target=t1,t2,...` multi-target syntax => both tgt and base
  logged w.r.t. implicit generator; ratio gives DLP in arbitrary base. parameters/dlp/params.p40
  available for this 39-digit p.
- Build round 2 fix (link): MSYS ld can't resolve gmpxx C++ stream operators
  (operator<< on mpz_struct) — config/gmp.cmake `gmp_libname` patched "gmp" ->
  "gmp;gmpxx".
- Build round 3 fix (compile): linalg/bwc/lingen_matpoly_binary.cpp static_assert
  `is_same_v<unsigned long, mp_limb_t>` too strict for MSYS (LP64: both 8 bytes,
  mp_limb_t=unsigned long long) — relaxed to sizeof-equality.
- Build round 4 fix (link): polyselect/polyselect_shash.h GNU89-vs-C99 inline
  mismatch across TUs -> multiple definition of polyselect_shash{,2}_add on PE-COFF
  — both qualifier branches patched to `static inline` (EMIT_ADDRESSABLE TU still
  emits the strong definition).
- Driver: ~/driver.sh waits build [100%] -> dlp_run2.sh
  (NCPUS_FAKE=2; --parameters params.p40; workdir ~/dlp_work;
  logs read from accountdb sqlite -> c1q=Lt*La^-1 mod q + sanity pow check).
- Build OK after the 4 fixes (BUILD4_EXIT=0, all binaries linked).
- cado-nfs.py runtime portability issues found+fixed on MSYS:
  1) werkzeug HTTPS API server BlockingIOError on cygwin sockets ->
     scripts/cadofactor/cadotask.py StartServerTask "ssl": True->False (http).
  2) empty server whitelist blocked the local client (403) -> cadotask.py appends
     "127.0.0.1" to server_whitelist.
  3) this master needs an EXPLICIT local client: cado-nfs-client.py
     --server=http://localhost:$PORT (no --retries option; auto-client absent).
  4) driver MUST run via `bash -lc` (login shell): non-login bash.exe script.sh
     resolves python3 to Windows python (no flask/cadofactor) => ModuleNotFoundError.
  5) build/WORKSTATION/scripts lacked the cadofactor package -> cp -r from source
     (+ PYTHONPATH=source/scripts in run scripts).
- Sieving params: p40 dlp defaults qmin=5000 with lpb=14 abort WUs ("special q
  larger than large-prime bound") -> added tasks.sieve.allow_largesq=true
  (accepted; check now bypassed).
- CURRENT BLOCKER: sieve/las.exe SEGFAULTS (exit -11) on every real WU under
  MSYS (even -t 1, -allow-largesq; las -h works). Suspect SIMD/alignment port
  bug (build flags -mavx2 -mpclmul + cygwin malloc 16B align vs 32/64-byte
  aligned buffers). gdb backtrace being captured (las_bt.log) for the fix
  (candidates: rebuild sieve with -fno-tree-vectorize / SSE2-only, or upstream
  alignment fix).
- BLOCKER UPDATE (gdb): crash is INSIDE /usr/bin/msys-2.0.dll in a las
  worker std::thread (frame #28 = std::thread::_Invoker<void(las_info&, int,
  report_and_timer&)> -> sieve/las.cpp:1595 subjob threads). `ulimit -s
  unlimited` does NOT help. Root cause = cygwin threads/libportability in the
  current master, needs real porting work (e.g. try a cado-nfs release tag
  instead of master, port las threads to omp_proxy, or run the sieving stage
  in a Linux VM/container).
- Everything else in the pipeline is proven working on this box end-to-end:
  polyselect(size+root), numbertheory_tool, makefb, freerel all completed
  against the real instance; server+client link works (http, whitelist ok).
- Repro/resume: `bash -lc 'bash ~/dlprun3.sh'` (fresh workdir
  rm -rf ~/dlp_work first). Exact failing cmd captured in
  ~/sqcmd.sh. c1q extraction + solve + submit remain one-liners:
  c1q from accountdb logs table (Lt*La^-1 mod q), then
  python3 solve_final.py <c1q> && python3 submit_flag.py unevaluated-tetctf2021 <flag>.

## RUN 2026-11-02b (root cause FOUND — thread-pool red herring)
- gdb full backtrace of the "thread" segfault: real crash = SIGSEGV on
  `vmovdqa %ymm0,-0x20(%rbp)` inside do_one_special_q — AVX 32-byte-aligned
  STACK SPILL. MSYS2/cygwin guarantees only 16-byte stack alignment; gcc on
  x86-64 assumes SysV 32-byte. std::thread itself is fine. ulimit/linker
  stack size irrelevant.
- Secondary bug also fixed: mpz_poly_roots entered libgomp from the subjob
  thread in a pattern that crashes on cygwin (frames gomp->msys-2.0.dll);
  utils/mpz_poly.cpp patched with `#undef HAVE_OPENMP` under __CYGWIN__
  (rootfinder now serial). las.cpp subjob spawn patched to pthread_create
  with 256MB stack under __CYGWIN__ (LAS_THREAD_STACK_MB env override).
- FIX applied: sieve/CMakeLists.txt gains
  `if(CYGWIN) add_compile_options(-mpreferred-stack-boundary=5 -mstackrealign)`
  → rebuild target las → retest exact WU (sqcmd.sh cmd).

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.

## RUN FINAL 2026-11-03/04 — SOLVED (server-accepted)
1. linalg completed overnight (client chain dlprun5.sh; CADO checkpointed).
2. descent crashed: las_descent binary unbuilt -> 'make las_descent -j2' in MSYS2
   (~/tools/msys64 login shell; plain git-bash lacks make). MAKE_RC=0.
3. gcc-16 alignment miscompile pre-patched: patch_align.py rewrote 3349 VEX sites
   (identical count to las.exe twin).
4. stack restart (stale client killed; download/las_descent cache purged per skill)
   -> descent completed within minutes: Lt=log(target)=52428006994321819500721565893750632838,
   La=log(base)=24604319847519209932104184704152670097 (mod q).
5. c1q = Lt*La^-1 mod q = 73786676453545329798001225722728090587 -> solve_final.py
   -> t=1, k=36448648214228125938240931382630080621576419859132411658551075951915466230810,
   pt = [flag — recorded in FLAGS/ctf-archive/challenge-305-cryptohack-unevaluated-tetctf2021/flag.txt] (valid pad, printable).
6. submit_flag.py -> HTTP 200 accepted; API solved 298 -> 299 (score unchanged: archive level).
Instance was believed OFFLINE (run 11-02) — the submit endpoint in fact accepted; the
"offline" door was a dead submission path assumption, not a dead challenge.
