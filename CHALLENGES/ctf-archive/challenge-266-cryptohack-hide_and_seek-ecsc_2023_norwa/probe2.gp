default(parisize,"1G");
read("data.gp");
f(i,j) = my(x,y); x=data[i][1]; y=data[j][2]; return(x+y); }
print(f(1,2));
g(u,v) = return(data[u][1]*data[v][2]); }
print(g(1,2));
