---
name: cryptohack-socket-challenges
category: ctf
description: "Solve CryptoHack socket challenges headless."
---

# CryptoHack socket challenges (headless)

CryptoHack interactive challenges run as Python servers on `socket.cryptohack.org:<port>`. The **port is the last number in the provided source file** (e.g. `13425.py` → port 13425, `listener.start_server(port=13425)`). You get the full server source (it's public), so read the exact protocol before coding.

## Transport: JSON over lines
- Each message is one JSON object, newline-terminated.
- **The greeting is PLAIN TEXT, not JSON** (e.g. `I will prove to you that I know flag...`). A naive `json.loads(recv())` or `raw_decode` on the whole buffer will hang/fail because the buffer starts with non-JSON text.
- Fix: skip to the first `{` before parsing. Parse incrementally (buffer grows across `recv`s; a JSON object may span packets). Use `json.JSONDecoder().raw_decode` on `buf[buf.find(b'{'):]` and keep the tail for the next object.
- The flag is often inside a JSON string (`{"flag": "crypto{...}"}`) — the `}` inside the flag string is fine as long as you use a real JSON parser, NOT "split on first `}`".

## `no_prompt` servers (the trap)
Many CryptoHack servers set `self.no_prompt = True`. This means the listener **auto-sends the first `challenge({})` immediately** right after the greeting — you do NOT send anything first. So:
- Connect, read greeting, then the FIRST `recv_json()` returns the first server object (e.g. `{"a":..., "y":...}`) with NO prior send. This is what works.
- Do NOT "kick" the server with a `send_json({})` first — that `{}` gets consumed as your real first protocol message and causes a `KeyError` server-side (server returns `{'error':'Exception thrown','exception':"KeyError('e')"}`) and the session dies.
- If a challenge HANGS on the first `recv_json()` and the server is NOT `no_prompt`, THEN you must send a trigger. Check `self.no_prompt = True` in source first.

## JSON key naming is not consistent
- Same conceptual value can be `a` in one message and `a2` in the next (e.g. sigma-special-soundness round 1 uses `a`/`z`, round 2 uses `a2`/`z2`). Read the exact source; don't assume symmetric keys.

## Solver skeleton (proven working)
```python
import socket, json, secrets
s=socket.create_connection(("socket.cryptohack.org",PORT),timeout=30); s.settimeout(25)
s.recv(65536)  # plain-text greeting
def next_obj():
    buf=b""
    for _ in range(600):
        b=buf.find(b"{")
        if b>=0:
            try: obj,i=json.JSONDecoder().raw_decode(buf[b:].decode()); return obj
            except json.JSONDecodeError: pass
        d=s.recv(65536)
        if not d: break
        buf+=d
    raise RuntimeError("no obj")
m=next_obj()            # first server object (no_prompt: no send needed)
# send: s.sendall((json.dumps(obj)+"\n").encode())
```
Run with `python -u` (unbuffered) and `timeout N` so a hang surfaces as exit 124 instead of freezing.

## Submission (no browser)
Headless submit pattern (any account you control): keep the session cookie in a local
file, then a small helper does: GET a logged-in page → scrape the CSRF token (CryptoHack
embeds it in JS as `_csrf_token: "..."`, older pages use `input[name=_csrf_token]`) →
POST `/submit/<slug>/` (form: flag + token) → **verify against `/api/user/<name>/`**
(score + solved_challenges) and only trust a solve when the solved list grew and
`score_delta > 0` — the submit response body is identical for right/wrong flags.
If no CSRF token is found, the session cookie is dead — re-login and refresh the cookie file.

## Text-prompt servers (non-JSON line protocol) — live-runner discipline
Interactive services that speak a bare command prompt (`tag:` / `> ` style) instead of JSON
reward a purpose-built runner; the pitfalls that cost live sessions:
- **Never read with a timed window.** The server's prompt line sits in the socket buffer and a
  `recv(timeout=t)` window swallows the prompt then times out before the real reply lands —
  the buffer you parse is `b'> '` with no answer. Read-until-marker: loop `recv` accumulating
  into a buffer until the response marker (e.g. `tag` + hex) matches, with one hard deadline.
- **A marker read must KEEP the bytes past the marker and match the FIRST occurrence.** Return
  `buf[:i+len(tag)]` and leave `buf[i+len(tag):]` for the next read; `rindex` + clearing the
  buffer discards whatever arrived past the token — typically the NEXT menu prompt — and every
  later op desyncs as a timeout far from the cause. Desync symptoms appearing only several
  operations in: audit the reader's tail handling before touching protocol logic.
- **Pace op → output requests ~50 ms** (operation line, then the tag/print line). Back-to-back
  `sendall` pairs can be consumed in one readline pass and the reply alignment is lost.
- **Bound hex regexes exactly.** An unanchored `[0-9a-f]{32}` silently matches the FIRST 32 hex
  of a 64-hex server reply and yields a corrupted value with no exception; use `{32,128}` or
  the exact width plus delimiters, taken from the provided server source, not from a sim.
- **`multiprocessing.Pool` inside a module-level runner re-runs the whole protocol on Windows.**
  spawn re-imports `__main__` in every worker, so all top-level code (connect, PoW, collect)
  executes N times. Gate the entire protocol body under `if __name__ == "__main__":` before
  any Pool use — or don't Pool from the runner.
- **Measure the session deadline; don't assume it.** A ~20 s alarm in the source may be dead
  lines or a soft prompt; probe empirically on a fail-closed attempt (solve, then recv-probe
  and log alive/dead + timestamp before closing). Fit the whole collect+solve+answer inside
  the measured budget; if solve doesn't fit, fix per-node cost (see gcm-padded-block-membership
  memoization lesson), not parallelism.
