/*
 * storagebypass_bsm2.c is a C-file S-function defining the 
 * rules for potential necessary bypass of the storage tank.
 * See documentation by Dr Marie-Noelle Pons.
 * If liquid volume > 90% of total volume then automatically bypass flow.
 * If liquid volume < 10% of total volume then automatically input flow.
 * Storage output and automatic bypass streams are joined in a flow combiner outside this module.
 * Output(22) is current output flow from the storage tank.
 * Input(22) is the requested output flow from a controller.
 * Input(23) is the current volume in the storage tank.
 * 
 * Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden
 *
 */

#define S_FUNCTION_NAME storagebypass_bsm2

#include "simstruc.h"
#include <math.h>

#define V	       ssGetArg(S,0)

/*
 * mdlInitializeSizes - initialize the sizes array
 */
static void mdlInitializeSizes(SimStruct *S)
{
    ssSetNumContStates(    S, 0);  /* number of continuous states           */
    ssSetNumDiscStates(    S, 0);   /* number of discrete states             */
    ssSetNumInputs(        S, 23);  /* number of inputs                      */
    ssSetNumOutputs(       S, 43);  /* number of outputs                     */
    ssSetDirectFeedThrough(S, 1);   /* direct feedthrough flag               */
    ssSetNumSampleTimes(   S, 1);   /* number of sample times                */
    ssSetNumSFcnParams(    S, 1);   /* number of input arguments             */
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
}

/*
 * mdlOutputs - compute the outputs
 */

static void mdlOutputs(double *y, double *x, double *u, SimStruct *S, int tid)
{
double vol, Qin_s, Qout_s, Qbypass_s;
int i;

vol = mxGetPr(V)[0];

if ((u[22] <= (vol*0.9)) && (u[22] >= (vol*0.1))) {
    Qin_s = u[14];
    Qout_s = u[21];
    Qbypass_s = 0.0;
}
if ((u[22] >= (vol*0.9)) && (u[14] > u[21])) {
    Qin_s = 0.0;
    Qout_s = 0.0;
    Qbypass_s = u[14];
}
if ((u[22] >= (vol*0.9)) && (u[14] <= u[21])) {
    Qin_s = u[14];
    Qout_s = u[21];
    Qbypass_s = 0.0;
}
if (u[22] <= (vol*0.1)) {
    Qin_s = u[14];
    Qout_s = 0.0;
    Qbypass_s = 0.0;
}
  
  for (i = 0; i < 14; i++) {
      y[i] = u[i];
      }

 y[14] = Qin_s; 
 y[15] = u[15];                                  
         
 y[16] = u[16];
 y[17] = u[17];
 y[18] = u[18];
 y[19] = u[19];
 y[20] = u[20];

 y[21] = Qout_s;    /* next output flow rate for storage tank */
 
 /* The potentially bypassed flow */
 for (i = 22; i < 36; i++) {
    y[i] = u[i-22];
    }

  y[36] = Qbypass_s;    /* bypassed flow rate */
  y[37] = u[15];                        
         
 /* dummy states, no need for non-activatation */
  y[38] = u[16];
  y[39] = u[17];
  y[40] = u[18];
  y[41] = u[19];
  y[42] = u[20];
 
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


