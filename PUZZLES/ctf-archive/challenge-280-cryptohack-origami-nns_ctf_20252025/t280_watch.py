# t280_watch.py — watch t280_fpm_h.cur.fplll for tour updates; on change, run the
# deterministic finisher (fin2: relaxed scan -> pair w/ saved f++ -> solve_sigma ->
# decrypt). Pure python + fin2 (no fplll). Logs to t280_watch.log. Lives ~7h.
import os, time, subprocess, sys
PY = sys.executable
F = "t280_fpm_h.cur.fplll"
try:
    last = os.path.getmtime(F)
except OSError:
    last = 0
end = time.time() + 7 * 3600
log = open("t280_watch.log", "a", buffering=1)
log.write(f"watch start {time.strftime('%H:%M:%S')} last={time.strftime('%H:%M:%S', time.localtime(last))}\n")
while time.time() < end:
    time.sleep(30)
    try:
        m = os.path.getmtime(F)
    except OSError:
        continue
    if m != last:
        last = m
        log.write(f"pm changed {time.strftime('%H:%M:%S', time.localtime(m))} -> fin2\n")
        r = subprocess.run([PY, "-u", "t280_fin2.py", F],
                           capture_output=True, text=True, timeout=1800)
        log.write(r.stdout[-4000:])
        if r.stderr.strip():
            log.write("STDERR: " + r.stderr[-800:] + "\n")
        if os.path.exists("FLAG_FOUND.txt"):
            log.write("!!! FLAG_FOUND.txt exists -> stopping watcher\n")
            break
log.write(f"watch end {time.strftime('%H:%M:%S')}\n")
