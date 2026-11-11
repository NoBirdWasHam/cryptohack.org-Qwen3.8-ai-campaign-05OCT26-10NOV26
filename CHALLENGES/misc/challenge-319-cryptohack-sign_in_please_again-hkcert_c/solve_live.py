# LIVE solve: archive.cryptohack.org:60192. Reconnect on pepper miss.
# Budget: <=6 connections, >=10 s spacing. PoW precedes the 60 s alarm.
import sys, os, time, base64
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sbase import S
from solve_core import solve_connection

VERBOSE = ('-v' in sys.argv)

def run_once():
    s = S(timeout=55)
    t_alarm = time.time()
    log = print if VERBOSE else (lambda *a: None)
    log(f'connected, pow {s.pow_t:.1f}s; phases:')
    spy = lambda pbox, salt: _spy(s, pbox, salt)
    t0 = time.time()
    flag = solve_connection(spy, lambda: s.auth_begin(), lambda h: s.auth_answer(h), log=log)
    log(f'solve took {time.time()-t0:.1f}s after alarm start')
    try:
        s.s.close()
    except Exception:
        pass
    return flag

def _spy(s, pbox, salt_bytes):
    out = s.spy(pbox, base64.b64encode(salt_bytes).decode())
    assert out.startswith('\U0001f511'), f'spy error: {out!r}'
    return out.split()[1]

if __name__ == '__main__':
    max_conn = 6
    for i in range(max_conn):
        try:
            f = run_once()
        except Exception as e:
            print(f'conn {i}: EXCEPTION {type(e).__name__}: {e}')
            time.sleep(10)
            continue
        if f:
            print(f'conn {i}: CAPTURED: {f}')
            break
        print(f'conn {i}: miss (pepper recovery ~64% per conn)')
        time.sleep(10)
    else:
        print('NO FLAG after connections')
