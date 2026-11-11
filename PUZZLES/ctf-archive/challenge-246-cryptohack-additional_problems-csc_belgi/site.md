# additional_problems-csc_belgi

- Category: ctf-archive (data-stage ctf-archive-2024)
- Slug: additional_problems-csc_belgi (progress.json nn=246; NOTE: parent-task label
  "additional_problems-utctf" and the prior triage hypothesis "CSIDH-like PARI Velu
  isogeny path-finding" are BOTH disproven: no utctf challenge exists on
  cryptohack.org (checked cached + live ctf-archive card list and full inventory), and
  server.py is a DGHV-style approximate-GCD service, not isogenies.)
- Name: Additional problems (CSC Belgium)
- Points: 0 (archive)
- Service: archive.cryptohack.org:21970
- Files: server.py (static/challenges/server_ee5b62d3dc97eed5e8645e362c2183ab.py)
- Card source: https://cryptohack.org/challenges/ctf-archive/

- **2026-11-10 connection-space sweep (owner round: 'something else may be wrong; check every
  way to connect') — everything else is now eliminated:** single A record / no IPv6 (each address
  probed), no TLS, no second host/port, no per-user instance mechanism, username-first wrapper
  tested live (no effect), 12 same-host live controls (0 refused, 4 banner-live → my egress is
  clean), full code re-read (no hidden variant; release_files is a same-file pointer).
- **Solver forensics (public API, exact dates):** MAINT-ACCOUNT = first-blood staff-style account
  (joined 29-Dec-2025, before import; empty public solve list). SOLVER-A 19-Oct + SOLVER-B 01-Nov:
  identical score 17370, same-day whole-series sweeps. SOLVER-C 24-Oct: same-day pair. SOLVER-B's
  solve day overlaps three same-day 319-byte dead captures (12:49/12:59/13:10). String-collect
  pattern; interactive play cannot be proven either way from records, and is not required: the
  flag string is posted publicly and solves are website submissions.
