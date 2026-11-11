import socket, json
H="socket.cryptohack.org"; P=13432
def conn():
    s=socket.create_connection((H,P),timeout=25); s.settimeout(15)
    w=s.recv(4096); print("WELCOME:",w,flush=True); return s
def send(s,o):
    s.sendall((json.dumps(o)+"\n").encode()); return s.recv(65536)
# Connection A: fresh state, negative index first
s=conn()
print("A node=-1 ->", send(s,{"option":"get_node","node":-1}),flush=True)
print("A node=-2 ->", send(s,{"option":"get_node","node":-2}),flush=True)
print("A node=0  ->", send(s,{"option":"get_node","node":0}),flush=True)
print("A do_proof junk ->", send(s,{"option":"do_proof","root":"00"*32}),flush=True)
print("A two-objs-one-line ->", end="",flush=True)
s.sendall(b'{"option":"get_node","node":-1}\n{"option":"get_node","node":-2}\n')
import time; time.sleep(2)
try:
    print(repr(s.recv(65536)),flush=True)
except Exception as e: print("recv err",e,flush=True)
s.close()
# Connection B: does secret persist across connections? leaf0 twice on same conn impossible; compare leaf3 (stable) and leaf0 across two conns
for tag in ("B","C"):
    s=conn()
    print(tag,"node=0 ->", send(s,{"option":"get_node","node":0}),flush=True)
    print(tag,"node=3 ->", send(s,{"option":"get_node","node":3}),flush=True)
    s.close()
