# run_all.py — finish remaining blocks then assemble flag
import os, subprocess, sys, time
D = os.path.dirname(os.path.abspath(__file__))
PY = r'~/tools/crypto-ctf/venv/Scripts/python.exe'
ok = True
for bi in range(7):
    if os.path.exists(os.path.join(D, f'seg_{bi}.txt')):
        print('block', bi, 'cached'); continue
    t0 = time.time()
    r = subprocess.run([PY, '-u', os.path.join(D, 'solve10.py'), str(bi)],
                       capture_output=True, text=True, timeout=1500)
    print(f'block {bi} rc={r.returncode} ({time.time()-t0:.0f}s)',
          r.stdout.strip().replace('\n', ' | ')[-160:])
    if r.returncode != 0:
        ok = False
        break
if ok:
    flag = b''.join(open(os.path.join(D, f'seg_{i}.txt'), 'rb').read() for i in range(7))
    fs = flag.rstrip(b'\x00').decode('latin1')
    print('FLAG:', fs)
    open(os.path.join(D, 'flag_failproof_revenge-sekaictf202.txt'), 'w').write(fs)
