print(version());
f() = { res = errcatch([qfminim([4,0;0,9],10,1)]); print("ok ", #res); };
f();
