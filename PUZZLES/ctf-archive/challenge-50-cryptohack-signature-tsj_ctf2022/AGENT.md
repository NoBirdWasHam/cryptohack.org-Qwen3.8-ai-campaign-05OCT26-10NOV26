---
record: agent-aar
puzzle: challenge-292-cryptohack-signature-tsj_ctf2022
category: ctf-archive
url: https://cryptohack.org/challenges/signature-tsj_ctf2022/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-50-cryptohack-signature-tsj_ctf2022/flag.txt"
flag_sha256: 2ba312df360ca7b147dae6fed656c00592d8ab503e063da2469215c8f4ff856e
skills: []
human_twin: AAR.md
---

# AGENT — challenge-292: CryptoHack "Signature" (TSJ CTF 2022)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability / model" [OBSERVED text; evidence tag applies to its source, not each claim]
k = d XOR z = d + z − 2(d AND z). From s·k ≡ z + r·d (mod q):

    d·(s−r) − 2s·(d AND z) ≡ z·(1−s)  (mod q)

Writing d = Σ 2^j d_j, d_j ∈ {0,1}, each signature is ONE linear equation mod q in the
256 bit-unknowns:

    Σ_j 2^j·d_j·((s−r) − 2s·z_j) ≡ (1−s)·z  (mod q)

6 equations, 256 binary unknowns → expected #binary solutions = 2^(256−4·256)=~0 ⇒ unique.
Solved as CVP in the kernel lattice {w : M w ≡ 0 mod q} (det q^6) with target = sparse
particular solution x0 (free vars = 0). Model VALIDATED on simulated signatures
("model check on sim d: True") — true bits satisfy M·bits = v exactly.

## reusable-rules
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

## anti-patterns / limits
`solve.py:try_candidate` checked `r == x((d XOR z) mod q · G)`, but challenge.py multiplies
G by the UNREDUCED integer `k = d XOR z`. z is a raw sha256 value, ≥ q roughly half the
time, so k ≥ q frequently and k·G ≠ (k mod q)·G. The real r values therefore did NOT match
for the TRUE d ⇒ the 64-flip repair loop rejected the correct candidate and the run
wrongly escalated to BKZ. Fixed in solve.py (use k unreduced).

## artifacts [OBSERVED]
- code: solve.py, solve2.py, solve3.py, solve4.py, solve5.py
- data/logs: b262v4.txt, flag_signature-tsj_ctf2022.txt, output.txt, real5.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided challenge.py + output.txt only. The GitHub URL inside the recovered flag string (jonasnick/ecdsaPredictableNonce) is a flag payload reference, not a consulted solution artifact; per the run logs nothing there was read as a writeup. Lattice modeling derived in-session (uSVP/Kannan embedding); pycryptodome CTR auto-nonce behavior reproduced locally on 3.24. No CryptoHack solutions pages consulted.
