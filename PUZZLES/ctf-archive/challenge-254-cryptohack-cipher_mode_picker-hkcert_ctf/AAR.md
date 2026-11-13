# AAR — cipher_mode_picker-hkcert_ctf (archive.cryptohack.org:2951)

**Solved: yes.** Flag: `[flag — recorded in FLAGS/ctf-archive/challenge-254-cryptohack-cipher_mode_picker-hkcert_ctf/flag.txt]`

## The vuln
`chall.py` (1334 B, fetched from `/static/challenges/chall_0095f51d1a465af2ef03fb394d971c4e.py`):
one AES key + one IV reused across 5 rounds; user picks mode (each mode at most once,
`options.remove(option)`) and target (`data` = chosen hex, or `flag`, 80 bytes).
Mode confusion: CFB with `segment_size=128` and **all-zero plaintext** degenerates to the
OFB keystream recursion — `C_i = P_i ⊕ E(C_{i-1})` with `P_i = 0` gives `C_i = E(C_{i-1})`,
`C_0 = E(iv)`, i.e. exactly `KS_i = E^{i+1}(iv)`, the OFB keystream.

## Attack (2 queries)
1. `cfb data 00*80` → returns OFB keystream KS (5 blocks).
2. `ofb flag` → `ct = flag ⊕ KS`.
3. `flag = ct ⊕ KS`.

## Validation
- Local clone (`python3 solve.py --local`, FLAG=hkcert21{A*70}) recovered the test flag byte-exact.
- Remote run on archive.cryptohack.org:2951 returned printable 80-byte hkcert21{...} (matches `assert len(flag)==80`).
- Submission: `submit_flag.py` → ok:true, solved list 241→242 (score_delta 0 — archive entries credit 0 pts; solved-readback is the ground truth).

## Learning points
- Same key+IV across modes ⇒ any mode that exposes `E(iv)`-chain output under chosen plaintext breaks OFB. Zero-fill is the trick that makes CFB's ciphertext-feedback equal OFB's.
- ECB/CBC/CTR unused; CTR (`Counter.new(16, prefix=iv[:14])`) would also have leaked keystream but only for its own counter blocks, not the OFB chain.
- Protocol nit: `input('> ')` prompt has no newline, so it glues to the next hex line — parse last whitespace token.

## Limitations
None — solved first try. (Prior solver's head start: card extraction + listener/port; chall.py re-fetched fresh.)

## Files
- chall.py, statement.txt, solve.py (local + remote modes), flag_cipher_mode_picker-hkcert_ctf.txt

## Sources
not recorded in run logs (pre-discipline solve)
