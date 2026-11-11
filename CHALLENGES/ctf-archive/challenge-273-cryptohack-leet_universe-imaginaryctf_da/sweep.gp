default(parisize,"512M");
R = read("_R.txt");
for(xx=0, 20000000, d = gcd(xx^13 + 37, R); if(d > 1, write("sweep_hit.txt", Str("HIT x=", xx, " d=", d))); if(xx % 1000000 == 0, write("sweep_progress.txt", Str("at ", xx))); );
write("sweep_done.txt","sweep 0..2e7 done");
