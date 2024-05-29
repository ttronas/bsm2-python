/*
 * storage_bsm2.c is a C-file S-function for a simple storage tank
 * of variable volume V with complete mix. No biological reactions.
 * Dummy states are included. TEMPMODEL defines how temperature changes
 * in the input affects the liquid temperature. ACTIVATE used to
 * activate dummy states.
 * See documentation by Dr Marie-Noelle Pons.
 * Works together with storagebypass_bsm2.c
 * Storage output and automatic bypass streams are joined in a flow combiner outside this module.
 * System is initiated with 50% liquid volume in tank.
 * Input(22) is the calculated output flow rate for next integration step.
 * Output(22) is current liquid volume to be used for control purposes.
 *
 * Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden
 *
 */

#define S_FUNCTION_NAME storage_bsm2

#include "simstruc.h"
#include <math.h>

#define XINIT      ssGetArg(S,0)
#define V	       ssGetArg(S,1)
#define TEMPMODEL  ssGetArg(S,2)
#define ACTIVATE   ssGetArg(S,3)

/*
 * mdlInitializeSizes - initialize the sizes array
 */
static void mdlInitializeSizes(SimStruct *S)
{
    ssSetNumContStates(    S, 22);  /* number of continuous states           */
    ssSetNumDiscStates(    S, 0);   /* number of discrete states             */
    ssSetNumInputs(        S, 22);  /* number of inputs                      */
    ssSetNumOutputs(       S, 22);  /* number of outputs                     */
    ssSetDirectFeedThrough(S, 1);   /* direct feedthrough flag               */
    ssSetNumSampleTimes(   S, 1);   /* number of sample times                */
    ssSetNumSFcnParams(    S, 4);   /* number of input arguments             */
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

for (i = 0; i < 22; i++) {
   x0[i] = mxGetPr(XINIT)[i];
}
}

/*
 * mdlOutputs - compute the outputs
 */

static void mdlOutputs(double *y, double *x, double *u, SimStruct *S, int tid)
{
  double tempmodel, activate;
  int i;

  tempmodel = mxGetPr(TEMPMODEL)[0];
  activate = mxGetPr(ACTIVATE)[0];

  for (i = 0; i < 14; i++) {
      y[i] = x[i];
      }

  y[14] = u[21];        /* output flow rate was calculated in storagebypass_bsm2.c */

  if (tempmodel < 0.5)   /* Temp */
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

  y[21] = x[21];     /* current liquid volume in storage tank, needed for control */
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
double vol;
double tempmodel, activate;

vol = mxGetPr(V)[0];
tempmodel = mxGetPr(TEMPMODEL)[0];
activate = mxGetPr(ACTIVATE)[0];

dx[0] = u[14]/x[21]*(u[0]-x[0]);
dx[1] = u[14]/x[21]*(u[1]-x[1]);
dx[2] = u[14]/x[21]*(u[2]-x[2]);
dx[3] = u[14]/x[21]*(u[3]-x[3]);
dx[4] = u[14]/x[21]*(u[4]-x[4]);
dx[5] = u[14]/x[21]*(u[5]-x[5]);
dx[6] = u[14]/x[21]*(u[6]-x[6]);
dx[7] = u[14]/x[21]*(u[7]-x[7]);
dx[8] = u[14]/x[21]*(u[8]-x[8]);
dx[9] = u[14]/x[21]*(u[9]-x[9]);
dx[10] = u[14]/x[21]*(u[10]-x[10]);
dx[11] = u[14]/x[21]*(u[11]-x[11]);
dx[12] = u[14]/x[21]*(u[12]-x[12]);
dx[13] = u[14]/x[21]*(u[13]-x[13]);

dx[14] = 0.0;           /* Flow */

if (tempmodel < 0.5)    /* Temp */
   dx[15] = 0.0;
else
   dx[15] = u[14]/x[21]*(u[15]-x[15]);

/* dummy states */
if (activate > 0.5) {
   dx[16] = u[14]/x[21]*(u[16]-x[16]);
   dx[17] = u[14]/x[21]*(u[17]-x[17]);
   dx[18] = u[14]/x[21]*(u[18]-x[18]);
   dx[19] = u[14]/x[21]*(u[19]-x[19]);
   dx[20] = u[14]/x[21]*(u[20]-x[20]);
   }
 else if (activate < 0.5) {
   dx[16] = 0.0;
   dx[17] = 0.0;
   dx[18] = 0.0;
   dx[19] = 0.0;
   dx[20] = 0.0;
   }

dx[21] = u[14] - u[21];   /* variable liquid volume */
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
