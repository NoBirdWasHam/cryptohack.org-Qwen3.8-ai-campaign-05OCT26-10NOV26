---
name: cado-nfs-msys-port
description: Use when building/running CADO-NFS on MSYS2 or Windows.
---

# CADO-NFS on MSYS2 (cygwin) port checklist

Build (cmake tree, e.g. tools/cado-nfs build/WORKSTATION):
- CXX flags: `-fpermissive -D_GNU_SOURCE -Wno-format` (mp_limb_t=unsigned long long).
- config/gmp.cmake: `set(gmp_libname "gmp;gmpxx")` — MSYS ld needs libgmpxx for
  C++ stream operators on mpz/mpq.
- linalg/bwc/lingen_matpoly_binary.cpp: relax static_assert to
  `sizeof(unsigned long)==sizeof(mp_limb_t)` (cygwin LP64, both 8B).
- polyselect/polyselect_shash.h: patch BOTH inline qualifier branches to
  `static inline` (GNU89/C99 inline mismatch -> multiple defs on PE-COFF).

Runtime (cado-nfs.py master):
- MUST run via `bash -lc` (login shell): non-login bash.exe picks Windows
  python3 (no flask/cadofactor).
- api_server: werkzeug HTTPS dies with BlockingIOError on cygwin sockets ->
  cadotask.py StartServerTask paramnames `"ssl": False`.
- Empty whitelist blocks localhost (403) -> append "127.0.0.1" to
  server_whitelist in cadotask.py before ApiServer(...).
- master has NO auto local client: run cado-nfs-client.py --server=http://
  localhost:PORT explicitly (no --retries option); copy scripts/cadofactor
  into build dir scripts/ and export PYTHONPATH=source scripts.
- NCPUS_FAKE=2 caps all tasks.*.threads.
- p40 dlp params + qmin=5000 need tasks.sieve.allow_largesq=true.
- KNOWN BLOCKER SOLVED (run 2026-11-02c final): las.exe "segfault in std::thread
  inside msys-2.0.dll" was NOT threads: MSYS2 gcc-16.2 emits vmovdqa/vmovaps
  32-byte-aligned stack spills whose entry-residue assumption is inconsistent
  across call chains (psb16 vs SysV). No entry alignment, stack size, pthread
  stub, or compiler flag fixes ALL sites (-mstackrealign asserts; AVX-disable
  breaks intrinsics). WORKING FIX: binary-rewrite aligned VEX loads/stores to
  unaligned in the PE: C5 F9/FD + 6F/7F -> +1 (vmovdqu); 28/29 -> -1 (vmovups);
  objdump-driven, PE VA->file-offset aware: ~/patch_align.py
  (3349 instrs in las.exe). SAME MISCOMPILE hits lingen_pz.exe (169 sites),
  filter/merge.exe (108), sqrt/sqrt.exe (233) — patch each on first crash.
  Keep .orig backups. Verified 25+ consecutive WU runs, deterministic rel counts.
  (gdb: `handle SIGSEGV stop nopass` + `bt 60` needed to see real chain.)
  Also: pass PATH=/usr/bin first when launching las from non-msys shells
  (msys-stdc++-6.dll not found otherwise).

Operational (server+client manual mode):
- DESCENT needs `make las_descent` — build ONLY via MSYS2 login shell:
  `~/tools/msys64/usr/bin/bash -lc 'cd <builddir> && make las_descent -j2'`
  (git-bash has no make/c++; CMakeCache /usr/bin/* paths = MSYS2 env). Pre-patch the
  built exe with patch_align.py (las-family miscompile; 3349 sites on las_descent.exe,
  identical to las.exe) BEFORE first client fetch, and rm -rf build/<x>/download/las_descent
  so clients never cache the unpatched binary. Descent then completes in minutes once
  linalg is done. SOLVED-VERIFIED on challenge-305 2026-11-04.
- Server log block-buffers: launch cado-nfs.py master via `python3 -u`.
- Ready marker in server log is "Running on" (not "listening").
- rm -rf build/.../download/las before EACH launch (stale unpatched cache exe).
- Zombie clients are python.exe — taskkill by image misses them; kill by PID.
- Stale task-DB failure counters poison restarts: move whole workdir aside
  (dlp_work.poisoned.N) for a fresh run, don't try to surgically reset.
DB state poisons on repeated WU failures -> rm -rf workdir for fresh run.

## Canonical references (owner list 2026-11-02)

[R29] Buhler-Lenstra-Pomerance, 'Factoring integers with the number field sieve', LNCS 1554, 1993 (the NFS textbook chapter). https://link.springer.com/chapter/10.1007/BFb0091537 | [R30] CADO-NFS dev team, https://cado-nfs.inria.fr/ (reference implementation + parameter generator).
   CITATION ERRATUM (2026-11-02): DOI 10.1007/BFb0091537 is actually Lenstra-Lenstra-Manasse-Pollard,
   'The number field sieve' — SAME volume (LNM 1554, 'The development of the number field sieve'), DIFFERENT
   chapter. BLP'93 is a separate chapter of that volume; cite each by its own chapter when quoting.
   CADO-NFS recommended citation (their site): 'The CADO-NFS Development Team. CADO-NFS, An Implementation
   of the Number Field Sieve Algorithm, release <X.Y.Z>, <year>, http://cado-nfs.inria.fr/' — include the
   release you used; for dev builds give the git revision.
