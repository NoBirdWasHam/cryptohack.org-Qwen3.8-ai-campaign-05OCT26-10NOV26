---
record: agent-aar
puzzle: challenge-18-cryptohack-rsatogether-ecsc_2024_italy20
category: ctf-archive
url: https://cryptohack.org/challenges/rsatogether-ecsc_2024_italy20/
status: solved
date: 2026-10-29
flag_ref: "FLAGS/ctf-archive/challenge-18-cryptohack-rsatogether-ecsc_2024_italy20/flag.txt"
flag_sha256: sha256:5769a5c2250c4ee7af7b4d76e754436b81dea03ac572377c96e898d47d196053
skills: [poly-ring-toolkit]
human_twin: AAR.md
---

# AGENT — rsatogether (CryptoHack ctf-archive, ECSC 2024 Italy)
Machine twin of AAR.md — facts tagged [OBSERVED]/[NOT OBSERVED]/[UNKNOWN].

## System [OBSERVED]
- Server: Shamir-style sharing of the RSA secret over Z/phi(n) (NOT lambda); nodes x=1..t, t = n_shares+1.
- "You are also given a share": input k returns u_k = beta_k * P_k(k) mod phi with beta_k = (-1)^(k-1) * (k+1),
  P_k = sharing polynomial truncated to k+1 coeffs (staircase: coeff a_j absent from rows k < j).
- 101 inputs (k=1..101) against a 100-coefficient polynomial. Per-connection keys (n differs across conns).
- Prompt string "...private key? "; server disconnects at ~85-100 s.

## Attack [OBSERVED, self-derived]
1. Exact dim-1 left kernel w of the 101x100 staircase A[k][j]=k^j (j<=min(k,99)): M0 = sum_k (L*w_k/beta_k)*u_k
   is an EXACT integer multiple of phi, from server output alone (max |mu_k| ~ 2^15475).
2. Miller/Sabt factoring from ANY multiple of phi: M0 = 2^s*m; random g; x_i = g^(2^i m) to first 1; gcd(x-1,n) splits.
   Multiple-size irrelevant (log M0 ~ 17.5k bits).
3. d = e^-1 mod phi; decrypt flag ct; regex ECSC{...} out of random padding. One connection: menu 2 x101, then 3.

## Procedure
fetch_all.py (101 u_k + ct, chunked recv, retries) -> kernel.py (dim-1 nullspace) ->
factor_from_phi_multiple.py (Miller/Sabt) -> solve.py (decrypt+submit). sim2.py asserts share model AND
M0 % phi == 0 offline before touching live math.

## Pitfalls [OBSERVED]
- sympy LUsolve on the singular staircase minor silently returns garbage; A.T.nullspace() is the correct dim-1 source. ALWAYS run the algebraic ok-check.
- Lagrange sign must be (-1)^(x-1) C(t,x).
- Read loop must be chunked (s.recv(65536)); per-char reads blow the disconnect window (3 failures at k~99).
- sys.set_int_max_str_digits(10**6) before touching 15k-bit ints (Python 3.11+).

## Verify
reproduce: sim2.py offline; live: fetch_all.py; factor + decrypt deterministic from data.
