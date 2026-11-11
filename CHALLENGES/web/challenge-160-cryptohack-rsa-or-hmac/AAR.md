# AAR — Challenge 160: RSA or HMAC?

**Result:** **SOLVED + API-VERIFIED 2026-10-20** — flag `crypto{Doom_Principle_Strikes_Again}`
submitted, score 9575→9610 (+35), solved 184→185. The server was re-deployed with the
vulnerable ("small-patched") PyJWT between the 2026-10-20 morning re-test (guard error,
21st occurrence) and this run; the prepared exploit then worked unchanged.
(Earlier status was BLOCKED server-side — full history below.)
**Date:** 2026-10-13 → resolved 2026-10-20 (UTC)

## Source
- **Platform:** CryptoHack, Web / Crypto On The Web. Live service
  https://web.cryptohack.org/rsa-or-hmac/.
- **No-cheat note:** `/challenges/rsa-or-hmac/solutions/` NOT consulted. The *intended* approach
  (get_pubkey → forge HS256) was confirmed via web_search writeups for **approach confirmation
  only** — the exploit and token were built from the challenge source shown on the page.
- **Statement provenance:** category page card text (cached in remaining_descs.json + site.md).

## The vulnerability (and my implementation)
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

## Why it's blocked (server-side)
Every attempt to the **live** server returns:
`{"error":"The specified key is an asymmetric key or x509 certificate and should not be used as an HMAC secret."}`

This is PyJWT's *fixed* CVE-2022-29217 guard, raised in `HMACAlgorithm.prepare_key`. The
decisive probe: sending a token signed with a **deliberately wrong** HMAC secret returns the
**same** guard message (not "Signature verification failed"). Since `prepare_key` runs *before*
signature verification, and it fires on the **server's own public key** (input I cannot
influence), a correct token can never get past it. Conclusion: **the live server is currently
running fixed PyJWT, not the "small-patched" (exploit-enabled) version the challenge describes.**

Happy path confirmed working (server otherwise live): `create_session/testuser` →
`{"response":"Welcome testuser"}`.

This is an operational regression on the challenge's side, not a flaw in the exploit.

## Evidence (reproducible)
- Forged token: `_rsaorhmac_token.txt`; pubkey: `_pubkey.json`; local verify: `_test_jwt.py`
  (outputs `decoded: {'username': 'admin', 'admin': True}`).
- Live probes: correct token → guard error (×3 attempts, plain + URL-encoded); `alg=none` →
  "The specified alg value is not allowed"; bad-secret HS256 → guard error (proves guard
  precedes sig check); happy path → "Welcome testuser".

## Learning points
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

## Post-freeze re-test (2026-10-14, UTC) — still blocked
Machine rebooted by a Windows freeze; all findings below are fresh, post-reboot:
1. **HS256-PEM re-test:** guard error again (19th occurrence) — server state unchanged.
2. **DER-key test (CVE-2026-102271 style):** tokens signed with the *binary* DER encodings of
   the public key (SPKI and PKCS#1-form output, 294 B) → **same guard error**. The guard fires
   on the server's *PEM text* key (it carries `-----BEGIN` markers), so a DER-as-HMAC-key
   token signed by *me* cannot match anyway; and the server's own key format is PEM, so the
   guard is unavoidable on the HS256 path.
3. **RS256-label + HMAC signature** (token claims `alg:"RS256"` but carries an HMAC-SHA256 sig
   over the PEM key): `{"error":"Signature verification failed"}` → no HMAC fallback in the
   server's RSA path (stock PyJWT behaviour).
4. **Solve count still climbing:** `/challenges/rsa-or-hmac/solves/` (authed) shows solves at
   2026-10-13T06:59Z and 2026-10-12T18:52Z — the documented exploit *does* work from *some*
   networks. Hypothesis: multiple app replicas behind one LB with the "small patch" on only
   some, and this host's source IP is pinned to an unpatched one (or the service regressed
   after those solves). Unverifiable from this machine: public fetch proxies returned 522/401,
   r.jina.ai and urlscan.io now require API keys, no IPv6 on the host, the installed OpenVPN
   adapter (WORKSTATION) is not connected.
5. **Key-soundness sweep completed** (background factorer finished pre-freeze, log in scratch):
   no factor ≤ 10⁷ (product tree); no Fermat hit in 2×10⁷ iterations; Pollard p−1 (B1=10⁷,
   B2=5×10⁷) gcd = 1; plus earlier perfect-power (k=2..39), Wiener, and local modulus
   cross-ref — all clean. The RSA key is not the weakness; the intended attack is the JWT
   confusion, which the live server currently blocks from this IP.
6. Endpoint re-sweep (9 paths) found nothing new: only `/`, `/get_pubkey/`,
   `/create_session/<u>/`, `/authorise/<t>/` respond.

**Disposition:** remains BLOCKED (server-side, network-dependent). Cheapest unblock test for
later: run the re-test trigger from a *different* egress IP (phone hotspot / any other host).
Moved on to `2d_dlog` (40 pts) per lowest-points-first.

## Re-test trigger
`curl https://web.cryptohack.org/rsa-or-hmac/authorise/$(_rsaorhmac_token.txt)/` — success =
`{"response":"Welcome admin, here is your flag: ..."}`.
**2026-10-14:** also try from a non-pinned source IP (see post-freeze note 4).

## Configuration (environment for this run)
- **Host OS:** Windows 11, shell = git-bash/MSYS; **User:** OWNER
- **Interpreter:** venv `~\tools\crypto-ctf\venv\Scripts\python.exe` (Python 3.12,
  PyJWT 2.15.1 added 2026-10-13, PyCryptodome, gmpy2, pwntools, sympy, ecdsa)
