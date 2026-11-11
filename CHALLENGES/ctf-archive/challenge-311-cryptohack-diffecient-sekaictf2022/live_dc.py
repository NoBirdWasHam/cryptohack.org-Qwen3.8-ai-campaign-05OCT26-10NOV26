import socket, time
K0='4141414141414141414141414141414141414141414141414141414141613121'
K1='e99f204c4141f27c414141414141414141414141414141414141414141613121'
s=socket.create_connection(('archive.cryptohack.org',29201),timeout=25)
f=s.makefile('rwb',buffering=0)
def rd(n=6000):
    out=b''; s_=time.time()
    while time.time()-s_<n:
        try:
            c=f.readline()
        except Exception as e:
            return out+b' ERR '+str(e).encode()
        if not c: break
        out+=c
        if b'API option' in c: break
    return out
print('BANNER:', rd(30)[:80])
f.write(b'1\n'+K0.encode()+b'\n'); print('pre-query K0:', rd(30)[-40:])
f.write(b'2\n'+K1.encode()+b'\n'); print('add K1:', rd(30)[-40:])
f.write(b'1\n'+K0.encode()+b'\n'); print('post-query K0:', rd(30)[-40:])
f.write(b'3\n'+K0.encode()+b'\n'); print('ADMIN:', rd(30)[-120:])
f.write(b'4\n')
try: print(rd(10))
except: pass
s.close()
