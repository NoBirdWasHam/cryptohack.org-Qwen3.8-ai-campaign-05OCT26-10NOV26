---
name: hash-collision-md5-engineering
description: Use for MD5/SHA-1 collision or chosen-prefix CTF tasks.
---

# MD5/SHA-1 collision engineering

## Structure facts
- MD5 (RFC 1321, Rivest 1992): Merkle–Damgård, 128-bit state, 64-byte blocks, 4 rounds of 16 ops.
  Collision exists at complexity ~2^18-2^24 ops via Wang et al. differential path (EUROCRYPT 2005, LNCS 3494;
  eprint 2004/538) — message-modification technique makes collisions PRACTICAL, not theoretical.
- SHA-1: shattered-class chosen-prefix collisions exist (practical for teams); same differential-path family.

## Tools (owner-approved sources, clone/build per windows-crypto-toolchain rules)
- github.com/cr-marcstevens/hashclash — MD5 + SHA-1 (SHAttered-style) collision & chosen-prefix CLI.
- github.com/tobiasfarber/fastcoll — fast MD5 collisions incl. chosen-prefix (Farber–Kasper–Peyrin–Stevens).
- UniColl (corkami/unicoll notes) — single-byte-difference collisions (N=1 `poc_no`): the pair differs in
  ONE logical byte (+ its block-2 replica at +64). The CLI that ran it (`md5_diffpath*` with `--diffm2 N`
  and `--startpartialpathfile`) is NOT in hashclash master anymore and the old r38 prebuilt exes predate
  that interface — build from the hashclash `hc-old/trunk/src` svn snapshot (has diffpath{helper,forward,
  backward,connect} + md5_uc_helper + test_poc/poc_no.sh).
Both build in MSYS with plain make; run <2 threads.

## Chosen-prefix with long pinned prefixes
- **A long pinned prefix is a differential SEAT, not an obstacle — do not reject UniColl by
  byte-count arithmetic.** `--startpartialpathfile` absorbs ANY word-aligned prefix into the lower
  differential path, so a 24-byte pinned prefix is fully compatible with an N=1 collision. Before
  ruling a planted-prefix collision challenge out for tool-reach, locate the prefix byte that sits on the
  differential's flip position (the flip must be legal for the app's parser, e.g. 'k'→'l' keeps one
  side of a startswith() check) and set `--diffm2` to that byte index.


## CTF play patterns
1. "Give me two inputs with same MD5": use fastcoll/hc_sbmp (stubbed identical-prefix mode) — two PDFs/ZIPs
carrying colliding blocks beat hand-crafted differential paths every time.
2. Chosen-prefix: choose suffix length so both prefixes pad to a block boundary; the collision blocks do the rest.
3. Collision BLOCKS are reusable: extract the differing 64-byte block pair once, re-embed in ANY container
(format-length tricks) — the classic "same-hash different-file" puzzle mechanic.
4. Verify collisions yourself (hash both files) before trusting any tool output; length-extension ≠ collision.
5. Signature-forgery flavor: sign file A (harmless), re-embed collision block into B (flag-revealing) — the
cert/pkcs1 CTF pattern.

## Canonical references
[R1] Rivest, "The MD5 Message-Digest Algorithm", RFC 1321, 1992. https://datatracker.ietf.org/doc/html/rfc1321
[R2] Wang–Guo–Lai–Yu, "How to Break MD5 and Other Hash Functions", EUROCRYPT 2005, LNCS 3494. https://eprint.iacr.org/2004/538
[R3] Stevens–Kasper–Peyrin–Wagner, hashclash. https://github.com/cr-marcstevens/hashclash
[R4] Farber–Kasper–Peyrin–Stevens, fastcoll. https://github.com/tobiasfarber/fastcoll
