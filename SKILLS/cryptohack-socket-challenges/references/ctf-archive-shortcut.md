# CTF-archive official repo: LEGIT vs FORBIDDEN (corrected 2026-10-27)

For CryptoHack CTF-archive challenges the official repo publishes everything:
- List: `curl -s https://api.github.com/repos/cryptohack/ctf_archive/contents/`
- Deployed code + pip pins: `.../<Folder>/server_files/server.py`, `Dockerfile` — **LEGIT**:
  the challenge's own deployed artifacts; use them to fingerprint the live build + exact lib
  versions (within no-cheat rules).
- Flag: `.../raw/main/<Folder>/description.yml` -> `base64_flag` — **FORBIDDEN** as a solve
  source under this user's no-cheat discipline: it is the answer file. Retrieving + submitting
  it is a RETRIEVAL, not a solve; if ever done it must be labeled as such in AAR + progress
  notes. Never recommend it as a workflow step. Self-derive, or record a documented STUCK /
  proven-negative outcome.
- DSA param search gotcha: p=q*sq+1 odd prime needs sq EVEN; `timeout` on git-bash cannot
  kill Windows python.
