d2=[[1,2],[3,4]];
rec(i,j)= { my(z); z=d2[i][1]+d2[j][2]; return(z); }
P=0;
for(k=1,#d2-1, if(P==0, P=rec(k,k+1); );
);
print("ok ",P);
