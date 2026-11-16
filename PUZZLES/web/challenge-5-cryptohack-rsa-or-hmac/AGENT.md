---
record: agent-aar
puzzle: challenge-5-cryptohack-rsa-or-hmac
category: web
url: https://cryptohack.org/challenges/rsa-or-hmac/
status: solved
date: 2026-10-20
flag_ref: "FLAGS/web/challenge-5-cryptohack-rsa-or-hmac/flag.txt"
flag_sha256: 9e28425507b534600ed8fef00f64eb1a5ef7b47c740ea02710b7315a0bb67b5e
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 160: RSA or HMAC?
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability (and my implementation)" [OBSERVED text; evidence tag applies to its source, not each claim]
Classic JWT algorithm confusion (CVE-2022-29217): the server verifies with
`jwt.decode(token, PUBLIC_KEY, algorithms=['HS256','RS256'])`. Because the *same* `PUBLIC_KEY`
is handed to the HS256 (HMAC) path, an attacker can forge an `HS256` token whose HMAC secret is
the **public** key:
- header `{"alg":"HS256"}`, payload `{"username":"admin","admin":true}`
- `sig = b64u(HMAC-SHA256(pubkey_pem_bytes, "header.payload"))`
- → `GET /rsa-or-hmac/authorise/<token>/`

The statement's "make the edit to `jwt/utils.py`" is about the player's *local* PyJWT: modern
PyJWT's `jwt.encode(..., 'HS256')` refuses an asymmetric key, so you neutralise the
`is_pem_format`/asymmetric-key guard to mint the token. I reproduced this exactly: installed
PyJWT 2.15.1 in the venv, monkeypatched `jwt.algorithms.is_pem_format = lambda b: False`
(equivalent to the utils.py edit), and **`jwt.decode(forged, PUBLIC_KEY,
algorithms=['HS256','RS256'])` returns `{'username':'admin','admin':True}`** — the token is valid
under the vulnerable PyJWT. The HMAC signature was independently recomputed and matches
byte-for-byte.

## reusable-rules
- **A locally-verified exploit that the live server rejects with the library's own anti-abuse
  guard** signals the *server* config differs from the challenge premise. Probe with a
  **known-bad** input: if the bad input hits the same guard, the guard (a pre-check) is what's
  firing, and it's server-side.
- **`prepare_key` ordering matters:** for HMAC, key-shape validation runs before signature
  checking, so the key *format* (PEM public key) — not the signature — is what the fixed guard
  rejects.
- The "make the edit on *your* machine" phrasing is easy to misread as patching the server; it's
  about your local `jwt.encode` refusing an asymmetric key.
- **Re-test later:** if the service is re-provisioned with vulnerable PyJWT (or the guard
  disabled), the prepared token in `_rsaorhmac_token.txt` should be submitted as-is.

## anti-patterns / limits
(Full histories are in the sections above; summarized here.)
- Blocked server-side for a week: live server ran fixed PyJWT whose `HMACAlgorithm.prepare_key` guard rejects asymmetric keys *before* signature checking. Decisive probe: a deliberately WRONG-secret token hit the same guard message, proving the guard (not the signature check) was rejecting — a server-side config mismatch, not an exploit flaw.
- DER-encoded key variants (binary SPKI/PKCS#1) → same guard; `alg=RS256` label with an HMAC signature → "Signature verification failed" (no HMAC fallback); `alg=none/None` → alg not allowed (allowlist is RS256+HS256).
- Key-soundness sweep of the RSA key (trial to 1e7, Fermat, p-1, perfect powers, Wiener, modulus cross-ref): all clean — the RSA key is not the weakness (as expected; it is only the attack vehicle).
- LB-replica hypothesis (other users solving while this egress IP was pinned to a guarded replica) could not be verified from this host (no IPv6, proxies 522/401, no second egress). Resolved in practice by service re-deploy on 2026-10-20.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack, Web / Crypto On The Web. Live service
  https://web.cryptohack.org/rsa-or-hmac/.
- **No-cheat note:** `/challenges/rsa-or-hmac/solutions/` NOT consulted. The *intended* approach
  (get_pubkey → forge HS256) was confirmed via web_search writeups for **approach confirmation
  only** — the exploit and token were built from the challenge source shown on the page.
- **Statement provenance:** category page card text (cached in remaining_descs.json + site.md).
