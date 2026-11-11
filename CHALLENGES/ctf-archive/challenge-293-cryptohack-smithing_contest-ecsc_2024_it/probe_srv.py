# probe formats of the live server
import socket, json, re
HOST,PORT="archive.cryptohack.org",25469
s=socket.create_connection((HOST,PORT),timeout=25)
f=s.makefile('rwb')
rl=lambda: f.readline().decode().strip()
sd=lambda l: (f.write((l+"\n").encode()), f.flush())
print('L1:', rl()[:80])
print('L2 params:', rl()[:400])
sd("probeuser")
print('du0:', rl()[:300])
print('du1:', rl()[:300])
G2Xs = "100774561144590475569157120930767342387*a + 218728496724280042701446122970647661523"
G2Ys = "115367896606755692925113233629944781384*a + 211093354487559124632805793736258741445"
sd(json.dumps([[1, 133660577740454676305948404600566797994], [G2Xs, G2Ys]]))
sd("m1")
sd("probeuser")
print('C-line:', rl()[:120])
print('next:', rl()[:120])
s.close()
