# Publish + score-clearing protocol (owner decision 2026-11-10)
1. Owner verifies this tree (this document set + gates in GATES.md).
2. Owner manually resets CryptoHack progress **before** the GitHub upload.
3. Upload batch 0: top-level docs + LEDGER + FLAGS + TOOLS + SKILLS.
4. Then one batch per category, in cat_order: maths → rsa → ecc → diffie-hellman → aes →
   hashes → web → post-quantum → misc → isogenies → zkp → ctf-archive.
   Each batch = `CHALLENGES/<category>/**` (scripts + AARs, our artifacts only).
5. Owner reclears the score after each batch lands ("then I will reclear when done").
Rationale: the repo is the durable record; the scoreboard stays courtesy-clean throughout.
