# AAR — toshitreasure (CryptoHack, misc, 150 pts) — SOLVED

Flag: `[flag — recorded in FLAGS/misc/challenge-197-cryptohack-toshitreasure/flag.txt]` (score_delta +150, verified)

## The vuln
Plain (non-verifiable) Shamir Secret Sharing over GF(2^521−1) — the 13th Mersenne
prime (counting M2,M3,M5,M7,M13,M17,M19,M31,M61,M89,M107,M127,M521). The combiner
reveals the reconstructed secret for *any* submitted share, and a participant can
freely choose their own share. No commitments/Pedersen VSS → a malicious shareholder
controls the output.

## Attack
x-coords fixed: teammates 2–5, me 6. Reconstruction at x=0 is linear in the shares:
s = C + λ₆·y₆, with λ₆ = (2·3·4·5)/((6−2)(6−3)(6−4)(6−5)) = 120/24 = **5** mod p.

1. Submit fake share y=0 → server prints combined secret = C (one oracle call gives C).
2. Craft y* = (s_target − C)·5⁻¹ mod p with s_target = my $1k wallet privkey
   (from hyper_privkey.txt) → ceremony reconstructs *my* key (story step 2).
3. Server then asks for the privkey of the *real* wallet. Recover it from the same
   linear relation: s_real = C + 5·y_real (y_real from the banner share) → 256-bit
   valid key → flag.

Key numbers: p = 2^521−1; λ₆ = 5; C observed per-session (shares regenerate per
connection, so oracle + craft must share one session).

## Learning points
- "13th Mersenne prime" is M521, not M127 — off-by-one counting trap.
- Linearity of Lagrange interpolation at x=0: one chosen-plaintext-style oracle query
  pins down everything else; λ for your own x-slot is pure public info.
- This is exactly why real key ceremonies need Pedersen/VSS (the flag says so).
- The final step needed the *real* secret, not the forged one — read the story
  ("Unlock the real wallet") before guessing what the wallet wants.

## Limitations
- First unlock attempt sent the forged $1k privkey → "invalid private key"; the
  wallet wanted the real reconstructed secret (fixed on 2nd try, same session logic).
- No failures otherwise; no third-party writeups consulted (Wikipedia example code
  is the challenge's own reference for SSSS).

Files: statement.txt, hyper_privkey.txt, solve.py (end-to-end), probe.py/probe2.py
(protocol discovery), flag_toshitreasure.txt.

## Source (section added by 2026-11-09 corpus audit — AAR body text unchanged)
- Platform: CryptoHack, ctf-archive card 'Toshi's Treasure' (challenge file per site.md).
- Statement provenance: statement.txt in folder (begins: " Toshi&#39;s Treasure 150 pts &middot; 629 Solves &middot; 13 Solutions --> You ...")
- Provided material as stored in folder: flag_toshitreasure.txt, hyper_privkey.txt, probe.py, probe2.py, solve.py, statement.txt
- Not consulted: /solutions/ pages, third-party writeups (campaign no-cheat rule).