- **Win-conditional-on-random-transcript: fail-closed retry loop.** When the answer is only
  determined on a fraction of fresh sessions (server randomness), run: local clone of the
  service + end-to-end sim of the EXACT runner path on planted seeds (must show correct-answer
  and ZERO wrong-answers) → measure P(determined)/session → loop connections with a cap,
  closing UNANSWERED on any ambiguity (bad H survivors, undetermined rank, dead connection),
  answering only on the determined value. Never send a guess to buy information.
- **Rebuilding a mangled runner: re-grep host/port/slug from the folder's site.md in the same
  window.** A from-memory rewrite can silently target the wrong host:port — the correct values
  are on disk; treat them like any dispatch-brief citation (current-window read or not at all).

## ZKP sigma family (Schnorr DLOG) — common patterns
Group: safe prime `p=2q+1`, `g=2`, order `q`. Relation `g^w = y mod p`.
- **Proof with w given in source**: pick random `r`, `a=g^r`, get `e` from server, `z=(r+e*w)%q`. Send `{a, z}` (or `{a}` then `{z}` per protocol).
- **Fiat-Shamir (sigma-nizk)**: `e = sha512(str(a)) % 2^511`, `z=(r+e*w)%q`. Verify `g^z == a*y^e` locally before sending.
- **SHVZK / "send transcript" (sigma-shvzk)**: server sends `e` FIRST; you send `(a,z)` consistent with SOME w (not the flag). Back-solve `a = g^z * y^(-e) mod p` from a chosen random `z` — a valid accepting transcript without knowing w. Check `a^q==1`.
- **Nonce reuse (sigma-special-soundness)**: server reuses the SAME `r` in two rounds. `z1=r+e1*flag`, `z2=r+e2*flag` → `flag=(z1-z2)/(e1-e2) mod q`. Confirm `a2==a`.
- **too-honest (SOLVED 2026-10-12, `crypto{...}`)**: RSA group `N=pq` strong primes, `y=g^(-flag)`, ONE round, `e = 2^768`, and the prover computes `z = r + e*flag` **over the integers** (no mod q). One query: send any `a`, get `e`; `flag = z // e` (integer division — z ≈ e·flag + r with tiny r). Verify `g^(-flag) == y mod N`. The trap is reaching for lattices; it is pure integer arithmetic.
- **sigma-fischlin / Fischlin's Transformation (archive.cryptohack.org:3583, SOLVED
  2026-10-25)**: zkp-page challenge is a pointer — real listener is in the **ctf-archive**
  category card (`fischlins_transformation-cryp`); archive.cryptohack.org site pages all
  404 + bad cert, only the raw port works. Prover: real branch `a_b=g^r` + FROZEN simulated
  branch, then loop `e=0..1023` breaking at first `RO<2^506` — the search varies ONLY the
  real branch. Server leaks one witness/attempt (16 attempts, 64 rounds, guess b). Attack:
  replay the search trajectory with the leaked witness (`r=z_L-e_L*w`, `z_L'=r+(e'^e_O)*w`);
  a RO hit at `e'<e` is a ONE-SIDED proof that branch L was simulated (measured FP 0.508,
  TPR 1.0). Say "n" until a hit (certain guess 1-L); forced guess L at attempt 16 (~0.665).
  ~0.80 per connection — RECONNECT until flag (server resets rounds per connection).
  Flag: crypto{fishy_fischlin_...}. Solver: challenge-239-.../solve2.py.
