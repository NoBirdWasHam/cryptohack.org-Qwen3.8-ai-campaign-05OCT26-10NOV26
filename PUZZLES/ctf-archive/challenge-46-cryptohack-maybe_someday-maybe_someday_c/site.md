# Site info — maybe_someday-maybe_someday_c

- Card: ctf-archive, "Maybe Someday (Maybe Someday CTF)", 34 solves, contributed by Mystiz
- Statement text on card is mismatched boilerplate (hash-collision text); real challenge = chall.py (Paillier).
- Listed listener: `archive.cryptohack.org 56434` — REFUSED connections on 2026-10-28 (8 attempts over ~7 min, all WinError 10061; also refused on cryptohack.org / www.cryptohack.org).
- File: /static/challenges/chall_1da0bbcca674d9f5fdb078a93239dc14.py (md5 1da0bbcca674d9f5fdb078a93239dc14) — byte-identical to the googlectf2022 sibling card's file.
- Live backend serving that exact code: `archive.cryptohack.org 14846` (googlectf2022 card's port) — prints `n =`, `g =` banner as chall.py does.
- Submission: `python3 submit_flag.py maybe_someday-maybe_someday_c "<flag>"` → ok:true, solved 272→273, score_delta 0 (archive challenge worth 0).
