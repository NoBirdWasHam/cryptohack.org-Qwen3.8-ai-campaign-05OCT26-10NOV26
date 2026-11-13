---
name: ctf-answer-challenges
category: ctf
description: "CryptoHack answer challenges: flag format to submit."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, cryptohack, answer-challenges, flag-format]
    related_skills: [ctf-practice-runs]
---

# CryptoHack answer challenges — flag format is the whole game

## When to Use
CryptoHack challenges with no file/service whose statement says "the flag is ...". The math
is trivial; the FAILURES come from submitting the wrong WRAPPER. The grader's response body
is identical for right and wrong — only the API score delta tells you the truth.

## Format rules (verified by submission, 2026-10-12)
1. **Statement says `crypto{...}`** → submit wrapped: `crypto{...}`.
2. **Statement gives a bare number / year / float** (gcd, egcd, root0/1, ma0/1, mdiv,
   basis, gramschmidt, zkpintro...) → submit the BARE value, no wrapper. Try the most
   literal form first (`9`, not `9.0`; `0.91611` to the stated precision).
3. **Statement says "enter the name / the CA / the organisation"** (secure-protocols) →
   submit the BARE string (`[flag — recorded in FLAGS/web/challenge-150-cryptohack-secure-protocols/flag.txt]`), no wrapper.
4. When in doubt: submit the bare value first; if score_delta 0, try wrapped; then try
   precision variants (`9.0`, `9.00000`). At most 3–4 attempts, then re-read the statement
   for the exact phrasing ("to 5 significant figures" → `0.91611` worked; `9.0` did not).

## Field-element answers (2026-10-15, comp_isogenies)
When the answer lives in an extension field (j-invariant in F_{p²}), the grader expects the
**Sage field-element string: highest-degree term first, explicit `*`, spaces around `+`**:
`[flag — recorded in FLAGS/isogenies/challenge-211-cryptohack-comp_isogenies/flag.txt]` (imag*i + real). Six serializations failed before this one:
`249510360818i + 292990704480` (no `*`), `292990704480+249510360818i`, space pair, comma
pair (± spaces), real-first `a + b*i`. Order to try: Sage form first (statement itself writes
F_{p²} values in that style, e.g. `K = (357834818388i + 53943911829, ...)`), then bare pairs.

## Browser-tool string elision (2026-10-12, token-appreciation)
`browser_exec` output ELIDES long strings (shows `eyJ0eX...47KQ` instead of the real
204-char JWT). When a statement shows a long token/blob to decode, DO NOT read it from the
tool result — decode it IN the browser via `js()` and return only the short decoded value:
```js
js("""(() => {
  const raw = document.querySelector('.codeBlock').textContent.trim();
  const b = s => { s=s.replace(/-/g,'+').replace(/_/g,'/'); while(s.length%4) s+='='; return atob(s); };
  const p = JSON.parse(b(raw.split('.')[1]));
  return JSON.stringify(p).match(/crypto\{[^}]*\}/)?.[0] || JSON.stringify(p);
})()""")
```
Verified: token-appreciation 204-char JWT -> `[flag — recorded in FLAGS/web/challenge-151-cryptohack-token-appreciation/flag.txt]`
in-browser; the raw token was never visible in the tool output.

## API reconciliation gotcha (2026-10-13) — name vs slug matching
`/api/user/<name>/` returns **display names** ("Gram Schmidt", "What's a Lattice?", "LWE
Intro") — NOT slugs. When diffing the API against inventory/remaining: normalize with
`lower().replace('_','-').strip()` and **do NOT mangle spaces** (`.replace(' ','-')` breaks
"Gram Schmidt" → "gram-schmidt" and made 17 live-solved challenges look stale). Match
name→slug via the inventory's (name, slug) pairs first. A wrong normalizer produces both
phantom "stale remaining" and phantom "solved but not live" — re-verify with exact
lowercase name equality before believing a diff.

## Pitfalls
- **zkpintro (2026-10-12):** "the year that Goldwasser et al published The Knowledge
  Complexity of Interactive Proof Systems" — the SIAM journal year **1989 was REJECTED**;
  the accepted flag is `[flag — recorded in FLAGS/zkp/challenge-224-cryptohack-zkpintro/flag.txt]` (the FOCS extended-abstract year). When a "famous
  paper" question fails, check the conference version before doubting your memory.
- **Answer statements live on the category page HTML** (server-rendered) — the per-challenge
  URL is JS-rendered/404 via curl. Scrape `data-challenge="..."` + the
  `challengeDescription` div from `/challenges/<cat>/`. (Some descriptions are HTML comments
  `--> ...` — strip the markers.)
- The category page carries the FULL statement including the flag instruction at the end
  ("The flag is the ... to 5 significant figures") — read the LAST paragraph first.