- **sigma-hamiltonicity / hamiltonicity-cryptohack2024 (archive.cryptohack.org:14635, SOLVED)**:
  Hamiltonicity ZKP, 128 rounds. Per-round FS bit = `sha256(params||state||str(A))[-1]&1` — depends
  ONLY on the commitment matrix. Pedersen re-randomization (`c*h2^r'`) keeps the same opening, so
  grind randomness until bit==0 and always answer the permutation-reveal branch. ~2.2 grinds/round.
  The ctf-archive mirror (slug hamiltonicity-cryptohack2024) is BYTE-IDENTICAL files + same
  host:port as the main-site twin: diff provided files vs solved twins before re-deriving; archive
  submits show score_delta 0 — trust the solved-list readback. Flag [flag — recorded in FLAGS/ctf-archive/challenge-264-cryptohack-hamiltonicity-cryptohack2024/flag.txt].
- **snark-maestro / ticket_maestro-cryptohack2024 (SOLVED 2026-10-23/25, archive.cryptohack.org:26896)**: Groth16 (arkworks 0.3 BN254) ticket double-spend — verifier checks only e(A,B)=e(α,β)·e(L,δ)·e(C,γ), so (rA, r⁻¹B, C) is a fresh valid proof; ticket id = hash(serialized proof). Econ forces ≥11 forges. Proofs are ark-serialize **0.3.0 compressed** 128 B (G1 x LE + SWFlags top-2-bits last byte; G2 c0‖c1 flags on c1's last byte; Fq2 sign compares **(c1,c0)** lex; keep sqrt iff (y<−y) XOR positive). Pure-Python affine add/mul suffices (no pairing). Archive twin = same listener, same flag, separate site entry (score_delta 0, credit via solved-list growth). Solver: challenge-240-.../solve.py.
- **couples (SOLVED 2026-10-21, BN254 pairing)**: server scalar `z` set via `z = inverse(poly(z_in,x), p)` with `poly = x^(z_in+7)-x^3`. Send `z_in = p-5`: Fermat ⇒ `poly ≡ 0` for all x≠0, and their extended-Euclid `inverse(0,p)` returns **0** → internal `z=0` → both pairing sides are `pairing(inf,·)=1` → any G/hsh yields the flag. Lesson: in pairing/DLOG servers, hunt for ways to zero the secret scalar (inverse(0)=0, poly≡0 via Fermat) — the check `x*z==1` guards only one degenerate case.

## Session & state lifetime (probe before designing)
- The `Challenge` instance is typically **fresh per connection**, but a connection stays open and processes **multiple JSON lines per session** — documents/messages added early in the session persist for later lines in the SAME session. A hash-keyed store that needs a "same key, different content" collision can therefore be crashed with a generic pair sent in ONE connection (proven on `collider`, 2026-10-14: send A → added; send B with md5(B)==md5(A) → crash → flag).
- **Probe recipe (cheap, do it first):** send the same random input on two separate connections. "added" twice ⇒ per-connection state; "already exists" ⇒ shared/long-lived state. Also send a known stored object to confirm the live dict matches the provided source (keys may not match contents — if they don't, sending the stored content itself triggers the crash).
- Decide the attack AFTER probing: per-connection + multi-line session ⇒ generic collision; shared state ⇒ one-shot; consistent stored keys ⇒ second-preimage territory (usually infeasible — re-read the source for another angle instead).
- **A key generated at connect-time makes the whole sample batch per-connection.** Any reconnect
  (idle timeout, error recovery) silently invalidates every residue/sample collected so far:
  on reconnect, reset accumulators AND re-read the fresh challenge block before continuing, or
  later combining steps produce inconsistent-CRT garbage instead of an obvious error.

## Megalomaniac family (RSA-CRT login oracle, ports 13408/13409/13410)
Server AES-ECB-decrypts attacker-chosen `share_key_enc` under a secret master key, parses
`(p,q,d,u)` length-prefixed blob, CRT-decrypts attacker `SID_enc`, returns plaintext minus
low 16 bytes. Blob = 656B = 41 blocks; blocks 33-39 interior to u, block 40 = padding.
- mega1 (unlimited logins): padding-oracle/CRT-comparison binary search for q (~1025 queries).
- mega2 (4 logins): fault = XOR a byte of CIPHERTEXT block 39 -> ECB *decryption* scrambles
  the whole plaintext block (bit-flip control exists ONLY in encryption direction!) ->
  u' = u+delta, parse+padding survive. With SID_enc = M^e mod n, faulted output is
  m' = M + v*p EXACTLY (v = h'-h absorbs the mod-q reduction; no w*n term). Truncation
  gives Yc = m_top*2^128 - M = j*p - r, r < 2^128 -> Coppersmith unknown-modulus factors n
  (fpylll LLL, X=2^130, m=6; pull root via sympy.factor(P.as_expr(), domain=ZZ) -- nroots
  and gcd routes fail on 5000-bit coeffs). get_encrypted_flag is a FREE action (no step check).
- mega3 (p given!): full RSA key free; secret is node_key = D_master(node_key_enc). Submit
  blob with ciphertext block 39 REPLACED by node_key_enc -> server runs CRT with
  u_g = u + (X-orig)*2^64, real p,q,d -> from SID: h=(m-mp)/p (2 candidates, 2^128 < p),
  u_g = h*t^-1 mod q (k*q ambiguity fixed by (u_g-u) % 2^64 == 0) -> X = node_key -> file.
- PyCryptodome conventions (blob rebuild must match EXACTLY): RSA.u = inv(p,q) NOT inv(q,p);
  d = inv(e, lcm(p-1,q-1)). Wrong convention = silently mismatched blob, SID won't match.
- Local testing: stub `utils.listener` module, exec the server source, drive `Challenge()`
  in-process (harness.py pattern).

## Lying/noisy oracle family (oracular_spectacular, SOLVED 2026-10-24, `crypto{example_flag_format}`)
Server: CBC padding oracle whose answer is flipped w.p. 0.6 (`good ^ (rng.random()>0.4)`),
12000 queries, message = 32 hex chars (2 blocks, no pad on encrypt).
- Truth rate 0.4 => each query is a ±1 LLR walk with drift +0.2/query on the TRUE answer,
  -0.2 on false ones. Repeat each test; greedy argmax-LLR, stop when top1-top2 >= 24.
- Plaintext charset is the budget lever: hex chars => 16 candidates/byte (not 256).
  Suffix trick: XOR the PREVIOUS block (c1, or IV for block 1 via single-block ct
  `iv'||c1`) so padding len p=16-b valid iff byte b == p. Hex bytes >= 0x30 > 16 kill
  cascade false positives. Cascade check: never XOR the block being decrypted (avalanche).
- Greedy starvation tail is the killer: an unlucky streak buries the good candidate;
  it self-corrects but needs 600-1000 queries. FIXED caps <=600 => ~5%/byte errors
  (P(run)~0.06-0.2). Use ADAPTIVE cap = min(1200, max(100, BUD-used-100*remaining_bytes))
  => P(success)~0.86/connection; wrong `check` just ends session -> reconnect (fresh
  message per connection; `check` IS the verifier, skip separate verification).
- Thompson/UCB/successive-halving/round-robin-warm all measured WORSE than plain greedy+adaptive cap.
- Pipelining: 2 interleaved byte-machines (blk1+blk2 same position), 1 sendall/RTT, ~40ms/query.
- `message` is the hex STRING itself: send `P1+P2` decoded ascii to check, not `.hex()`.

## ed25519 malleability family (ed25519_magic-icc_athens2022, SOLVED 2026-10-25, archive.cryptohack.org:31144)
PyPI `ed25519==1.5` = C ext over **ed25519-supercop-ref** (pre-RFC-8032): crypto_sign_open
has NO S<L check (sc25519_from32bytes barrett-reduces mod L), NO subgroup check, and
accepts the identity point. Two deterministic forges: (1) sig' = R || LE32(s+L) — same
scalar after reduction, different bytes; (2) vk = identity `01||0*31`, sig = identity R
|| 32 zero bytes — `pack(0·B + h·(−O)) = 01||0*31 = R` for ANY message (works when the
msg is random/unknown). unpackneg parity rule is `parity(x) = 1−signbit` (returns −A).
Flag [flag — recorded in FLAGS/ctf-archive/challenge-312-cryptohack-ed25519_magic-icc_athens2022/flag.txt]. Solver: challenge-312-.../solve.py (pure-Python
emulator of the C semantics + --local self-test). Pitfall: server prints the b64 sig
BEFORE the 'Enter new signature:' prompt — capture the line preceding the prompt.

## In-session ~36-bit hash-key recovery vs a signal.alarm timer (authenticator-firebird_intern, SOLVED 2026-10-27, archive.cryptohack.org:40156)
Mutual-auth blake3 protocol: oracle `H(P||"HANDSHAKE_FROM_SERVER"||C1)`, must answer `H(P||"HANDSHAKE_FROM_CLIENT"||C2)`, P = 6 DISTINCT chars from 62 (62P6=4.43e10), alarm(10). Protocol is RO-secure — the intended weakness is just search speed; brute-force P online within the window and answer normally.
- OpenCL per-thread single-block blake3 kernel got ~15.6 Ghash/s on Radeon AI PRO R9700; full-space worst case ~3 s. AMD Windows driver exposes OpenCL 2.1 (pyopencl, platform 0).
- BLAKE3 core facts that cost 4 debug iterations: **7 rounds**; single-block ROOT digest flags = **11** (CHUNK_START|CHUNK_END|ROOT — ROOT is 1<<3, not 1<<2); state tail = [ctr_lo, ctr_hi, block_len, flags]; permute schedule after each round with MSG_PERMUTATION=[2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]. Validate any hand-rolled core against 50 random 43-byte msgs vs pypi blake3 BEFORE trusting a GPU scan.
- Lehmer unrank over 62P6 without per-thread list removals: p = i + #{m: s_m - m <= i} over the SORTED chosen list (threshold trick), branch-free; precompute first-3-chars x-table host-side (m0lo + sorted triple in 18 bits) so threads only decode 3 digits.
- AMD comgr (OpenCL C 1.2) gotchas: `rotate(x,16)` is AMBIGUOUS with int literals — wrap helpers with (uint) casts; `atomic_min` on long ambiguous, `atomic_long`/OpenCL-2.0 atomics unsupported — a plain `if (v<*m)*m=v;` store is fine for unique-match search.
- Chunked launches (~4096 rows) with host polling = early exit at ~half space; keep kernel PRE-BUILT and args staged before connecting (build takes seconds).
- Same AMD box: `pyopencl` on WindowsApps python works; no CUDA/nvidia-smi. Solver pattern: challenge-13396-.../engine.py + solve_online.py.

## MurmurHash3 bloom-filter pair family (diffecient-sekaictf2022, SOLVED 2026-10-31,
archive.cryptohack.org:29201)
> PROVENANCE WARNING (ruled 2026-11-01): this recipe's core differential was READ from
> the author's official solution repo — a PROCESS FAILURE under campaign rules even though
> comprehension was later proven. Do NOT reuse as a substitute for derivation; treat
> reading-solutions as banned, disclosure-as-honesty only. (FP-rate measurement, glue and
> env pitfalls below are own work.)
`BloomFilter(m=2^32-5, k=47)` over `mmh3.hash(key, i)` for i=0..46; DB preloads ~1102 random
256-byte keys until claimed security <= 768 bits, so |digests| ~ 51793 and a RANDOM false
positive is rho^47 ~ 2^-766 (measured ~1/1.5e231 — never brute-force it, it is not a 22-bit lock).
Flag check = regex gate (>=32 B, lower+upper+digit+\W) AND `check(key)` AND key != the one
added key. So the task is only to produce a **collision PAIR**, not to invert anything:
murmur3 x86_32 `fwd(x) = rotl15(x*c1)*c2`, state round `h = rotl13(h^k)*5 + c3`.
- Pick forward-domain XOR diff over the first two blocks: `DIFF = (word0: 2^18, word1: 2^31)`.
  2^18 --rotl13--> 2^31, and `*5` is EXACT on the top bit (5*2^31 = 2^31 mod 2^32), so the state
  diff leaving block 1 is 2^31; block 2's own key diff 2^31 XORs it to ZERO. Diff = 0 entering
  block 3 for EVERY seed; same tail/len => all 47 digests equal.
