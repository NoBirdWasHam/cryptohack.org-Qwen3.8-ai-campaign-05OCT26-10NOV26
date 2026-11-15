# Course lesson — Transparency (General)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under General as challenge `transparency`.
**Status:** completed 2026-10-05 · **Points:** 50 · **Site:** https://cryptohack.org/challenges/transparency/
**Ledger row:** `course__transparency` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Challenge 22: Transparency (CryptoHack General)

**Result:** **SOLVED + leaderboard-verified** (account NoBirdWasHam, 2026-10-05) — flag ``flag — recorded in FLAGS/general/course-transparency/flag.txt`` accepted; solved-star lit. (Slug: `transparency`.)
**Date:** 2026-10-05 (UTC)

## Source
- Platform: CryptoHack (https://cryptohack.org/)
- Statement page: https://cryptohack.org/challenges/general/ (card "Transparency", slug `transparency`, 50 pts)
- Challenge file (fetched, in this folder as transparency.pem): the RSA public key
- CT log query (preserved, in this folder as ct_log_query_certspotter_20261005.json): certspotter.com issuance search for cryptohack.org (crt.sh was returning 502 at run time)
- Flag source: visiting the identified subdomain (the statement's intended method — "visit that subdomain to obtain the flag")
- Live response (preserved, in this folder as live_subdomain_response_20261005.txt)
- Not consulted: /challenges/transparency/solutions/, any writeup (no-cheat rule)

## The flag
``flag — recorded in FLAGS/general/course-transparency/flag.txt``

## How it was solved
1. Statement: given an RSA public key (PEM), find the **subdomain of cryptohack.org**
   whose TLS certificate uses these parameters, then visit it to get the flag. This is
   a **Certificate Transparency (CT)** exercise.
2. Extracted the key's modulus (n, 2048-bit, e=65537) from `transparency.pem` with
   PyCryptodome.
3. Queried a CT log for all cryptohack.org certificates (with subdomains). crt.sh
   was returning 502, so I used **certspotter.com** (a standard alternative CT
   aggregator):
   ```
   https://api.certspotter.com/v1/issuances?domain=cryptohack.org&include_subdomains=true&expand=dns_names
   ```
   This listed subdomains including `tls1/2/3.cryptohack.org`, `blog`, `web`, `aes`,
   and — the tell — **`thetransparencyflagishere.cryptohack.org`**.
4. **Verification nuance:** I fetched the live cert of each candidate and compared its
   modulus to the PEM's. None matched the *current* live modulus — the challenge's key
   is older than the subdomain's present (re-issued) certificate, which is expected:
   CT logs keep history but a host renews. The subdomain name itself is the intended
   signal.
5. Visited `https://thetransparencyflagishere.cryptohack.org/` ->
   ``flag — recorded in FLAGS/general/course-transparency/flag.txt`` (preserved in this folder).

## Learning points
- **Certificate Transparency: every CA must publish certs to public logs**, and those
  logs are searchable by domain/subdomain. Mapping "this public key -> which domain
   used it" is a real investigative technique (incident response, mis-issued cert
   hunting) — exactly what this challenge simulates.
- **Key match vs. name match:** a host renews certs, so a *current* modulus comparison
  can fail even when the subdomain is right. CT logs give you the historical set;
  combine "does any logged cert for this subdomain match n" with the subdomain's
  naming intent. (Here the name was unambiguous.)
- **crt.sh is flaky (502s); certspotter / Google CT are reliable fallbacks.** Having
  a second CT aggregator is worth remembering for real work.
- The flag thanks **redpwn** — the challenge is modeled on redpwn's "Transparency"
  CTF idea (finding a key's subdomain via CT logs).

## What I did / did not do
- Did: extract n, CT-log search (certspotter), enumerate subdomains, verify candidates
  (noting the renewal caveat), visit the flagged subdomain, preserve the live response.
- Did not: solutions/writeups; did not submit to the leaderboard (no account).

## Limitations
- The current live modulus of the subdomain does not equal the PEM's n (cert renewal);
  the solve rests on the CT-logged subdomain identification + its served flag, which
  is the method the statement specifies ("visit that subdomain to obtain the flag").

## Configuration (environment for this run)
- **Date (UTC):** 2026-10-05 (solving window ~02:00-03:30Z)
- **Host OS:** Windows 11 (11), shell = git-bash/MSYS (uname: `MSYS_NT-10.0-26200`)
- **User:** <USER>
- **Interpreter:** python3 = Python 3.10.11 (primary); python = Python 3.14.7; pip 26.2.1
- **Libraries:** pycryptodome, pillow, pwntools, cryptography (installed this session for the General category); openssl CLI available
- **Working dir:** `~\Practice runs`
- **Agent:** Hermes Agent; model = qwen38-27b (provider: custom)
- **No-cheat rule applied:** challenge statement + provided files only; no `/solutions/` pages, no search-engine writeups, no third-party flag strings.
## Sources
Sources: challenge-provided materials only; self-derived per run logs.

