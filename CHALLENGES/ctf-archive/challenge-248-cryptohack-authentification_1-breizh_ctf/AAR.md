# AAR — authentification_1-breizh_ctf (challenge-248)

## Result
SOLVED. Flag obtained from the live service (archive.cryptohack.org:61277) by forging an
`auth` cookie; submitted via submit_flag.py.

## The vulnerability
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

## Attack
1. `/reset-db`, register username of length 12, `/login` (allow_redirects=False) → (C, tag).
2. `S = tag XOR (P[0:16] XOR C[0:16])` = GHASH_H(buf), buf = pad(C) || len(A) || len(C).
3. GHASH is a degree-m polynomial in H (m = #blocks = 4 here). Recover H as the roots in
   GF(2^128) of `f(x) = X1·x^4 + X2·x^3 + X3·x^2 + L·x + S`:
   - g = gcd(f, x^(2^128)+x) over GF(2^128)[x];
   - split squarefree g by absolute-trace gcds: gcd(g, Σ_{i<128}(a·x)^{2^i}), random a.
4. f typically has 2 roots in the field → 2 candidate tags; the `/admin` page is the
   validity oracle — one candidate prints "Well played! ... flag".
5. Keystream for the first 45 bytes is known → forge `P' = {"username": "a", "role": "super_admin"}`
   (40 bytes ≤ 45) as `C' = P' XOR ks`, tag' = GHASH_H(buf') XOR ks[0].

## Key implementation notes (bugs that cost time — worth remembering)
- GCM bit-reflected convention: field identity element = bytes `0x80 00...` (MSB = x^0),
  NOT 0x01. Wrong "one" silently breaks monic normalization → infinite loop in poly mod.
- Polynomial long division mod monic m must subtract **coef·m**, not m (silent infinite loop).
- Trace-splitting length: exactly 128 Frobenius terms (absolute trace GF(2^128)/GF(2)).
  Using 128·deg terms makes the trace identically 0 on GF(2^128)-rational roots for deg-2 factors.
- The intern's bit-level GF(2^128) `mul` is ~1 ms; replaced with an int-based mul
  cross-verified against theirs on 500 random pairs (kept as ground truth).
- Werkzeug quotes cookie values containing `;` as `"....\073...."`: must unescape on read
  and send the forged cookie as `auth="ct\073tag"` or Flask truncates it at the `;`.

## Evidence
- Local: solve.py `test_local()` — against the actual provided `crypto.py`/`gcm/`, forged
  tokens pass `verif_token` (guest token correctly fails): 3/3 rounds.
- Remote: FLAG line printed by /admin; see flag_*.txt.

## Limitations / failed paths
- First solver drafts had three real bugs (wrong GF identity, p_mod missing coef·m,
  128·deg trace length) each causing hangs/failures — fixed as above, no approach change.
- Root ambiguity (2 candidates) is inherent (quartic GHASH equation); resolved by server
  oracle rather than extra math. A second registration to pin H uniquely is impossible
  (MAX_USERS=1; /reset-db wipes the key).

Method references: textbook AES-GCM (NIST SP 800-38D) + standard low-degree root finding
over finite fields (gcd with x^{q}-x + Berlekamp-style trace splitting). No solutions/writeups consulted.

## Source (section added by 2026-11-09 corpus audit — AAR body text unchanged)
- Platform: CryptoHack, ctf-archive card 'Authentification 1 (Breizh CTF)' (challenge file per site.md).
- Statement provenance: statement.txt in folder (begins: "                                                                                ...")
- Provided material as stored in folder: authentification-1_55a673acec9e42d255ff43cba53f1563.zip, flag_authentification_1-breizh_ctf.txt, solve.py, statement.txt, template_authentification_4f2dc17a405786f94ecd03f7768eab0a.py
- Not consulted: /solutions/ pages, third-party writeups (campaign no-cheat rule).