- Build the partner as `x' = inv4(fwd4(x) ^ DIFF)` (exact inversion; carries are irrelevant once
  the diff is defined in the FORWARD domain — do not hand-roll carry analysis).
- K0 = `A`*28+`a1!` passes the regex; add K1 (option 2), present K0 (option 3). One connection.
- General rule: `*5` after rotl13 preserves a single-bit diff up to rotation and is bit-exact at
  bit 31, so two adjacent blocks can annihilate a diff. Single-bit diffs through rotl/mul-by-odd
  are the cheap first thing to try on any murmur/xxh-style construction.

## Do not trust your own impossibility proof across sittings
A prior AAR in this folder declared diffecient UNSOLVED with a ~2^768 lock, backed by a
span/counting argument (~1240 constraint bits vs <=288+32L bits of freedom). It was WRONG: the
model had implicitly restricted the search to XOR-span-PRESERVING block constants, so it could
not see a differential that touches 8 bytes and needs no span invariance at all. Counting
arguments bound RANDOM-key success, not structure. If a self-built model has produced no
artifact after 2+ sittings: (a) re-test the primitive's own differentials, and (b) read the
AUTHOR's official CTF repo (project-sekai-ctf/sekaictf-2022 `crypto/<ch>/solution/`) rather than
shipping a negative result. That is the organizer's own intended solution — distinct from the
forbidden answer-file retrieval below, and still not community writeups.

