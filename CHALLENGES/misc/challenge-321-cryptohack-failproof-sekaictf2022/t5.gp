R = qfminim([4,0;0,9], 10, 2);
print("c2 ", R, " type ", type(R));
S = qfminim([4,0;0,9], 10, 3);
print("c3 ", S, " #S ", #S);
r = errcatch(qfminim([4,0;0,9],1,1));
print("errcatch plain #r ", #r);
