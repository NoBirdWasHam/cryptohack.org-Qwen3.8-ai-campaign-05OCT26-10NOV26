# AAR — Authenticator (Firebird Internal CTF), slug `authenticator-firebird_intern`

**Result: SOLVED.** Flag obtained from the live service (derivation of the session password via exhaustive search; verified by the service's own "Congrats!").

## The system
`chall.py` runs a blake3-based mutual-auth handshake with a 6-char password from `[0-9a-zA-Z]` **without repetition** → 62P6 = 44,261,653,680 ≈ 35.4-bit space, re-randomized per connection.

- Server prints `R1 = blake3(P || "HANDSHAKE_FROM_SERVER" || C1)` for our C1 (16 B), then sends random C2.
- We must return `R2 = blake3(P || "HANDSHAKE_FROM_CLIENT" || C2)`.
- `signal.alarm(10)` across the whole session.

## Attack
The design is RO-secure as a protocol (the S1-oracle can never output an S2-domain value), but it falls to the author's own acknowledged joke: 36 bits **is** exhaustible in-session if you have a fast enough search.

1. Custom OpenCL kernel (`b3v3.cl`) computing blake3 single-block hashes (all inputs ≤64 B → one compression, t=43, **flags=11** = CHUNK_START|CHUNK_END|ROOT, 7 rounds) for one password candidate per work-item.
2. Search space split: x ∈ [0, 62·61·60) → first 3 chars (precomputed on host: LE m0 low 3 bytes + sorted-triple LUT entry), y ∈ [0, 59·58·57) → last 3 chars via Lehmer unranking with the sorted-chosen threshold trick `p = i + #{m: s_m − m ≤ i}` (branch-free).
3. Filter on the first two digest words (64-bit) → at most one candidate for the full space; CPU-verifies with the real blake3.
4. Chunked launches (4096 y-rows) between which the host polls a match flag → early exit.
5. Measured **≈15.6 Ghash/s** on the Radeon AI PRO R9700 (gfx1201, OpenCL) → worst-case full scan ≈3 s, comfortably inside the 10 s alarm. Live solve finished in **3.5 s** from connect.
6. Flag: service printed it after a valid R2 (P recovered = `b'EkmNWn'` for that session).

## Key numbers
- Space 4.426e10; 0.49 s to R1+C2; found P at 3.38 s; verdict 3.49 s.
- Submit: ok:true 200; solved list 262→263 (archive, score_delta 0 as expected).

## Limitations / what failed (evidenced)
- Protocol-level bypass attempts all failed and are proven dead ends: replay of R1 → "Invalid response."; no session looping; alarm genuinely kills at ~10 s (13 s wait test); password fresh per connection (4 identical-C1 probes, 4 distinct R1s).
- PRNG-seed predictability: probed (probe_sessions.json) but abandoned once the structural route died — GPU scan made it moot; not tested further.
- Kernel debugging cost 4 wasted iterations: I initially implemented 16 rounds with flags=5 (misremembered BLAKE3 for ChaCha-family details) and packed an unsorted/incomplete x-table triple. Correctness against the official library (single-block random-message sweep) is what finally nailed it: **7 rounds, flags=11, sorted Lehmer decode**.
- References used (allowed, named per brief): official BLAKE3 reference implementation (`BLAKE3-team/BLAKE3` `reference_impl.rs`) consulted only to pin down compression flags/rounds — no solution/writeup of this challenge was consulted; the attack is original.

## Files
- `statement.txt`, `site.md` — statement + analysis notes
- `b3v3.cl` — GPU kernel; `engine.py` — host engine (table build, chunked scan, index↔password maps); `solve_online.py` — live attack; `chall.py` — challenge source
- `flag_authenticator-firebird_intern.txt` — flag (from service)

---

## VERIFICATION AUDIT RUN 2026-11-14 - independent rainbow-table re-derivation (original solve 2026-10-28, GPU blake3 brute)

The audit re-derived the password independently of the original method. Service-given
flag; audit-run submit receipt: solved 313 -> 314.

Method: rainbow tables over 62P6 = 44,261,653,680 six-distinct-char passwords (the 10 s
alarm forces offline precompute). Chains L=K=2048 with position-dependent salted
reductions R_i(h) = unrank(le64(T(pw)) ^ salt_i); T fixed =
blake3(pw || HANDSHAKE_FROM_SERVER || cc). Full-covering table N=M/L = 21,612,135 chains
built in ~12 min on 16 cores (rb2.c); rank-keyed endpoints + open-addressed integer
index. Online: cc = 16 zero bytes, walk K=2048 rounds x L steps, verify T(cand)==t0,
answer HANDSHAKE_FROM_CLIENT. Per-connection success ~40% (coverage 63% x chain survival
65%); recovered on attempt 3, 0.80 s connection-to-flag.

Flag: firebird{y0u_d0n7_n33d_t0_pr3c0mpu73_3very7h1n9_4nyw4y}

Artifacts: artifacts_2026-11-14/ (rb2.c table builder, auth_live2.py client).
rb3.bin (330 MB table) NOT archived - regenerates from rb2.c in ~12 min/16 cores.