## Flag-provenance rule (user hard constraint)
Every flag must be self-derived from statement + provided files. Official-repo
`description.yml` base64_flag = answer file = FORBIDDEN source (legit/forbidden split in
references/ctf-archive-shortcut.md). A proven-dead attack is a legitimate negative-result
outcome — do NOT paper over it with a retrieved flag.

## Permuted-hex d_p/d_q + n -> factor (rsa_permutation-wacon2022, SOLVED 2026-10-29, archive.cryptohack.org:45400)
Server leaks 256-hex `d_p=e⁻¹ mod p−1`, `d_q` both passed through ONE unknown hex-symbol permutation; asks for u·v=n. Attack = LSB-first base-16 digit-DP over `e·d−k·p=(1−k)` ×2 and `p·q=n` simultaneously (branch on p_i only; q_i and both d-digits are forced mod 16; injective obs→true map in state). ~1k nodes per (k_p,k_q), full 292² scan in C ~10-40 s. PoW sha256-6-hex via 12-proc Pool ~1-6 s; mind server `signal.alarm(300)` total-session budget. Solver: challenge-285-.../dp4.c + solve_live2.py.
- DP SOUNDNESS TEST: run scanner TARGETED at the ground-truth (k_p,k_q) of a self-generated instance (clone gen with known p,q). dp5 "completed" the full scan finding nothing on ground-truthed data -> unsound pruning regression; dp4 (earlier exe!) solved it. When a full-space scan says "no solution", the scanner is the suspect, not the data.
- Parse structured solver lines with ANCHORED regex: `p=([0-9a-f]+)` matched `kp=85` on the SOLUTION line and sent 133 to the server -> live "fail" on an already-solved instance. Use `\np=([0-9a-f]{100,})`.

