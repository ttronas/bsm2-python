/*
 * storagedelay_bsm2 is a C-file S-function for a second-order filter for storage tank volume.
 * A first-order filter is not enough when the tank is getting empty.
 * It is simply needed to enhance simulation speed for steady state
 * calculations as the storage tank volume is used in a feedback loop to the
 * storage tank bypass system. For steady state calculations we do not want a
 * hybrid system, which would be the result if using a memory function,
 * first-order hold function etc.
 *
 * Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden
 */

#define S_FUNCTION_NAME storagedelay_bsm2

#include "simstruc.h"

#define XINIT   ssGetArg(S,0)
#define T       ssGetArg(S,1)

/*
 * mdlInitializeSizes - initialize the sizes array
 */
static void mdlInitializeSizes(SimStruct *S)
{
    ssSetNumContStates(    S, 2);  /* number of continuous states           */
    ssSetNumDiscStates(    S, 0);   /* number of discrete states             */
    ssSetNumInputs(        S, 1);  /* number of inputs                      */
    ssSetNumOutputs(       S, 1);  /* number of outputs                     */
    ssSetDirectFeedThrough(S, 0);   /* direct feedthrough flag               */
    ssSetNumSampleTimes(   S, 1);   /* number of sample times                */
    ssSetNumSFcnParams(    S, 2);   /* number of input arguments             */
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

   x0[0] = mxGetPr(XINIT)[0];
   x0[1] = mxGetPr(XINIT)[0];
}

/*
 * mdlOutputs - compute the outputs
 */

static void mdlOutputs(double *y, double *x, double *u, SimStruct *S, int tid)
{
      y[0] = x[1];
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
double timeconst;

timeconst = mxGetPr(T)[0];

if (timeconst > 0.000001) {
  dx[0] = (u[0]-x[0])/timeconst;
  dx[1] = (x[0]-x[1])/timeconst;
  }
else {
  dx[0] = 0.0;
  dx[1] = 0.0;

  x[0] = u[0];
  x[1] = u[0];
}
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
