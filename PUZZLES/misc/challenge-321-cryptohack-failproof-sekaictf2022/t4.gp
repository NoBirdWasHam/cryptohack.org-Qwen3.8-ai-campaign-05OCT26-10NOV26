print(qfminim([4,0;0,9], 10, 1));
f() = { r = errcatch([error("boom")]); print("caught ", #r); };
f();
g() = { r = errcatch([qfminim([4,0;0,9],10,1)]); print("ok ", #r); print(r[1]); };
g();
