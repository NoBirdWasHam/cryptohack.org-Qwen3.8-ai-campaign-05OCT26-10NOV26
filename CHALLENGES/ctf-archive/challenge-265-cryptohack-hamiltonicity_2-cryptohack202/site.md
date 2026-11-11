# site.md — hamiltonicity_2-cryptohack202 (folder 265)

- Card: category 303 (ctf-archive-2024), "Hamiltonicity 2 (CryptoHack)", 199 solves, 1 solution listed.
- Listener: archive.cryptohack.org:34597 (only open port in 34560-34644 banner scan; banner
  "prove to me that G has a hamiltonian cycle!\n" then bytes-repr prompt "b'send fiat shamir proof: '").
- Posted files (MD5 == our copies, verified):
  chal.py          eedb81528048e6276932d8fd437a8572
  example.py       ffb8932a1a23b56e397061c33a278ec4
  hamiltonicity.py bc3acea59e37dd6941ddd4fdbf34f5ff
- Re-confirmed LIVE 2026-11-03 (one connection, _local/reprobe_2026-11-03.log): same banner,
  same traceback fingerprint, round-0 bit matched global-final-LSB prediction => no build drift.
- Live == posted build (evidence): server traceback frames /app/chal.py line 75
  `if not testcycle(A, N, cycle, openings):` and /app/hamiltonicity.py line 70
  `from_list = [n[0] for n in nodes]` match the posted files line-for-line;
  3 live challenge bits matched the posted-hash prediction vs 4 rival
  derivations (see AAR).
- Note: NOT the sigma-course variant (folder 237, different host/build era;
  its conclusions were not reused; independent fingerprinting done here).
