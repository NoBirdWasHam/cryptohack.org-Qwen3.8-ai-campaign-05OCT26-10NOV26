
default(parisize, "6g");
read("params.gp");
F = ffinit(PVAL, 2);
W = ffgen(F, 'W);
o1 = W^0; z0 = W*0;
ffsqrt_ts(r) = {
  local(q, e, mm, z, c, x, t, i, b);
  if(r == 0, return(z0));
  q = PVAL^2;
  if(r^((q-1)>>1) != o1, return(-1));
  e = valuation(q-1, 2); mm = (q-1) >> e;
  z = W; while(z^((q-1)>>1) == o1, z = z+1);
  c = z^mm; x = r^((mm+1)>>1); t = r^mm;
  while(t != o1, i = 0; b = t; while(b != o1, b = b^2; i = i+1); b = c^(2^(e-i-1)); c = b^2; x = x*b; t = t*c);
  return(x);
}
mk(re, im) = { re + im*I2 };
DATA = read("bytes.gp");
MVAL = PVAL + 1;
I2 = ffsqrt_ts(-1 + z0);
print("i^2+1 == 0: ", I2^2 + o1 == z0);
FLAG = "";
for(idx = 1, #DATA, d = DATA[idx]; Ax = mk(d[1], d[2]); Ay = mk(d[3], d[4]); Bx = mk(d[5], d[6]); By = mk(d[7], d[8]); RA = Ay^2 - Ax^3; RB = By^2 - Bx^3; a4 = (RA - RB)/(Ax - Bx); a6 = RA - a4*Ax; E = ellinit([0,0,0,a4,a6]); A = [Ax, Ay]; B = [Bx, By]; if(!ellisoncurve(E, A) || !ellisoncurve(E, B), print(idx, " ONCURVE FAIL")); b = 1; for(j = 1, #PR, l = PR[j]; e = EE[j]; Ae = ellmul(E, A, MVAL/l^e); Be = ellmul(E, B, MVAL/l^e); zpl = ellweilpairing(E, Ae, Be, l^e); vv = 0; for(k = 0, e, if(zpl^l^k == o1, vv = k; break)); vl = e - vv; if(l == 2, vl = 7 - vv); if(vl > 0, b = b * l^vl)); FLAG = FLAG || Strchr(b); print(idx, " b=", b, " ", Strchr(b)));
print("FLAG: ", FLAG);
