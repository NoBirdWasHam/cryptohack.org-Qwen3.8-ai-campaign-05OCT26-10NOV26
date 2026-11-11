#!/usr/bin/env python
# rhetorical_oracle (131, aes, 100pts) -- AES-CBC padding-oracle forge (Beaulieu-Desmedt).
# socket.cryptohack.org:13436.  Win: send {"ciphertext": hex(IV+blocks)} that decrypts
# (server key) to JSON {"user_id": admin} with valid PKCS7 -> returns flag.
import socket, json, os, sys, time
HOST="socket.cryptohack.org"; PORT=13436
ADMINS=["0656d38b8cb0b41b82ecc9859cb7c03e53c7c6610bdce9ea14d30d1a33c80204",
        "3cc87cad6be102200df733cfa33e02889ce798a88470f3aa2e59bebcaee054b3"]
ADMIN=ADMINS[0]
TARGET=json.dumps({"user_id":ADMIN}, separators=(',',':')).encode()
padlen=16-(len(TARGET)%16)
TARGET=TARGET+bytes([padlen]*padlen)
NB=len(TARGET)//16
print(f"target {len(TARGET)}B -> {NB} blocks, admin={ADMIN[:12]}...", flush=True)

class Conn:
    def __init__(self):
        self.s=socket.create_connection((HOST,PORT),timeout=60); self.s.settimeout(60)
        self.buf=b''; self.n=0
        try: self._obj()          # consume greeting {"token":...}
        except EOFError: pass
    def _fill(self):
        d=self.s.recv(65536)
        if not d: raise EOFError
        self.buf+=d
    def _obj(self):
        while True:
            i=self.buf.find(b'{')
            if i<0: self._fill(); continue
            try:
                o,_=json.JSONDecoder().raw_decode(self.buf[i:].decode('utf-8','ignore'))
                self.buf=self.buf[:i]; return o
            except json.JSONDecodeError: self._fill()
    def query(self,hexct):
        self.s.sendall(json.dumps({"ciphertext":hexct}).encode()+b"\n")
        self.n+=1
        o=self._obj()
        if "flag" in o: return True, o["flag"]
        return bool(o.get("good_pad",False)), None

def recover_D(conn, block):
    """Recover D(block)=AES-ECB-decrypt(block) via oracle, using prev block all-zero."""
    res=bytearray(16); t0=time.time()
    for pos in range(16):
        target=pos+1                      # padding value to force
        found=None
        for v in range(256):
            cand=bytearray(16)
            cand[15-pos]=v
            for j in range(pos):          # force trailing pos bytes to `target`
                idx=15-pos+1+j
                cand[idx]=res[idx]^target
            gp,flag=conn.query((bytes(cand)+block).hex())
            if flag: return None, flag
            if gp: found=v; break
        if found is None: raise RuntimeError(f"no match pos={pos}")
        res[15-pos]=target^found
    print(f"  D recovered {time.time()-t0:.1f}s ({conn.n} q total)", flush=True)
    return bytes(res), None

def main():
    only=int(sys.argv[1]) if len(sys.argv)>1 else NB   # test: recover only last `only` block(s)
    conn=Conn()
    P=[TARGET[i*16:(i+1)*16] for i in range(NB)]
    c=[None]*NB; c[NB-1]=os.urandom(16)
    start=NB-only
    for i in range(NB-1,start-1,-1):
        Di,flag=recover_D(conn,c[i])
        if flag: print("FLAG:",flag); return
        print(f"  D(c[{i}])={Di.hex()}", flush=True)
        if i>start:
            c[i-1]=bytes(a^b for a,b in zip(Di,P[i]))
        else:
            IV=bytes(a^b for a,b in zip(Di,P[0])) if i==0 else None
    if only<NB:
        print("PARTIAL (last %d blocks) ok; queries=%d"%(only,conn.n)); return
    ct=(IV+c[0]+c[1]+c[2]+c[3]+c[4]).hex()
    print("final ct len",len(ct)//2,"queries",conn.n, flush=True)
    gp,flag=conn.query(ct)
    print("RESULT good_pad",gp, flush=True)
    if flag: print("FLAG:",flag)

if __name__=="__main__": main()