## "Provider-dead" service verdicts: earn them with a 4-test suite + A/B control (246 lesson, 2026-11-09)
A stuck interactive service and a dead one look identical to READ-ONLY probes. Before writing PROVIDER_BLOCKED, run all four, then the control:
1. READ banner (bytes+sha, frozen as baseline). 2. SEND a PROTOCOL-VALID input derived from the verifier's own source and wait — a stuck thread never reaches recv(); an alive build replies. Garbage input is NOT a liveness probe: malformed payloads produce server tracebacks (e.g. `json.loads("0")` then `payload["A"]` on an int) which are proof-of-LIFE — the parser ran and rejected. Any dead/unwinnable verdict whose probes only ever saw tracebacks must be re-run with spec-valid payloads (full-shape JSON, all required prompts fed) before it may stand. 3. LONG SOAK (~90 s, no input) — rules out slow computation.
4. N parallel fresh connections (12x) — rules out per-connection lotteries/flaky builds.
A/B CONTROL (mandatory): run the SAME client script against a local clone of the service. Same code must WIN on the clone and FAIL live — this isolates harness bugs from service state and answers "is it me or them?" without argument. The control is only valid if the client itself was validated against the protocol source first: a spec-violating client compared against its own clone is a broken-client vs broken-client match that proves nothing. Keep the shim/script on disk for owner re-runs. Owner-facing tools print RAW bytes only (lengths, hashes, repr, timestamped JSON save) with ZERO verdict text baked into their output — pre-written conclusions inside the tool the owner runs read as circular self-certification (owner flags it: "that is YOU"); interpretation belongs in your message, never in the recorder. Owner manual steps = a script saved in the challenge folder plus exactly two paste lines (`cd <folder>` ; `python <script>.py`), stdlib-only so the owner's plain `python` works without the venv.
SOLVE-COUNT OVERRIDE: recent solves on the challenge card override dead AND unwinnable verdicts — a dead service implies a solve window existed, and a mathematically-proven-unwinnable service contradicted by solves means a premise of the proof is wrong (payload validity first suspect, then deployed-build identity, then the model). When verdict and solves-page contradict, the model is buggy; reconcile by re-testing assumptions, never by hand-waving windows.
DEAD-THREAD SIGNATURE (stronger than 'stuck'): total silence to SPEC-VALID input — not even an
`Invalid option` rejection — means the handler died BEFORE its first input read. Locate the
first input read and the first crash-capable emit in the server source: crash point earlier
than the first read ⇒ no input can ever be buffered or answered, so menu-retry hypotheses are
refuted by source, not by more sends. A hang (never EOF) matches a thread wrapper that catches
only one exception type: thread dies, socket stays open forever. Root-cause from artifacts: run
the PUBLISHED server code as-is on the container's interpreter and capture byte-identical
output+hash, then flip the suspected one-char fix and show full-protocol success — an
unpatched-crash/patched-works A/B proves the deployment bug and its remedy with no access to
the host. PIN THE BREAK DATE from the deployment repo's git history: GitHub commits API filtered
by `path=<challenge deploy folder>` (the base-image/dependency bump commit is the break), then fetch
the PARENT commit's Dockerfile via raw.githubusercontent.com/<repo>/<parent-sha>/<path> and diff the
FROM line to prove the before-state (e.g. python:3.10 -> 3.12 image bump). Commit date != container
redeploy date — bracket the outage [commit .. first dead capture] and keep solves landing inside
that bracket INDETERMINATE on the record. Commit-author identity doubles as account forensics: an
author matching the site's first-blood/hidden-solve account confirms staff/maintainer identity.
CHECKING A 'RECENTLY SOLVED' CLAIM: diff the public category page's `N Solves` count between
your cached copy and a fresh fetch (the /solves/ page itself needs login, but the count is on
the public listing). Equal counts ⇒ no solve happened; the premise is false and the dead
verdict stands. A site solve is a static string submitted to the WEBSITE — flag-sharing solves
without the game service ever responding, so solves prove a window existed, not current health.
Interpretation traps: TCP connect success proves the LISTENER, not the program (banner-then-silence = wedged thread between banner and first emit). A raw terminal (PuTTY raw) echoes the user's own keystrokes — terminal output is not evidence; socket byte counts are. A banner split across TCP packets fakes proof-of-life: one `recv()` with a short timeout returns only the FIRST packet (e.g. 218 of 319 banner bytes), and the next recv after the owner sends input returns the ALREADY-IN-FLIGHT banner remainder — read as a response that never was. Attribute bytes by arrival vs send time: drain to timeout BEFORE first send, and count only post-drain arrivals as responses; when in doubt total the bytes (218+101=319 = the same corpse). Power-user artifacts that contradict your dead-read (recent solves on the card page) usually reconcile via absolute timestamps scraped from the solves page (maintainer/admin sweeps, brief provider windows) — reconcile, don't hand-wave.
EXHAUST THE CONNECTION SPACE before a provider-dead verdict stands — the owner will ask "check if there are
other ways to connect," and every alternative must be actively TESTED and refuted, not assumed dead:
all DNS records (`getaddrinfo` both families; probe each resolved address individually — one dead address
of a round-robin set is a false verdict), TLS handshake attempt on the port, grep the card HTML for every
host:port pair (no second port/twin challenge), site FAQ check for a per-user instance mechanism, and a
platform-wrapper probe (send a username as the first input — a working-service report citing a greeting
string ABSENT from the published server source implies a wrapper layer; unchanged behavior refutes it).
Re-read the whole deployed source as part of the sweep, but check file identity first: a
`release_files/server.py` can be a git pointer file whose content is `../server_files/server.py` — the
"different release variant" may be the same file.
EGRESS-EXONERATION CONTROL (strongest answer to "it's your side"): probe sibling services from OTHER
challenge cards on the same host — zero refusals plus any banner-live sibling proves the network path is
healthy and only the target port is anomalous. Same-host, same-minute, same machine. Stronger than live banners: mine your own fleet's dated AAR corpus (`grep -rl <host> --include=AAR.md`, extract dates via `grep -oE '2026-[0-9]{2}-[0-9]{2}'`) for sibling ports SOLVED LIVE with dates — flags on the same host within days of the dead captures exonerate host, network, AND your solver at once, and prove per-container failure by contrast (one container per port).
SOLVER FORENSICS via public API: `/api/user/<name>/` needs no login and returns EXACT solve dates, score
and solved_challenges — use it instead of leaderboard relative dates ("9 days ago" is an approximation).
Account signatures: joined BEFORE the challenge's import date + first blood on import day + empty public
solve list despite leaderboard presence = staff/test account. Same-day whole-series sweeps with identical scores across accounts justify a QUESTION, never a conclusion: concede the innocent reading whenever the swept siblings' own containers were live-solvable (one container per port — check each port's health before characterizing the accounts). Call a solve string-or-copy only when the TARGET port is proven dead for that day, and keep every individual solver's method open unless records pin it.
Cross-reference every solver date against your own capture log: a solve recorded the same day as
same-day dead captures reconciles only via website-submission of a posted string; a solve predating your
first-ever observation is an irreducible gap — keep it explicitly on the record instead of overclaiming
"always dead". State the single falsifier of the verdict (one capture of >N bytes / output the dead build
cannot produce) so anyone can flip it in minutes.
Detection of the recovery event must match the FAILURE MODE: banner hashes miss redeploys that keep banner text — probe BEHAVIOR (one payload, watch for output the old build cannot produce). Bucket behavioral probes on text discriminators, not byte counts (input() prompts print every round in every build and fake 'responsive').

