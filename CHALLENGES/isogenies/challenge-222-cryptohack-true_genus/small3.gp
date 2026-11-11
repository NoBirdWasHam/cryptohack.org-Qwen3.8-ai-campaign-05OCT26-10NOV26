default(parisize,"512M");
read("orbit.gp");
dumporbit() = {
  my(p=1289, ls=[3,5,43], d=3);
  my(K=bnfinit(x^2+p,1), h=K.no, cs=[]);
  print("H=", h, " cyc=", K.cyc);
  for(i=1,#ls, my(P=idealprimedec(K,ls[i])[1]); my(z=bnfisprincipal(K,P,0)); my(c=if(type(z[1])=="t_INT",z[1],z[1][1])%h); cs=concat(cs,[c]); print("CLS ",ls[i]," ",c));
  my(res=orbitBFS(p,Mod(0,p),Mod(1,p),ls,d,3000));
  my(m=res[1], order=res[2]);
  for(k=1,#order, my(jj=order[k]); my(w=getword(m,jj)); my(x=0); for(t=1,#w, my(l=w[t][1]); my(s=w[t][2]); for(i=1,#ls, if(ls[i]==l, x=x+s*cs[i]))); my(v); mapisdefined(m,jj,&v); print("ROW ", x%h, " ", lift(v[1]), " ", lift(v[2])));
  print("WROTE ",#order);
}
dumporbit();
