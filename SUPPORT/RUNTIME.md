# Runtime / models
Two inference hosts, both self-hosted; no cloud model APIs were used for solves.

| role | model | host | notes |
|------|-------|------|-------|
| primary agent brain (most phases) | Qwen3.8-27B | local workstation, GPU (Radeon R9700), :8080 | served locally; llama.cpp-family engine, details in LEDGER/HANDOFF_sanitized.md |
| late-phase / fleet brain | Qwen3.8-Flash-Next, unsloth UD-Q4_K_XL quant | GPU-HOST (RTX 3090 Ti, 128 GB RAM), :8080 | engine swap procedure itself is campaign practice (engine-feed) |
| agent shell | Hermes agent | Windows 11 | toolchain: Python venv (fpylll, pwntools, pycryptodome), PARI/GP, msolve; WSL disabled |

Attribution honesty: per-challenge model attribution is **phase-level, best-effort** —
the ledger records dates, not per-message model IDs. Early-mid campaign = local 27B;
the 11-09→11-10 fleet walk = Flash-Next. A hardware incident (BSOD bugcheck 0x154 under
sustained dual-load, 2026-11-10 ~03:04) ended the fleet phase; see FRICTION.md.
See runtime.yaml for machine-readable form.
