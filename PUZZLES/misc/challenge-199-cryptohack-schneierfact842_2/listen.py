import socket, json
pw = open("password.txt").read().strip()
s = socket.create_connection(("socket.cryptohack.org", 13401), timeout=60)
f = s.makefile("rwb")
banner = f.readline()
print("banner:", banner[:120])
f.write((json.dumps({"password": pw}) + "\n").encode())
f.flush()
resp = f.readline()
print("resp:", resp[:300])
try:
    d = json.loads(resp)
    print("msg:", d.get("msg"))
except Exception:
    pass
s.close()