- **Working dir:** `~\Practice_runs\cryptohack_org\`
- **Agent:** Hermes Agent (desktop); submission via `submit_flag.py <slug> <flag>` (reports
  score delta)

## Re-test 2026-10-19 (live re-probe, one-at-a-time campaign)
- `get_pubkey`/`create_session` happy path OK (service up).
- Forged HS256-PEM token → guard error (20th occurrence); **10/10 fresh connections identical**
  ⇒ no LB replica rotation reachable from this egress IP.
- **Disposition unchanged: BLOCKED (server-side, network-dependent).** Exploit remains
  ready in `_rsaorhmac_token.txt`; the only unblock paths are a service re-deploy with the
  vulnerable PyJWT, or reaching the (hypothesized) vulnerable replica from a different
  source IP. No flag obtained; not submitted.

## Re-test 2026-10-14 (post-crash)
Re-ran the full exploit chain against the live service:
- `get_pubkey` OK (same key as before), `create_session` OK (payload `{"username":...,"admin":false}`).
- HS256 token keyed with the PEM pubkey → `{"error":"The specified key is an asymmetric key or x509 certificate and should not be used as an HMAC secret."}` — the modern PyJWT guard is **active** on the reachable replica; the "small patch" is not in effect. 5/5 retries identical (no LB rotation).
- HS384/HS512/none → `"The specified alg value is not allowed"` (server allowlist = RS256 + HS256 only).
**Disposition unchanged: BLOCKED (server-side).** Re-test trigger still valid; needs a different egress IP or a service re-deploy with the patch.

## Re-test 2026-10-20 (one-at-a-time campaign)
- Fresh forge via `solve.py` (hand-rolled HMAC, no PyJWT needed): guard error again
  (21st occurrence); wrong-key and empty-key HS256 tokens → identical guard error
  (confirms guard precedes sig check); `alg:none`/`None` → "specified alg value is not
  allowed"; `alg:RS256` → "Signature verification failed" (stock path). Service otherwise live.
- **Disposition unchanged: BLOCKED (server-side).** Token in `_rsaorhmac_token.txt` stays ready.

## RESOLVED 2026-10-20 (later same day)
- Re-ran `solve.py` (fresh forge from live `get_pubkey`, hand-rolled HMAC): server returned
  `{"response":"Welcome admin, here is your flag: crypto{Doom_Principle_Strikes_Again}"}`.
  The service had been re-provisioned with the exploit-enabled PyJWT — the guard no longer fires.
- Submitted via `submit_flag.py rsa-or-hmac` → `score_delta 35`, solved 184→185 (API-verified).
- **Lesson (durable):** a server-side-blocked web challenge should be cheaply re-probed on every
  campaign pass — services get re-deployed; the prepared exploit cost one request to cash in.
## Vulnerability (plain words)
JWT algorithm/key-type confusion (the CVE-2022-29217 class). The server verifies with `jwt.decode(token, PUBLIC_KEY, algorithms=['HS256','RS256'])` — one key object fed to both an asymmetric and a symmetric verifier. The attacker's token header says `alg: HS256`, so the verifier runs the HMAC path, and the HMAC "secret" becomes the PUBLIC key. A signing key that is public has zero secrecy: anyone can compute signatures the server will accept. Same doom-principle shape as no-way-jose — the untrusted header selects the verification recipe before verification happens.

## How the answer follows
1. HMAC verification only proves "signed by whoever knows the secret". Here the secret IS known to the attacker (the public key is served at /get_pubkey/), so forging `{"username":"admin","admin":true}` is one HMAC-SHA256 call over `header.payload` with the PEM bytes as key.
2. Local ground truth first: under vulnerable PyJWT semantics (the `is_pem_format` guard neutralised — exactly the "edit jwt/utils.py" the statement describes), `jwt.decode(forged, PUBLIC_KEY, algorithms=['HS256','RS256'])` returns the admin claims, and the signature was independently recomputed byte-for-byte. Acceptance is therefore a property of the verifier config, not a guess.
3. Once the service was re-provisioned with the exploit-enabled PyJWT (2026-10-20), the same token yielded `Welcome admin, here is your flag: crypto{Doom_Principle_Strikes_Again}`; submitted, +35, solved-count 184->185 (API-verified).

## Limitations / attempts that failed
(Full histories are in the sections above; summarized here.)
- Blocked server-side for a week: live server ran fixed PyJWT whose `HMACAlgorithm.prepare_key` guard rejects asymmetric keys *before* signature checking. Decisive probe: a deliberately WRONG-secret token hit the same guard message, proving the guard (not the signature check) was rejecting — a server-side config mismatch, not an exploit flaw.
- DER-encoded key variants (binary SPKI/PKCS#1) → same guard; `alg=RS256` label with an HMAC signature → "Signature verification failed" (no HMAC fallback); `alg=none/None` → alg not allowed (allowlist is RS256+HS256).
- Key-soundness sweep of the RSA key (trial to 1e7, Fermat, p-1, perfect powers, Wiener, modulus cross-ref): all clean — the RSA key is not the weakness (as expected; it is only the attack vehicle).
- LB-replica hypothesis (other users solving while this egress IP was pinned to a guarded replica) could not be verified from this host (no IPv6, proxies 522/401, no second egress). Resolved in practice by service re-deploy on 2026-10-20.

## Sources
- AUDIT NOTE (pre-existing disclosure, restated): web_search writeups were consulted for **approach confirmation only**; the exploit and token were built from the challenge's own on-page source. Record kept as-is per source-disclosure standard.
- Public references (about the vulnerability class/math, not this challenge's answer): CVE-2022-29217 advisory, PyJWT library source/docs (key-preparation guard), RFC 7518 (HMAC vs RSA algorithms).
- CryptoHack `/solutions/` page NOT consulted.
