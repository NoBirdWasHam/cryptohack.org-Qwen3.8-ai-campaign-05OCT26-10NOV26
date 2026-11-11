
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
for(idx = 1, 1, d = DATA[idx]; Ax = mk(d[1], d[2]); Ay = mk(d[3], d[4]); Bx = mk(d[5], d[6]); By = mk(d[7], d[8]); RA = Ay^2 - Ax^3; RB = By^2 - Bx^3; a4 = (RA - RB)/(Ax - Bx); a6 = RA - a4*Ax; E = ellinit([0,0,0,a4,a6]); A = [Ax, Ay]; B = [Bx, By]; if(!ellisoncurve(E, A) || !ellisoncurve(E, B), print(idx, " ONCURVE FAIL")); b = 1; print("curve ok, starting primes"); for(j = 1, #PR, l = PR[j]; e = EE[j]; km = KM[j]; if(km >= 1, sc = 37*LVAL*MVAL/l^(e+1); Xl = ellmul(E, A, sc); Yl = ellmul(E, B, sc); Tl = ellmul(E, A, MVAL/l^e); if(j<=3, print("j=",j," l=",l," Tl done")); va = 0; cur = Tl; while(cur != [0,1,0], cur = ellmul(E, cur, l); va = va+1); alpha = e - va; if(j<=3, print("j=",j," alpha=",alpha)); mu = 0; if(j<=3, print("j=",j," pairing start")); forstep(k = km, 1, -1, if(mu == 0, Xk = ellmul(E, Xl, l^(k-1)); Yk = ellmul(E, Yl, l^(k-1)); if(ellweilpairing(E, Xk, Yk, l^e) == o1, mu = k))); vl = 0; if(j<=3, print("j=",j," mu=",mu)); if(mu > 0, vl = mu; if(mu > alpha, Xm = ellmul(E, Xl, l^(mu-1)); Ym = ellmul(E, Yl, l^(mu-1)); if(Xm == [0,1,0] || ellweilpairing(E, Xm, Ym, l^e) != o1, vl = alpha)); if(mu < alpha, print(idx, " ANOM mu<alpha l=", l))); if(vl > 0, b = b * l^vl))); FLAG = FLAG || Strchr(b); print(idx, " b=", b, " ", Strchr(b)));
print("FLAG: ", FLAG);
