# AAR — rsatogether (CryptoHack, challenge-322, ECSC 2024 Italy)

**Status: SOLVED & SUBMITTED.** Flag: `ECSC{eprint_p4p3r5_c4n_b3_r3al1y_s0m3thin6_4t_tim3s_e732fc09c4a0cf80}`
(solved-list 278→279; archive = 0 pts by design.) Self-derived; no writeups consulted.

## Vulnerability
Server: Shamir-style sharing of RSA secret over Z/phi (not mod lambda!), nodes x=1..t, t = n_shares+1.
"You are also given a share" leaks the share at node x=k for input k: u_k = beta_k * P_k(k) mod phi with
beta_k = (-1)^(k-1) * (k+1) (Lagrange-at-0 weight C(k+1,k) up to sign) and P_k = poly truncated to k+1
coeffs (staircase: coeff a_j absent from rows k < j). 101 inputs (k=1..101) vs 100 poly coeffs.

## Attack (pipeline: fetch_all.py + kernel.py + factor_from_phi_multiple.py + solve.py)
1. Exact dim-1 left kernel w of the 101x100 staircase A[k][j]=k^j (j<=min(k,99)):
   sum_k w_k k^j = 0 for j=0..99. Then M0 = sum_k (L*w_k/beta_k) * u_k = -phi * sum(nu_k t_k) is an
   **exact integer multiple of phi**, computable from server output alone. mu = L*w/beta, max |mu| ~ 2^15475
   (superlinear growth confirmed — this is why the ±window trick on M/n died; irrelevant anyway).
2. **Key unlock over previous session: Miller/Sabt factoring from ANY multiple of phi(n)** — write
   M0 = 2^s * m, random g, walk x_i = g^(2^i m) to first 1, gcd(x-1, n) splits. Size of the multiple is
   irrelevant (log M0 ~ 17.5k bits, trivial). Previous run stopped at "M0 too big for C=round(M/n) window".
3. Single connection needed (per-connection keys; verified n differs across conns): menu 2 x101 (reshare
   input k), then 3 for flag ct. All 101 u_k + ct in one session: fetch_all.py.
4. d = e^-1 mod phi, pt = ct^d, regex ECSC{...} out of random-length random padding.

## Operational notes (cost real time)
- Server prompt is "...private key? " — NOT "friends?"; old stop-token was only satisfied by timeout.
- Per-char read(1) reader made ~0.85s/roundtrip; server disconnects at ~85-100s -> one fetch failed at
  k~99 three times. Chunked s.recv(65536) fixes it (whole fetch ~140s worst case, retries in script).
- sympy `LUsolve` on the 100x100 staircase minor silently returns garbage (minor is SINGULAR — rows carry
  j<=k not j<k); `A.T.nullspace()` is the correct dim-1 source (took ~6.2 min). ALWAYS run the algebraic
  `ok` check — it caught the bogus solve.
- Python 3.11+ int->str cap: sys.set_int_max_str_digits(10**6) needed before dumping/reading 15k-bit ints.
- Lagrange sign: coeffs_x = (-1)^(x-1) C(t,x). sim.py used (-1)^(t-j) — wrong; sim2 asserts both the
  share model AND M0 % phi == 0 offline before touching live math.

## Files created this session
fetch_all.py, kernel.py, kernel.json, factor_from_phi_multiple.py, sim2.py, solve.py, live_data.json.

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
