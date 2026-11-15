# AAR — import numpy as MT (Zh3r0 CTF V2), cryptohack slug `import_numpy_as_mt-zh3r0_ctf`

## Vulnerability
`challenge.py` seeds numpy's legacy `RandomState` (Mersenne Twister 19937) with a
**32-bit** seed (`random.seed(rand_32())`), then derives AES-CBC `iv,key` from
`random.bytes(16)` twice. The MT19937 stream is fully determined by the 32-bit seed,
and the iv is transmitted in the clear — so the seed (hence the key) is recoverable.
The author's "double encryption so people don't bruteforce it" only doubles the work:
each AES layer is peeled independently, outermost first.
Note `pad()` runs ONCE before the loop: round 2 encrypts `iv1||ct1` **unpadded**
(unpadding the outer plaintext is wrong — cost two debug cycles).

## Attack
1. `random.bytes(16)` = 4 uint32 MT words, **little-endian per word** (verified against
   local numpy 1.23.5: `bytes(16)` == LE-pack of `randint(2**32)` words).
2. numpy seeds via `init_genrand`: `A[0]=seed`, `A[i]=1812433253*(A[i-1]^(A[i-1]>>30))+i`,
   and **twists before the first output** (pos starts at 624). So observed word_i =
   `temper(T[i])` where `T[i] = A[(i+397)%624] ^ f((A[i]&U)|(A[i+1]&L))` — canonical
   out-of-place twist (verified exactly against a live RandomState).
3. Untemper the 4 iv words → T[0..3]. Every `A[0..8]` and `A[397..400]` is a pure
   function of the seed, so brute-force all 2^32 seeds checking the 4 twist equations
   (`mtbrute.c`, OpenMP + 4-way ILP chains, ~100 s full scan). 4 equations ≈ 128 bits
   of constraint → no false positives; confirmed by regenerating iv from the seed.
4. Regenerate `iv2,key2` from seed2 → CBC-decrypt outer layer → strip PKCS#7 →
   `iv1||ct1`. Repeat seed recovery on iv1 → `key1` → decrypt → flag.

## Key numbers
- Seed space 2^32 per layer; scan ~100 s/layer single machine.
- Listener: archive.cryptohack.org 7265; output = hex(iv2 || AES-CBC2(pad(iv1||AES-CBC1(pad(flag))))).

## Learning points
- numpy legacy `RandomState` ≠ CPython `random`: same MT19937 core, but `bytes()` is
  LE-per-word and the first output comes **after** an initial twist — untemper(word0)
  is NOT the seed directly; you must model the twist (or brute the recurrence).
- The init_genrand recurrence is a bijection chain: any post-twist word is a function
  of the 32-bit seed alone, turning "state recovery" into a cheap 2^32 scan with
  early-exit checks instead of 624-word untempering.
- Don't paste hex from truncated terminal previews into scripts — fetch to a file.

## Result
SOLVED. Flag: `[flag — recorded in FLAGS/ctf-archive/challenge-313-cryptohack-import_numpy_as_mt-zh3r0_ctf/flag.txt]`
Submitted to slug `import_numpy_as_mt-zh3r0_ctf` (the task card's `-zh3r0_ctf_v2` is the
CTF name, not part of the slug): submit ok:true, solved count 243→244 (archive
challenges are 0-point, so score_delta 0 is expected; solved-list readback confirms).
Recovered seeds (live run): seed2=3689276241, seed1=3935403785.

## Limitations
- First live attempt timed out at 180 s (two sequential 2^32 scans in one foreground
  call); fixed by backgrounding / raising timeout.
- First captured ciphertext was truncated to 200 hex chars by a terminal-preview
  paste → CBC length error; fixed by writing socket output to `ct_hex.txt`
  programmatically and never pasting hex.
- Wasted two cycles on `unpad(outer_plaintext)` — the outer layer has no padding
  (pad-once-before-loop). The iv-regeneration assert passing while padding failed was
  the diagnostic clue.
- No attempt to invert the twist analytically (a 4-equation MITM might avoid the
  2^32 scan); brute force was fast enough (~100 s/layer).

## Sources
not recorded in run logs (pre-discipline solve)
