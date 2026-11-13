---
record: agent-aar
puzzle: challenge-165-cryptohack-mega2
category: web
url: https://cryptohack.org/challenges/mega2/
status: solved
date: 2026-10-23
flag_ref: "FLAGS/web/challenge-165-cryptohack-mega2/flag.txt (absent: FLAG-PLACEHOLDER-REMOVED: only a masked placeholder existed;…)"
flag_sha256: null — flag withheld (note in FLAGS/INDEX.jsonl)
skills: []
human_twin: AAR.md
---

# AGENT — CryptoHack Megalomaniac 2 (challenge-165, socket 13409)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack (1 login, ~3.5s live)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. `SID_enc = M^e mod n` with `M = 2^1024+12345`, so the *correct* CRT output is exactly `M`.
2. Fault: XOR one byte of **ciphertext block 39** (bytes 624–639). AES-ECB decryption
   scrambles the whole plaintext block 39 — which lies entirely inside the `u` field, so
   the length prefixes and the padding block stay valid. The server parses `u' = u + δ`
   (δ unknown, |δ| < 2^192) with genuine `p,q,d`.
3. Since `m = M` and `m' = h'·p + mp`, the faulted output is **`m' = M + v·p` exactly**
   (`v = h'−h`, |v| < q — no `w·n` term; the mod-q reduction is absorbed in v).
4. Server returns `m_top = m' >> 128`, so `Yc = m_top·2^128 − M ≡ −m_low (mod p)` with
   `m_low < 2^128`: a near-multiple of p. **Coppersmith** (root of `x + Yc mod p | N`,
   X = 2^130, m = 6, dim-12 lattice, fpylll LLL + `sympy.factor` over ZZ to pull the
   linear factor out of the short polynomial) gives `r = m_low`, then
   `p = gcd(N, Yc + r)`.
5. `get_encrypted_flag` (free action, no step check) → AES-ECB key
   `SHA256(l2b(p) ‖ l2b(q))` → flag.

## reusable-rules
- AES-ECB **decryption** of a tampered ciphertext block scrambles the *entire* plaintext
  block (bit-flip control exists only in the encryption direction). Fault granularity is
  one 16-byte block; pick a block whose field can absorb arbitrary garbage (u).
- A CRT fault on u perturbs the output by an exact multiple of p — truncation of the low
  128 bits then yields a Coppersmith instance `Y ≡ j·p − r`, r small. The unknown
  multiplier j makes enumeration pointless; the lattice handles it.
- `sympy.factor(P.as_expr(), domain=ZZ)` extracts the linear factor `(x−r)` from the
  short lattice polynomial; `nroots`/`gcd` routes fail on 5000-bit coefficients.

## anti-patterns / limits
- First model (from earlier session) assumed a single-byte XOR on u's low byte and
  `m = M + f·p²·d − w·n` with enumeration over (f,d,w): **wrong** — ECB block scrambling
  breaks padding (verified: byte 645 tamper → error; dbg10/dbg11), and the w-term model
  was a mis-derivation. The correct relation `m' = M + v·p` needs no enumeration.
- If `d` were 255 bytes the layout shifts by one byte and block 39 would clip u's
  length prefix; solver retries offsets 630/624 on a new connection (not needed live).

## artifacts [OBSERVED]
- code: 13409.py, cop3.py, dbg1.py, dbg10.py, dbg11.py, dbg2.py, dbg3.py, dbg4.py, dbg5.py, dbg6.py, dbg7.py, dbg8.py, dbg9.py, harness.py, solve_mega2.py, solve_mega2_v2.py, test_offline_v2.py
- data/logs: flag_mega2.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Public mathematics literature (about the MATH, per source-disclosure rules): Boneh-DeMillo-Lipton CRT fault attack; Coppersmith's small-roots method (as implemented per standard lattices references); HPS textbook available locally for Coppersmith background.
- `sympy.factor(domain=ZZ)` linear-factor extraction — library/tooling docs, not a challenge solution.
- No third-party writeup or solution artifact for this challenge consulted.
