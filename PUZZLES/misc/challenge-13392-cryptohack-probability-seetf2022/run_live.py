#!/usr/bin/env python3
"""Repeated live attempts until the flag arrives (per-stream optimal win count
is ~800 +- 20, so each connection wins the flag with prob ~30-40%)."""
import sys, time, os, importlib.util

MAX_ATTEMPTS = int(sys.argv[1]) if len(sys.argv) > 1 else 8
sys.argv = ['solve']
spec = importlib.util.spec_from_file_location('solve', 'solve.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FLAGF = 'flag_probability-seetf2022.txt'

for attempt in range(1, MAX_ATTEMPTS + 1):
    print(f'=== attempt {attempt} @ {time.strftime("%H:%M:%S")}', flush=True)
    t0 = time.time()
    try:
        mod.run_net(attempt=attempt)
    except Exception as e:
        print(f'  attempt {attempt} error: {e!r}', flush=True)
    if os.path.exists(FLAGF):
        print('FLAG FILE PRESENT:', open(FLAGF).read().strip(), flush=True)
        sys.exit(0)
    print(f'  attempt {attempt} failed after {time.time()-t0:.0f}s', flush=True)
    time.sleep(5)
print('no flag after attempts', flush=True)
sys.exit(1)
