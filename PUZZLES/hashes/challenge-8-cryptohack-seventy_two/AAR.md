# AAR — Challenge 139: Seventy-Two (50 pts, hashes → key derivation)

**Date:** 2026-10-14 · **Status:** SOLVED (server-verified) · **Flag:** `[flag — recorded in FLAGS/hashes/challenge-8-cryptohack-seventy_two/flag.txt]`
**Delta:** +50 (7195 → 7245, 155 → 156 solved) · **Method:** self-solve from statement + provided `13433.py`. No solutions page, no writeups.

## Vulnerability

The server binds credentials as `material = f"{TENANT}|{username}|{password}"` and stores
`bcrypt.hashpw(material, gensalt(cost=8))`. **bcrypt silently uses only the first 72 bytes
of its input** (the C implementation's `EXTRACT_SALT`/password loop bound) — the "Seventy-Two"
of the title.

Effective entropy per account = `72 − len("TENANT|user|")` bytes of the 32-char random
password (charset = 62 alnum):

| account | len("TENANT\|user\|") | effective pw bytes | search space |
|---|---|---|---|
| root | 42 | 30 | 62^30 — infeasible |
| backup@corp.bluerock.example | 66 | 6 | 5.7×10^10 — infeasible |
| m.laurent@corp.bluerock.example | 69 | 3 | 238,328 — feasible |
| **k.barrymore@corp.bluerock.example** | **71** | **1** | **62 — trivial** |

The directory service's own tenant/account binding is what creates the win: the long
Bluerock email usernames eat the 72-byte budget. `k.barrymore@...` leaves exactly **one**
password byte in the hash, so the stored hash is determined by a single character.

## Exploit

Login protocol (CryptoHack JSON-line socket listener): server sends a `before_input` JSON
line (tenant, accounts, hint); client sends one JSON line `{"username": ..., "password": ...}`;
server replies `{"msg": "Authentication failed."}` or
`{"msg": "Signed in as <user>. Flag: crypto{...}"}`. One attempt per connection.

`solve.py`: for each of the 62 charset chars `c`, open a connection and log in as
`k.barrymore@corp.bluerock.example` with password `c` (1 byte — exactly fills the 72-byte
window: 71 prefix + 1). When `c == real_password[0]`, the 72-byte material matches the
stored hash byte-for-byte → bcrypt `checkpw` succeeds.

**Result:** hit at guess 51 (`c = 'Y'`) after ~25 s of sequential connections (each attempt
costs one server-side cost-8 bcrypt, ~0.3–0.4 s).

## Verification

- Flag returned by the service in the success response.
- `submit_flag.py seventy_two "crypto{...}"` → HTTP 200 "Flag submitted"; API user endpoint
  confirms score 7195 → 7245 (+50) and solved 155 → 156.

## Learning points

- **bcrypt's 72-byte input limit is a real, exploitable design flaw** (not just a lint
  warning): any scheme that concatenates identifiers into the bcrypt input gets its
  effective key material silently truncated. The fix is to hash the components (e.g.,
  HMAC/SHA-256 of the full material) or use a modern KDF (Argon2id, as the statement hints)
  with no such truncation.
- When a service concatenates `tenant|user|password` for a KDF, **compute the prefix length
  for every account** — the longest username minimizes the effective password space.
  Here the challenge was literally designed so one account sits 1 byte under the limit.
- Socket-listener challenges: probe the protocol once (`before_input` line, single JSON
  request, JSON response) before writing the loop; the listener gives one shot per
  connection, so sequential connections are the natural brute-force shape.

## Files

- `solve.py` — exploit (62 sequential logins; `probe` mode prints the before_input).
- `13433.py` — server source (provided by the challenge).
- `statement.txt` / `site.md` — statement and metadata.
- `flag.txt` — flag.

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
