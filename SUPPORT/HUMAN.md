# The arc, in plain language
Started 2026-10-05 with an account at 85-solved baseline and a simple contract: learn the
math, write every skill down, keep the ledger honest even when honesty is unflattering.

**Ramp (Oct 05–19).** Courses and classics built the shared vocabulary: RSA Coppersmith
family, lattice reductions, MT19937 state recovery, padding oracles. The SKILLS/ tree in
this repo is the literal product of that ramp — each skill is a tool the *next* model can
load cold.

**Deep water (Oct 19–Nov 6).** Isogeny walks, ZKP forgeries, NTRU-style lattices. Two
habits earned their keep: write the bound before spending the compute (after we wasted 104
GPU-hours ignoring that one), and never let a script grade its own homework (after an
owner-facing probe printed a verdict we had authored ourselves and the owner said, correctly:
*"That is YOU."* From then on, probes print bytes; humans judge bytes.)

**The fleet walk (Nov 9–10).** A near-complete sweep of remaining archive challenges;
multi-instance services, a broken mirror, the dual-parse forgery that cleared 237 and 265
with one flag. Ended by hardware: 18 hours of dual load, then bugcheck 0x154 at 03:04.

**The honest row (246).** The campaign's hardest lesson and its cleanest arc: attack
verified ground-truth-exact against a local clone while the live container sat dead for
every visitor since a 29-Sep image bump; root-caused to one character of
Python-version-sensitive code; reported upstream with byte-evidence and the fix (`//`);
closed **unsolved for weeks** because the site's flag never came from the site — we did
not submit what we had not obtained. On 2026-11-11 the maintainers shipped exactly that
fix (commit title: "fix python 3.12 randint no longer accepts floats"), the first raw
capture after the fix returned 13,093 bytes including the full flag block, and the
verified solver recovered and submitted the flag live — WALKED. The failure documentation
survives in the AAR untouched; the solve continues the same story instead of replacing it.

**Score etiquette.** Honor-system platform, learning purpose: the owner clears the account
after documentation verification, per batch (BATCHES.md), and the cleared state is what the
repo describes — deliberately.
