---
name: interval-dlp-kangaroo
description: Use for interval DLP; kangaroo + range-complete verdicts.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, dlp, kangaroo]
    related_skills: [ctf-ecc-attacks, ctf-practice-runs, cryptohack-socket-challenges]
---

# Interval DLP — parallel kangaroo + verdict discipline

## When to Use
The secret exponent is known/conjectured to lie in an interval [a,b] much narrower than the group
order: twin-DLP constructions (same secret, two bases), signed-exponent searches, RSA-with-hint
variants, or "find x in range" archive challenges.

## Method (formulas banked; sources in campaign REFERENCES.md group B)
- Pollard lambda / distinguished-point kangaroo: tame herd walks from a,b; wild herd from g^y;
  a DP-to-DP meeting yields x. Serial expected total (2+o(1))·sqrt(w), w=b−a; worst case
  (3+o(1))·sqrt(w) near endpoints (Galbraith–Montgomery–Teitler give the rigorous tail).
- Parallelization: distinguished points give linear speedup, negligible comms (van Oorschot–Wiener).
  2T+2W herd config expected total ≈ 3.3·sqrt(w) (Galbraith–Pollard–Ruprai 4-kangaroo: 1.714·sqrt(N)).
- Practical: measure your own rate (group ops/s) early from the stats line; budget_hours·3600·rate·n_herds
  = expected total steps; compare against sqrt(w) multiples, not raw step counts.

## THE VERDICT FRAME (the part that gets skipped)
An empty kangaroo run is only a **RANGE-COMPLETE negative** if the per-direction budget covers the
walk tail: budget_total ≈ t·sqrt(w) with t ≫ herd-expectation (e.g. 45·sqrt(w) per kangaroo ≈ 55x
the 2T2W expectation gives meeting-failure tail <~ e^-40 under the pseudorandom-walk model — state
the model). Otherwise the result is **BUDGET-BOUNDED** (a weaker negative) and must be labeled as
such — never let "ran out of time" report as "not in range". Write the verdict into the folder as a
dated artifact with the final log lines, steps, sqrt(w)-multiples, and the tail bound formula used.

## Engineering that survived contact
- **Checkpoint every herd** (JSON: steps, dp-table size, herd positions): makes the run resumable,
  which is what lets a fleet-cap dispute pause the KANGAROOS instead of an uncheckpointed hunt.
- venv launchers spawn a base-interpreter child: `tasklist`/grep counts DOUBLE (trampoline + real
  worker). Count by CommandLine match (Get-CimInstance) or CPU-seconds, not process-name grep.
- A sound hosted build that yields zero meetings over a range-complete run is EVIDENCE the secret is
  outside the range — the residual door becomes provider drift only (drift sentinel + frozen banner
  hash), and the row stays open per owner rule.

## Pitfalls
- Do not compare the interval width to the GROUP order sqrt and call it feasible: cost is sqrt(W)
  with W = interval width, always, tame-side included.
- Rounds/params in a homegrown runner must round-trip against a planted x in [a,b] on a toy group
  BEFORE spending the real budget (same planted-control rule as every hunt).
