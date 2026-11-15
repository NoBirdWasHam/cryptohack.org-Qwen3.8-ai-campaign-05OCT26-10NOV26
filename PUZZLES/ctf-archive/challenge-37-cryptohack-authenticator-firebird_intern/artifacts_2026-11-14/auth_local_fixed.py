import socket, sys, types, os, threading

sig = types.ModuleType('signal')
sig.SIGALRM = 14
def _noop(*a, **k): pass
sig.signal = _noop
sig.alarm = _noop
sys.modules['signal'] = sig

os.environ['FLAG'] = 'FLAG-REDACTED-SEE-FLAGS-MIRROR'

import importlib.util
spec = importlib.util.spec_from_file_location('auth_chall_mod', 'auth_chall.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PW = os.environ.get('TESTPW', '1mbVy3').encode()

def handle(conn):
    r = conn.makefile('rb')
    w = conn.makefile('wb')
    def inp(prompt=''):
        w.write(prompt.encode()); w.flush()
        line = r.readline()
        if not line: raise EOFError
        return line.decode().strip()
    def pr(*args, **kw):
        w.write((' '.join(str(a) for a in args) + '\n').encode()); w.flush()
    server = mod.AuthenticationServer(PW)
    try:
        cc = bytes.fromhex(inp('challenge_client = '))
        rs, cs = server.handshake(cc)
        pr(f'response_server = {rs.hex()}')
        pr(f'challenge_server = {cs.hex()}')
        rc = bytes.fromhex(inp('response_client = '))
        server.verify_handshake(rc)
        pr(f"Congrats! {os.environ['FLAG']}")
    except Exception as err:
        pr(f'Error: {err}')
    finally:
        conn.close()

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('127.0.0.1', 13339))
srv.listen(5)
print('serving fixed-pw on 13339', flush=True)
while True:
    c, a = srv.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
