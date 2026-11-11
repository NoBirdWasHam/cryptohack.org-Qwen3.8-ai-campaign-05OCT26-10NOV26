# AAR — calm_down (HKCERT CTF 2020, CryptoHack archive, 0 pts)

Status: SOLVED. Flag submitted 2026-10-27, accepted (reconcile.py live
solved-list now contains `calm_down-hkcert_ctf2020`; score_delta 0 is
expected for a 0-pt archive challenge).

Flag: `hkcert20{c4lm_d0wn_4nd_s0lv3_th3_ch4llen9e}`
(full decrypted message: `Hey, congratulations on solving the challenge.
But please hkcert20{c4lm_d0wn_4nd_s0lv3_th3_ch4llen9e}.`)

## Vuln
Textbook RSA with a decryption oracle: `send <b64 ct>` decrypts and prints
'nice' iff plaintext's LAST BYTE == ord('.'), else 'nope' (exception
caught). Choosing ct = c*s^e mod n gives oracle YES(s) <=>
(s*m mod n) mod 256 == 46, i.e. one bit about q(s) = floor(s*m/n):
YES <=> 46(s-1) = q(s)*n (mod 256), using mu = m mod 256 = 46 — the joke:
the plaintext ends with a full-stop.

## Winning attack (solve4.py — boundary binary search, ~2.5k queries)
Restrict to aligned s = 128t+1: then 46(s-1) = 46·128t ≡ 0 (mod 256), so
YES(128t+1) <=> q(s) ≡ 0 (mod 256). In the region s*m < n (q=0) every
aligned probe is YES; q=1..2 give NOPE, so on the bracket P(t) = [s(t)*m < n]
is monotone:
- doubling probe t = 1,2,4,... to first NOPE t_hi (lands in the q∈{1,2}
  region; bracket lies inside (T/2, 2T) so no later q≡0 (mod 256) YES
  region can fool it);
- binary search first NOPE t* in (t_hi/2, t_hi]: m/n ∈ [1/s(t*), 1/s(t*-1));
- width·n = 128·m²/n << 1 -> unique integer candidate; verify pow(m,e,n)==c.
Remote: bracket 2^1227, 2455 queries total, 360 s, one session.
Validated first on a 1024-bit local clone (recovered planted flag in
1813 queries / 6.5 s).

## Failed/superseded path (solve2/solve3 — 256-window interval walk)
Blocks of 256 consecutive s near 256/w; each YES gives bin [q/s,(q+1)/s]
(~8 bits per 256 queries, ~65-70k queries needed for 2048-bit n). Worked
from w=1 to w~1e-320 (local_run.log) then STALLED forever at ~57k queries:
in the small-phi regime q(s) is constant across a 256-wide window and YES
requires that constant Q even (and aligned); for odd Q the same block
(s0 = f(w) only) is retried infinitely — root cause of the predecessor's
two hung runs. solve3.py adds a parity-slide fix (on miss, shift s0 by
s0/Q to flip Q parity) but was superseded by solve4 before re-validation.

## Limitations
- solve3's parity-slide fix was never validated end-to-end (superseded);
  solve4 is what was validated (local clone + remote pow-check).
- Boundary-search monotonicity is hand-derived, not machine-verified; the
  final pow(m,e,n)==c check is what certifies m.
- No cryptohack solutions/writeups consulted (flag-provenance rule held).
- Note: chall_local512.py actually generates a 1024-bit key (PyCryptodome
  rejects <1024; filename is historical).

## Files
- solve4.py — winning attack (`python3 solve4.py remote` / `local`)
- solve3.py — interval walk + parity-slide fix (backup)
- solve2.py, solve.py — earlier attempts (solve.py had mu=46 skip bug)
- chall_local.py, chall_local512.py (fast clone), mklocal.py
- local_bnd.log (local solve4 validation), remote_bnd.log (win),
  local512.log.dead (512-bit clone crash), local_run.log / remote_run.log
  (predecessor walk logs)
- flag_calm_down-hkcert_ctf2020.txt

---

<!-- AAR batch #9 quality upgrade (2026-11-02): publication sections appended; everything above this marker byte-identical to the pre-append AAR (hash in aar_batch9_pre.sha). -->

## Vulnerability (plain words)
Textbook RSA plus a decryption oracle with a one-bit answer: the server decrypts any ciphertext you send and prints 'nice' iff the plaintext's LAST byte is a full stop '.', else 'nope'. By multiplicativity, `ct = c * s^e mod n` decrypts to `s*m mod n`, so the oracle is a predicate on the quotient `q(s) = floor(s*m/n)` — it says where `s*m` sits relative to multiples of n. That is a continued-fraction-grade leak of `m/n`, and the joke supplies the key constant: the plaintext ends with '.', so `mu = m mod 256 = 46`.

## How the answer follows
1. Oracle identity: `YES(s)` iff `(s*m mod n) mod 256 == 46` iff `q(s)*n == 46*(s-1) (mod 256)`.
2. Restrict to aligned `s = 128t + 1`: then `46*(s-1) = 46*128t == 0 (mod 256)`, so `YES(128t+1)` iff `q(s) == 0 (mod 256)`. Every `s` with `s*m < n` (q=0) answers YES; q in {1,2} answers NOPE, so within the doubling bracket the predicate `[s(t)*m < n]` is monotone.
3. Probe `t = 1, 2, 4, ...` to the first NOPE `t_hi` (lands in the q in {1,2} region; the bracket sits inside (T/2, 2T) so no later q == 0 mod 256 YES-region can fool it), then binary-search the first NOPE `t*` in `(t_hi/2, t_hi]`, bracketing `m/n` in `[1/s(t*), 1/s(t*-1))`.
4. Bracket width `* n = 128*m^2/n << 1` => a unique integer candidate m; certified by `pow(m, e, n) == c`. Remote run: bracket at 2^1227, 2455 queries in 360 s in one session; m decrypts to the congratulations sentence containing `hkcert20{c4lm_d0wn_4nd_s0lv3_th3_ch4llen9e}`.
5. Pre-validation: the same attack (solve4.py) recovered a planted flag on a 1024-bit local clone in 1813 queries / 6.5 s before any remote probing beyond fingerprinting.

## Limitations / attempts that failed
- solve2/solve3 (256-window interval walk, ~8 bits per 256 queries, ~65-70k queries needed): worked from w=1 to w ~ 1e-320, then stalled forever at ~57k queries — in the small-phi regime q(s) is constant across a 256-wide window and YES requires that constant even (and aligned); for odd Q the same block is retried infinitely. Root cause of the predecessor's two hung runs. solve3's parity-slide fix was never validated end-to-end (superseded by solve4 before re-validation).
- solve.py had an `mu == 46` skip bug. Boundary-search monotonicity is hand-derived, not machine-verified — the final `pow(m,e,n)==c` check is what certifies m.
- `chall_local512.py` in fact generates a 1024-bit key (PyCryptodome rejects < 1024; filename is historical; local512.log.dead records the crash).

## Sources
- Self-derived per logs from the provided `chall.py` and local clones; no CryptoHack solutions/writeups consulted (flag-provenance rule held). Conceptually the oracle-abuse pattern is Bleichenbacher-style adaptive predicates on multiplicatively blinded RSA ciphertexts — named as public background, not consulted as a solve source.
- Upgrade-time comprehension check (batch #9, 2026-11-02): re-derived the mod-256 YES predicate and the doubling-bracket monotonicity from `solve4.py` and `local_bnd.log`/`remote_bnd.log`; no new queries or submissions.
