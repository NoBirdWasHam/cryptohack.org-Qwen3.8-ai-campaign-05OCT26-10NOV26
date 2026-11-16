---
record: agent-aar
puzzle: challenge-1-cryptohack-authentification_1-breizh_ctf
category: ctf-archive
url: https://cryptohack.org/challenges/authentification_1-breizh_ctf/
status: solved
date: 2026-10-28
flag_ref: "FLAGS/ctf-archive/challenge-1-cryptohack-authentification_1-breizh_ctf/flag.txt"
flag_sha256: 656160d0749984850258a1e8ea08528c37fac59b9214f8f5a38e3580003d242b
skills: []
human_twin: AAR.md
---

# AGENT — authentification_1-breizh_ctf (challenge-248)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
Flask app issues GCM-authenticated session tokens `ct.hex();tag.hex()`; `/admin` prints the
flag iff the decrypted JSON has `role == "super_admin"` (registration only ever grants
`guest`, MAX_USERS=1).

Two compounding flaws in the intern's AES-GCM (`gcm/gcm.py` + `crypto.py`):
1. Static IV (`b"\x00"*12`) — classic GCM nonce reuse.
2. The real killer: **the counter is never incremented.** `encrypt()` calls `gctr(J0, P)`
   (spec: `gctr(inc(J0), P)`), while the tag is still masked with `E(J0)`. So the tag mask
   equals the FIRST keystream block: `E(J0) = ks[0] = P[0:16] XOR C[0:16]`.
   The token plaintext is fully known (we choose the username, JSON layout is fixed),
   so `GHASH_H(buf) = tag XOR E(J0)` becomes known.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- First solver drafts had three real bugs (wrong GF identity, p_mod missing coef·m,
  128·deg trace length) each causing hangs/failures — fixed as above, no approach change.
- Root ambiguity (2 candidates) is inherent (quartic GHASH equation); resolved by server
  oracle rather than extra math. A second registration to pin H uniquely is impossible
  (MAX_USERS=1; /reset-db wipes the key).

Method references: textbook AES-GCM (NIST SP 800-38D) + standard low-degree root finding
over finite fields (gcd with x^{q}-x + Berlekamp-style trace splitting). No solutions/writeups consulted.

## artifacts [OBSERVED]
- code: solve.py, template_authentification_4f2dc17a405786f94ecd03f7768eab0a.py
- data/logs: flag_authentification_1-breizh_ctf.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Platform: CryptoHack, ctf-archive card 'Authentification 1 (Breizh CTF)' (challenge file per site.md).
- Statement provenance: statement.txt in folder (begins: "                                                                                ...")
- Provided material as stored in folder: authentification-1_55a673acec9e42d255ff43cba53f1563.zip, flag_authentification_1-breizh_ctf.txt, solve.py, statement.txt, template_authentification_4f2dc17a405786f94ecd03f7768eab0a.py
- Not consulted: /solutions/ pages, third-party writeups (campaign no-cheat rule).
