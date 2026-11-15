# Probability (SEETF) — probability-seetf2022

- Category: CTF archive (cryptohack.org /challenges/ctf-archive page card)
- URL card: data-challenge="probability-seetf2022" in cat_ctfarch.html (37 solves, 0 solutions)
- Listener: archive.cryptohack.org 59737 (Dockerfile socat TCP-LISTEN:1337 -> python3 probability.py)
- Files: probability.py, Dockerfile (downloaded from cryptohack.org/static/challenges/)
- Optimal fair-play win prob = 0.4244 (stand threshold 0.5706); need 800/1337 = 59.8% -> impossible fairly.
- Real attack: MT19937 state recovery from the printed random.random() outputs, then play with foresight.
