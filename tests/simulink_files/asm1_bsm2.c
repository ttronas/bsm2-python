/*
 * asm1_bsm2 is a C-file S-function for IAWQ AS Model No 1 with temperature 
 * dependencies of the kinetic parameters. In addition to the ASM1 states, TSS
 * and dummy states are included. TEMPMODEL defines how temperature changes
 * in the input affects the reactor temperature. Temperature dependency for 
 * oxygen saturation concentration and KLa has also been added in accordance
 * with BSM2 documentation.
 *
 * Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden
 */

#define S_FUNCTION_NAME asm1_bsm2

#include "simstruc.h"
#include <math.h>

#define XINIT   ssGetArg(S,0)
#define PAR	ssGetArg(S,1)
#define V	ssGetArg(S,2)
#define SOSAT	ssGetArg(S,3)
#define TEMPMODEL  ssGetArg(S,4)
#define ACTIVATE  ssGetArg(S,5)

/*
 * mdlInitializeSizes - initialize the sizes array
 */
static void mdlInitializeSizes(SimStruct *S)
{
    ssSetNumContStates(    S, 21);  /* number of continuous states           */
    ssSetNumDiscStates(    S, 0);   /* number of discrete states             */
    ssSetNumInputs(        S, 22);  /* number of inputs                      */
    ssSetNumOutputs(       S, 21);  /* number of outputs                     */
    ssSetDirectFeedThrough(S, 1);   /* direct feedthrough flag               */
    ssSetNumSampleTimes(   S, 1);   /* number of sample times                */
    ssSetNumSFcnParams(    S, 6);   /* number of input arguments             */
    ssSetNumRWork(         S, 0);   /* number of real work vector elements   */
    ssSetNumIWork(         S, 0);   /* number of integer work vector elements*/
    ssSetNumPWork(         S, 0);   /* number of pointer work vector elements*/
}

/*
 * mdlInitializeSampleTimes - initialize the sample times array
 */
static void mdlInitializeSampleTimes(SimStruct *S)
{
    ssSetSampleTime(S, 0, CONTINUOUS_SAMPLE_TIME);
    ssSetOffsetTime(S, 0, 0.0);
}


/*
 * mdlInitializeConditions - initialize the states
 */
static void mdlInitializeConditions(double *x0, SimStruct *S)
{
int i;

for (i = 0; i < 21; i++) {
   x0[i] = mxGetPr(XINIT)[i];
}
}

/*
 * mdlOutputs - compute the outputs
 */

static void mdlOutputs(double *y, double *x, double *u, SimStruct *S, int tid)
{
  double X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS;
  double tempmodel, activate;
  int i;

  X_I2TSS = mxGetPr(PAR)[19];
  X_S2TSS = mxGetPr(PAR)[20];
  X_BH2TSS = mxGetPr(PAR)[21];
  X_BA2TSS = mxGetPr(PAR)[22];
  X_P2TSS = mxGetPr(PAR)[23];

  tempmodel = mxGetPr(TEMPMODEL)[0];
  activate = mxGetPr(ACTIVATE)[0];
  
  for (i = 0; i < 13; i++) {
      y[i] = x[i];
  }

  y[13] = X_I2TSS*x[2]+X_S2TSS*x[3]+X_BH2TSS*x[4]+X_BA2TSS*x[5]+X_P2TSS*x[6];
  
  y[14] = u[14];                                  /* Flow */

  if (tempmodel < 0.5)                            /* Temp */ 
     y[15] = u[15];                                  
  else 
     y[15] = x[15]; 
         
  /* dummy states, only give outputs if ACTIVATE = 1 */
  if (activate > 0.5) {
      y[16] = x[16];
      y[17] = x[17];
      y[18] = x[18];
      y[19] = x[19];
      y[20] = x[20];
      }
  else if (activate < 0.5) {
      y[16] = 0.0;
      y[17] = 0.0;
      y[18] = 0.0;
      y[19] = 0.0;
      y[20] = 0.0;
      }
}

/*
 * mdlUpdate - perform action at major integration time step
 */

static void mdlUpdate(double *x, double *u, SimStruct *S, int tid)
{
}

/*
 * mdlDerivatives - compute the derivatives
 */
