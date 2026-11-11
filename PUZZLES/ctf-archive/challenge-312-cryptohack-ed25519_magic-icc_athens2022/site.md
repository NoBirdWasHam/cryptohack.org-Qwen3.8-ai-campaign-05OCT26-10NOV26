# site.md — ed25519_magic-icc_athens2022

- Category: ctf-archive (cat_ctfarch.html card)
- Listener: `archive.cryptohack.org 31144` (container-internal 1337 via xinetd)
- Files: chal.py (sha-slug b65423a0…), Dockerfile (python-base:3.12 + ed25519==1.5 sdist,
  versioneer patched for py3.12), magic.xinetd
- Solves at capture time: 55; points: 0 (archive)
- Protocol: line-based text. L1: prints base64 sig line, then "Enter new signature:"
  prompt AFTER it. L2: "Enter verifying key:" then "Enter signature:", then flag line
  `ICC{...}` then connection closes.
- Library: PyPI ed25519 1.5 = C ext over ed25519-supercop-ref (no S<L, no subgroup,
  no identity checks).
