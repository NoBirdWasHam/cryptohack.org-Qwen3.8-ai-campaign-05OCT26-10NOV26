# 2020 (TETCTF 2020) - archive card notes

- Card source: cat_ctfarch.html, data-challenge="2020-tetctf2020"
- Service: archive.cryptohack.org:63222 (socat fork EXEC per connection -> fresh
  process + fresh urandom seed per connection; confirmed empirically)
- Provided files (downloaded from card static links):
  - /static/challenges/2020_106af43b083067552c1dcd44e46caa32.py -> 2020.py
  - /static/challenges/Dockerfile_6c539acde83a9a77f55fdeca5d0b9d9d -> Dockerfile
- Protocol: send 2 index lines; server prints 2019 lines (number for requested
  indices, 'Nope!' otherwise, flush happens when it blocks on the guess input);
  send 1 guess line; correct guess => server prints FLAG.
- Live behavioral fingerprint vs file: matches (header text, exactly 2019 loop
  lines, numbers printed exactly at requested positions, nIndices=2, extra lines
  become the guess, non-int index lines crash with 1 header line only, fresh
  random values per session at every probed index).