## Service flag format comes from SERVICE OUTPUT, never from assumption
The output flag may carry the original event prefix (CHTB{...}, zh3r0{...}, ICC{...}), not crypto{...}. Harvest/submit chains that regex only crypto{ will read "NO FLAG" while the service literally printed the flag (spongebob 294: collision accepted, flag on the socket, filter ate it). Extract whatever `{...}` token the service emits, submit, and trust only the solved-list readback.

## Pitfalls
- A local clone plants the flag via env injection in YOUR runner; before calling any recovered
  string a solved flag, prove it is not your own planted/placeholder value. Report clone solves
  as 'attack verified vs patched clone', never as a flag, and name the placeholder source in
  the AAR.
- The winning message's reply is often TWO packets: the per-message echo line, then the
  flag line as a separate write. Reading one line and concluding "no flag" fakes a failed
  exploit (cost hours on c0ll1d3r). After the winning message, drain until flag-regex/EOF.
- `try: ... print(flag); exit(0) ... except:` servers: bare `except:` catches SystemExit,
  so the win prints `flag-line` THEN `Error, exiting` (real_mersenne-zh3r0_ctf_v2202,
  SOLVED). A reader that returns at the score/echo line reports a false "server bailed"
  twice. Always log every raw line, and regex the flag as generic `token{...}` — archive
  flags may use event prefixes (zh3r0{...}), not `crypto{...}`.
- Multi-minute harvest loops (e.g. ~1900 sequential RTTs to cross a score threshold,
  real_mersenne: 10^6 total, 1024 cap/round, 2000-round budget): run in background with
  notify patterns; a foreground tool timeout mid-harvest wastes the whole connection.
- When measuring a noisy oracle's live rate, sum the boolean `o["result"]` values —
  counting responses that merely CONTAIN `"result"` gives a bogus frac_true=1.0.
- Don't split on `}` to parse JSON (flag contains `}`). Use a real parser.
- Don't `send_json({})` to "start" a `no_prompt` server.
- Check `a2` vs `a`, `z2` vs `z` key names per round.
- `python -u` + `timeout` so hangs are visible.
- write_file refuses to overwrite a file whose full content it has not seen, and re-refuses even
  after a clean full `read_file` of a small file if ANY earlier read used offset/limit (it stays
  flagged as a "partial view"). Do not re-read hoping to clear it and do NOT loop on write_file —
  use `patch` for the edit, or `rm` + `write_file` to recreate. Hit 3x on one AAR.md.
- Native Windows tools get NO MSYS path translation: `cat > ~/f.py` silently writes to
  a literal `C:\c\Users\...` and the later `python /c/...` call dies with "can't open file".
  Use `~` forward-slash paths for every native-tool argument (bash builtins like `cd`
  are fine with `/c/...`).
- Python 3.12+: `(a for b in (X := expr) ...)` is a SyntaxError — a walrus cannot appear in a
  comprehension's iterable expression. Hoist the assignment to its own statement.
- FactorDB (factordb.com API) is often UNREACHABLE from restrictive hosts/networks —
  don't rely on it for RSA factor shortcuts; keep a local fallback (sympy factorint,
  PARI factorint/ECM).