static void mdlDerivatives(double *dx, double *x, double *u, SimStruct *S, int tid)
{

double mu_H, K_S, K_OH, K_NO, b_H, mu_A, K_NH, K_OA, b_A, ny_g, k_a, k_h, K_X, ny_h;
double Y_H, Y_A, f_P, i_XB, i_XP;
double proc1, proc2, proc3, proc4, proc5, proc6, proc7, proc8, proc3x;
double reac1, reac2, reac3, reac4, reac5, reac6, reac7, reac8, reac9, reac10, reac11, reac12, reac13, reac16, reac17, reac18, reac19, reac20;
double vol, SO_sat, SO_sat_temp, KLa_temp;
double xtemp[21];
double tempmodel;
int i;

mu_H = mxGetPr(PAR)[0];
K_S = mxGetPr(PAR)[1];
K_OH = mxGetPr(PAR)[2];
K_NO = mxGetPr(PAR)[3];
b_H = mxGetPr(PAR)[4];
mu_A = mxGetPr(PAR)[5];
K_NH = mxGetPr(PAR)[6];
K_OA = mxGetPr(PAR)[7];
b_A = mxGetPr(PAR)[8];
ny_g = mxGetPr(PAR)[9];
k_a = mxGetPr(PAR)[10];
k_h = mxGetPr(PAR)[11];
K_X = mxGetPr(PAR)[12];
ny_h = mxGetPr(PAR)[13];
Y_H = mxGetPr(PAR)[14];
Y_A = mxGetPr(PAR)[15];
f_P = mxGetPr(PAR)[16];
i_XB = mxGetPr(PAR)[17];
i_XP = mxGetPr(PAR)[18];
vol = mxGetPr(V)[0];
SO_sat = mxGetPr(SOSAT)[0];

tempmodel = mxGetPr(TEMPMODEL)[0];

/* temperature compensation */
if (tempmodel < 0.5) {                            
   mu_H = mu_H*exp((log(mu_H/3.0)/5.0)*(u[15]-15.0)); /* Compensation from the temperature at the influent of the reactor */
   b_H = b_H*exp((log(b_H/0.2)/5.0)*(u[15]-15.0));
   mu_A = mu_A*exp((log(mu_A/0.3)/5.0)*(u[15]-15.0));
   b_A = b_A*exp((log(b_A/0.03)/5.0)*(u[15]-15.0));
   k_h = k_h*exp((log(k_h/2.5)/5.0)*(u[15]-15.0));
   k_a = k_a*exp((log(k_a/0.04)/5.0)*(u[15]-15.0));
   SO_sat_temp = 0.9997743214*8.0/10.5*(56.12*6791.5*exp(-66.7354 + 87.4755/((u[15]+273.15)/100.0) + 24.4526*log((u[15]+273.15)/100.0))); /* van't Hoff equation */
   KLa_temp = u[21]*pow(1.024, (u[15]-15.0));
}
else {
   mu_H = mu_H*exp((log(mu_H/3.0)/5.0)*(x[15]-15.0)); /* Compensation from the current temperature in the reactor */
   b_H = b_H*exp((log(b_H/0.2)/5.0)*(x[15]-15.0));
   mu_A = mu_A*exp((log(mu_A/0.3)/5.0)*(x[15]-15.0));
   b_A = b_A*exp((log(b_A/0.03)/5.0)*(x[15]-15.0));
   k_h = k_h*exp((log(k_h/2.5)/5.0)*(x[15]-15.0));
   k_a = k_a*exp((log(k_a/0.04)/5.0)*(x[15]-15.0));
   SO_sat_temp = 0.9997743214*8.0/10.5*(56.12*6791.5*exp(-66.7354 + 87.4755/((x[15]+273.15)/100.0) + 24.4526*log((x[15]+273.15)/100.0))); /* van't Hoff equation */
   KLa_temp = u[21]*pow(1.024, (x[15]-15.0));
} 

for (i = 0; i < 21; i++) {
   if (x[i] < 0.0)
     xtemp[i] = 0.0;
   else
     xtemp[i] = x[i];
}

if (u[21] < 0.0)
      x[7] = fabs(u[21]);

proc1 = mu_H*(xtemp[1]/(K_S+xtemp[1]))*(xtemp[7]/(K_OH+xtemp[7]))*xtemp[4];
proc2 = mu_H*(xtemp[1]/(K_S+xtemp[1]))*(K_OH/(K_OH+xtemp[7]))*(xtemp[8]/(K_NO+xtemp[8]))*ny_g*xtemp[4];
proc3 = mu_A*(xtemp[9]/(K_NH+xtemp[9]))*(xtemp[7]/(K_OA+xtemp[7]))*xtemp[5];
proc4 = b_H*xtemp[4];
proc5 = b_A*xtemp[5];
proc6 = k_a*xtemp[10]*xtemp[4];
proc7 = k_h*((xtemp[3]/xtemp[4])/(K_X+(xtemp[3]/xtemp[4])))*((xtemp[7]/(K_OH+xtemp[7]))+ny_h*(K_OH/(K_OH+xtemp[7]))*(xtemp[8]/(K_NO+xtemp[8])))*xtemp[4];
proc8 = proc7*xtemp[11]/xtemp[3];

reac1 = 0.0;
reac2 = (-proc1-proc2)/Y_H+proc7;
reac3 = 0.0;
reac4 = (1.0-f_P)*(proc4+proc5)-proc7;
reac5 = proc1+proc2-proc4;
reac6 = proc3-proc5;
reac7 = f_P*(proc4+proc5);
reac8 = -((1.0-Y_H)/Y_H)*proc1-((4.57-Y_A)/Y_A)*proc3;
reac9 = -((1.0-Y_H)/(2.86*Y_H))*proc2+proc3/Y_A;
reac10 = -i_XB*(proc1+proc2)-(i_XB+(1.0/Y_A))*proc3+proc6;
reac11 = -proc6+proc8;
reac12 = (i_XB-f_P*i_XP)*(proc4+proc5)-proc8;
reac13 = -i_XB/14.0*proc1+((1.0-Y_H)/(14.0*2.86*Y_H)-(i_XB/14.0))*proc2-((i_XB/14.0)+1.0/(7.0*Y_A))*proc3+proc6/14.0;

reac16 = 0.0;
reac17 = 0.0;
reac18 = 0.0;
reac19 = 0.0;
reac20 = 0.0;

dx[0] = 1.0/vol*(u[14]*(u[0]-x[0]))+reac1;
dx[1] = 1.0/vol*(u[14]*(u[1]-x[1]))+reac2;
dx[2] = 1.0/vol*(u[14]*(u[2]-x[2]))+reac3;
dx[3] = 1.0/vol*(u[14]*(u[3]-x[3]))+reac4;
dx[4] = 1.0/vol*(u[14]*(u[4]-x[4]))+reac5;
dx[5] = 1.0/vol*(u[14]*(u[5]-x[5]))+reac6;
dx[6] = 1.0/vol*(u[14]*(u[6]-x[6]))+reac7;
if (u[21] < 0.0)
      dx[7] = 0.0;
else
      dx[7] = 1.0/vol*(u[14]*(u[7]-x[7]))+reac8+KLa_temp*(SO_sat_temp-x[7]);
dx[8] = 1.0/vol*(u[14]*(u[8]-x[8]))+reac9;
dx[9] = 1.0/vol*(u[14]*(u[9]-x[9]))+reac10;
dx[10] = 1.0/vol*(u[14]*(u[10]-x[10]))+reac11;
dx[11] = 1.0/vol*(u[14]*(u[11]-x[11]))+reac12;
dx[12] = 1.0/vol*(u[14]*(u[12]-x[12]))+reac13;

dx[13] = 0.0; /* TSS */

dx[14] = 0.0; /* Flow */

if (tempmodel < 0.5)               /* Temp */    
   dx[15] = 0.0;                                  
else 
   dx[15] = 1.0/vol*(u[14]*(u[15]-x[15]));  
  

/* dummy states, only dilution at this point */
dx[16] = 1.0/vol*(u[14]*(u[16]-x[16]))+reac16;
dx[17] = 1.0/vol*(u[14]*(u[17]-x[17]))+reac17;
dx[18] = 1.0/vol*(u[14]*(u[18]-x[18]))+reac18;
dx[19] = 1.0/vol*(u[14]*(u[19]-x[19]))+reac19;
dx[20] = 1.0/vol*(u[14]*(u[20]-x[20]))+reac20;

}


/*
 * mdlTerminate - called when the simulation is terminated.
 */
static void mdlTerminate(SimStruct *S)
{
}

#ifdef	MATLAB_MEX_FILE    /* Is this file being compiled as a MEX-file? */
#include "simulink.c"      /* MEX-file interface mechanism */
#else
#include "cg_sfun.h"       /* Code generation registration function */
#endif


