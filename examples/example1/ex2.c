
#include "stdio.h"

int main(void)
{
  FILE *fp;
  
  printf("@ -- \n");
  printf("@ -- Output from fake application code \n");
  printf("@ -- comment lines \n");
  printf("@ -- \n");
 
  printf("$cputime = { 2.2 }\n");
  printf("$residuals { 33.33, 6.6 }\n");
  printf("kspits 42\n");
  printf("$norm = 99.9\n");
  printf("$rms 51.0\n");
  
  fp = fopen("ex2-residual.log","w");

  fprintf(fp,"@ -------------------------------------------- \n");
  fprintf(fp,"@ -- Residual log file from application code \n");
  fprintf(fp,"@ -------------------------------------------- \n");
  
  fprintf(fp,"\n");
  fprintf(fp,"Residuals = [\n");
  fprintf(fp,"0.001,\n");
  fprintf(fp,"0.0004,\n");
  fprintf(fp,"1.0e-4,\n");
  fprintf(fp,"1.4434e-7\n");
  fprintf(fp,"]\n");
  fclose(fp);
  
  return(0);
}