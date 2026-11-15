# AAR — tough_decisions (ECSC 2023 Norway, ctf-archive)

**Solved:** yes — flag derived purely from provided `output.txt` + `tough_decisions.py`.

## The vulnerability
LWE samples `(a, a·s + e mod 256)` vs uniform `(a, uniform)`, key = 16 bytes, 6 samples
per flag bit. The "PRNG" noise `sample_noise(7)` builds
`e = ((...((b1)|<<1)...)) = 2*(64b1+32b2+...+b7)` — i.e. **e is always even**.
So for real samples, `LSB(b) = LSB(a·s)` deterministically (the higher bits of e are
uniform mod 128, so parity is the *only* leak, and it's a perfect one).
Key gotcha: `[[real, fake][b](s)]` indexes with `b`, so **bit=0 → real**, bit=1 → fake.

## Attack
1. `LSB(a·s) = GF(2)-dot(a mod 2, s_low)` where `s_low` = LSBs of the 16 key bytes
   (16 unknown bits). Brute force all 2^16 masks: the correct `s_low` makes every real
   group (all 6 samples) parity-consistent. Observed score: **154/296 groups all-match
   for the true mask; runner-up only 17** — unambiguous.
2. Classify: group with ANY parity mismatch ⇒ fake ⇒ bit=1 (certain, real can't
   mismatch). All-match group ⇒ bit=0 (fake all-matches w.p. 2^-6 only).
   Error mode: true-1 bits decoded as 0 (never 1→0), i.e. true byte ⊇ decoded byte
   bitwise. With ~154 one-bits expected errors ≈ 2.4, but the decode came out fully
   within the flag charset with zero fixes needed — `fixes()` found 0 bad positions.
3. Bits are LSB-first per byte (`[(b>>i)&1 for b in bs for i in range(8)]`).

## Key numbers
- 296 groups = 296 bits = 37-byte flag; mask = 0x3D6D (15725).
- Result: `[flag — recorded in FLAGS/ctf-archive/challenge-30-cryptohack-tough_decisions-ecsc_2023_nor/flag.txt]` (self-derived).

## Pitfalls hit (worth remembering)
- First decode attempt inverted real/fake and produced garbage that *didn't* fit the
  assumed `crypto{` prefix — this challenge's flag prefix is `ECSC{`, and the index
  list `[real, fake][b]` means 0→real. Validate hypotheses with a prefix-fit scan
  (dbg1.py fits both labelings over 2^16 masks against a candidate prefix) rather
  than assuming `crypto{`.
- A GF(2) mask indexes the **per-byte LSB vector**, not the raw byte string — ANDing
  the mask against the 16-byte integer is wrong (bit j of mask must gate `a_j & 1`).

## Limitations
- Nothing failed outright; the only missteps were the two modeling bugs above, both
  caught by cross-checking against the known-format structure.
- No listener/port for this archive challenge; flag verified via cryptohack.org
  submission (`ok:true`, solved 280→281; archive challenges award 0 points).

## Files
- `solve.py` — initial (buggy bit-mapping, kept for history), `solve2.py` — final solver
- `dbg1.py` — 2^16 prefix-fit check for real/fake labeling
- `flag_tough_decisions-ecsc_2023_nor.txt`, `statement.txt`, `site.md`

References: none used beyond the provided challenge source (HPS textbook not needed).
