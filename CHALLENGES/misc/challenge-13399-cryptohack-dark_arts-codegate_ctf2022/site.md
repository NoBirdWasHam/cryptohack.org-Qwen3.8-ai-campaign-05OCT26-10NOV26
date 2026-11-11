# dark_arts-codegate_ctf2022 — site card (cryptohack.org/challenges/ctf-archive/)

- Title: Dark Arts (CODEGATE CTF)
- Slug: dark_arts-codegate_ctf2022
- Statement: "Breaking random functions is a dark art, and I need your help in this.
  Connect at `archive.cryptohack.org 35802`. Challenge files: chal.py.
  Challenge contributed by rkm0959"
- Solves at capture: 41
- Files: /static/challenges/chal_ab50c49bda5728e0370b640b328c4eb4.py (archive.cryptohack.org 404s; fetched from live cryptohack.org, 5015 B)
- Structure of chal.py: 4 sequential generators, all-or-nothing exit on any wrong guess;
  flag = os.environ["FLAG"] printed at the very end; signal.alarm(300) per connection.
