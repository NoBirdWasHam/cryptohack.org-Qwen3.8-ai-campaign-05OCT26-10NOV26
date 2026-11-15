# AAR — Challenge 13389: Collider (50 pts, hash functions → collisions)

**Date:** 2026-10-14 · **Status:** SOLVED (server-verified) · **Flag:** `[flag — recorded in FLAGS/hashes/challenge-13389-cryptohack-collider/flag.txt]`
**Delta:** +50 (7245 → 7295, 156 → 157 solved) · **Method:** self-solve from statement + provided `13389.py` + live probing. No solutions page, no writeups used.

## Vulnerability

The document system keys stored documents by MD5 and treats "same hash, different
content" as a crash that leaks the flag. Two facts decided the exploit:

1. **State is per-connection** (fresh `Challenge()` per socket), so a collision pair sent
   on two connections can never collide — and the two pre-stored docs' hash keys match
   their content exactly, so colliding *with them* would need a second preimage on MD5
   (~2^123, infeasible).
2. **The listener keeps the connection open and accepts multiple JSON lines per session.**
   Documents added early in the session are still in the dict later in the session.
   Within one connection: send A (added), then B with md5(B)=md5(A), B≠A → crash.

So a **generic** MD5 collision pair (not a second preimage) is all that's needed.

## Exploit steps (all performed)

1. Read `13389.py`. Verified from the real file (via `ast`) that
   `md5(stored_text) == stored_key` for both pre-stored docs → second-preimage path dead.
2. Live probes against `socket.cryptohack.org:13389`:
   - same random doc on two connections → "added" twice ⇒ per-connection state.
   - sending either stored text → "Document already exists in system" ⇒ live dict matches source.
3. Built an MD5 collision generator: downloaded Marc Stevens' hashclash `md5fastcoll`
   core (unmodified: block0/1*.cpp, md5.cpp, main.hpp), wrote a minimal boost-free
   `main_min.cpp` driver, compiled with mingw64 g++ (`-O2 -static`).
   Ran it: `msg1.bin`/`msg2.bin`, 128 B each, both md5 `3778dd67655b79828307612d215f560a`.
   Verified the pair locally with `hashlib.md5`.
4. One connection, two requests:
   ```
   → {"document": <msg1 hex>}   {"success": "Document 3778dd... added to system"}
   → {"document": <msg2 hex>}   {"error": "Document system crash, leaking flag: [flag — recorded in FLAGS/hashes/challenge-13389-cryptohack-collider/flag.txt]"}
   ```

## Verification

- Flag returned by the service in the crash response; re-ran `solve.py` end-to-end —
  reproduces the crash on a fresh connection.
- `submit_flag.py collider "crypto{...}"` → HTTP 200; API user endpoint confirms
  7245 → 7295 (+50), solved 156 → 157.

## Learning points

- **Always probe socket-challenge state lifetime before designing the exploit.**
  The per-connection vs per-session distinction turned an infeasible problem
  (second preimage, 2^123) into a trivial one (generic collision). The probe is cheap:
  send the same random input on two connections and compare "added" vs "already exists".
- **CryptoHack JSON-line listeners keep the connection open for multiple requests** —
  treat each session as a stateful conversation, not a one-shot RPC.
- **Generic MD5 collisions are a commodity** once you have md5fastcoll/hashclash built:
  seconds on a laptop, no GPU. Keep the built tool in the toolbox.
- When a service stores `hash → content`, check whether the stored keys actually match
  the stored contents (extract the real bytes from the source, don't trust a copy-pasted
  string). Consistent storage ⇒ only second preimages reach it; inconsistent storage
  (swapped/mismatched keys) ⇒ sending the stored content itself crashes it.

## Files

- `solve.py` — exploit (single connection, two JSON requests).
- `13389.py` — server source.
- `msg1.bin` / `msg2.bin` — collision pair (md5 `3778dd67655b79828307612d215f560a`).
- `md5fastcoll/` — generator source, minimal driver, built exe, `BUILD.md`.
- `flag.txt` — flag.

## Vulnerability (plain words)
The document system keys stored documents by MD5 and treats "same MD5, different content" as an internal crash that leaks the flag. The pre-stored documents' hash keys match their contents exactly, so colliding *with them* would require an MD5 second preimage (~2^123, infeasible) — but the listener keeps one connection open for multiple requests, and the document dict persists within a session. Therefore two documents with the same MD5 can simply be added one after the other on the **same connection**: a commodity generic MD5 collision pair is all the exploit needs.

## How the answer follows
1. Source check: `ast`-verified from the real `13389.py` that md5(stored_text) == stored_key for both pre-stored docs ⇒ second-preimage route provably dead before designing anything.
2. State-lifetime probes on `socket.cryptohack.org:13389`: same random document on two connections → "added" twice ⇒ state is per-connection (multi-connection plan void); sending a stored text → "Document already exists" ⇒ live dict matches the source.
3. Collision generation: Marc Stevens' hashclash `md5fastcoll` core compiled unmodified (block0/1*.cpp, md5.cpp, main.hpp + a minimal boost-free `main_min.cpp` driver, mingw64 g++ -O2 -static) → `msg1.bin`/`msg2.bin`, 128 B each, both md5 = `3778dd67655b79828307612d215f560a`, independently re-verified with `hashlib.md5`.
4. One connection, two JSON lines: msg1 → "Document 3778dd... added to system"; msg2 → `{"error": "Document system crash, leaking flag: [flag — recorded in FLAGS/hashes/challenge-13389-cryptohack-collider/flag.txt]"}` — flag handed over by the service.
5. Verification: `solve.py` reproduces the crash on a fresh connection; `submit_flag.py collider` → HTTP 200, API confirms 7245→7295 (+50), solved 156→157.

## Limitations / attempts that failed
The second-preimage path was eliminated by source verification rather than attempted; the naive two-connection plan was voided by the per-connection-state probe before it was exploited (probe evidence above). No further failed paths recorded in run logs — exploit worked first try against live.

## Sources
Provided server source `13389.py`; tool source: Marc Stevens' hashclash/md5fastcoll collision core (unmodified core, own driver — cited in the original AAR, `md5fastcoll/BUILD.md`); Python `hashlib` for verification. Method self-derived from statement + live probing; no solutions page, no writeups used.
