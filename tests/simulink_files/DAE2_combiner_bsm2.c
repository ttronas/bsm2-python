/*
 * The DAE2_combiner_bsm2.c is a C-file S-function level 2 for a speed-enhanced IAWQ AD Model No 1.
 * In this model the traditional states of the ADM1 and ion states + Sh2
 * from the last iteration of the pHsolver and Sh2solver are combined to create the overall output
 * at time t for all variables rather than using values for the ion states and h2
 * that are one iteration old (h2 may still be considered old as it is based on the old pH
 * but this is really a question of the chicken and the egg).
 *
 * Copyright (2007):
 * Dr Ulf Jeppsson
 * Dept. Industrial Electrical Engineering and Automation (IEA)
 * Lund University, Sweden
 * http://www.iea.lth.se/
 */

#define S_FUNCTION_NAME  DAE2_combiner_bsm2
#define S_FUNCTION_LEVEL 2

#include "simstruc.h"
#include <math.h>

/* Input Parameters */

/*
 * mdlInitializeSizes:
 *    The sizes information is used by Simulink to determine the S-function
 *    block's characteristics (number of inputs, outputs, states, etc.).
 */
static void mdlInitializeSizes(SimStruct *S)
{

    ssSetNumSFcnParams(S, 0);  /* Number of expected parameters */
    if (ssGetNumSFcnParams(S) != ssGetSFcnParamsCount(S)) {
        return;  /* Return if number of expected != number of actual parameters */
    }

    ssSetNumContStates(S, 0);
    ssSetNumDiscStates(S, 0);

    if (!ssSetNumInputPorts(S, 1)) return;
    ssSetInputPortWidth(S, 0, 59); /*(S, port index, port width) */

    ssSetInputPortDirectFeedThrough(S, 0, 1);

    if (!ssSetNumOutputPorts(S, 1)) return;
    ssSetOutputPortWidth(S, 0, 51);

    ssSetNumSampleTimes(S, 1);
    ssSetNumRWork(S, 0);
    ssSetNumIWork(S, 0);
    ssSetNumPWork(S, 0);
    ssSetNumModes(S, 0);
    ssSetNumNonsampledZCs(S, 0);

    ssSetOptions(S, SS_OPTION_EXCEPTION_FREE_CODE);
}


/*
 * mdlInitializeSampleTimes:
 *    This function is used to specify the sample time(s) for your
 *    S-function. You must register the same number of sample times as
 *    specified in ssSetNumSampleTimes.
 */
static void mdlInitializeSampleTimes(SimStruct *S)
{
    ssSetSampleTime(S, 0, CONTINUOUS_SAMPLE_TIME);
    ssSetOffsetTime(S, 0, 0.0);
}


#undef MDL_INITIALIZE_CONDITIONS   /* Change to #undef to remove function */
#if defined(MDL_INITIALIZE_CONDITIONS)
  /*
   * mdlInitializeConditions:
   *    In this function, you should initialize the continuous and discrete
   *    states for your S-function block.  The initial states are placed
   *    in the state vector, ssGetContStates(S) or ssGetRealDiscStates(S).
   *    You can also perform any other initialization activities that your
   *    S-function may require. Note, this routine will be called at the
   *    start of simulation and if it is present in an enabled subsystem
   *    configured to reset states, it will be call when the enabled subsystem
   *    restarts execution to reset the states.
   */
  static void mdlInitializeConditions(SimStruct *S)
  {
  }
#endif /* MDL_INITIALIZE_CONDITIONS */


#undef MDL_START  /* Change to #undef to remove function */
#if defined(MDL_START)
  /*
   * mdlStart:
   *    This function is called once at start of model execution. If you
   *    have states that should be initialized once, this is the place
   *    to do it.
   */
  static void mdlStart(SimStruct *S)
  {
  }
#endif /*  MDL_START */


/*
 * mdlOutputs:
 *    In this function, you compute the outputs of your S-function
 *    block. Generally outputs are placed in the output vector, ssGetY(S).
 */
static void mdlOutputs(SimStruct *S, int_T tid)
{
  real_T *y = ssGetOutputPortRealSignal(S,0);
  InputRealPtrsType u = ssGetInputPortRealSignalPtrs(S,0);

  int_T i;

  for (i = 0; i < 33; i++) {
      y[i] = *u[i];
  }

  y[7] = *u[58];   /* Sh2 */

  y[33] = -log10(*u[51]);    /* pH */
  y[34] = *u[51];            /* SH+ */
  y[35] = *u[52];  /* Sva- */
  y[36] = *u[53];  /* Sbu- */
  y[37] = *u[54];  /* Spro- */
  y[38] = *u[55];  /* Sac- */
  y[39] = *u[56];  /* SHCO3- */
  y[40] = *u[9] - *u[56];        /* SCO2 */
  y[41] = *u[57];  /* SNH3 */
  y[42] = *u[10] - *u[57];       /* SNH4+ */
  y[43] = *u[43];
  y[44] = *u[44];
  y[45] = *u[45];
  y[46] = *u[46];
  y[47] = *u[47];
  y[48] = *u[48];
  y[49] = *u[49];
  y[50] = *u[50];
}


#undef MDL_UPDATE  /* Change to #undef to remove function */
#if defined(MDL_UPDATE)
  /*
   * mdlUpdate:
   *    This function is called once for every major integration time step.
   *    Discrete states are typically updated here, but this function is useful
   *    for performing any tasks that should only take place once per
   *    integration step.
   */
  static void mdlUpdate(SimStruct *S, int_T tid)
  {
  }
#endif /* MDL_UPDATE */


#undef MDL_DERIVATIVES  /* Change to #undef to remove function */
#if defined(MDL_DERIVATIVES)
  /*
   * mdlDerivatives:
   *    In this function, you compute the S-function block's derivatives.
   *    The derivatives are placed in the derivative vector, ssGetdX(S).
   */
  static void mdlDerivatives(SimStruct *S)
  {
  }
#endif /* MDL_DERIVATIVES */


/*
 * mdlTerminate:
 *    In this function, you should perform any actions that are necessary
 *    at the termination of a simulation.  For example, if memory was
 *    allocated in mdlStart, this is the place to free it.
 */
static void mdlTerminate(SimStruct *S)
{
}


#ifdef  MATLAB_MEX_FILE    /* Is this file being compiled as a MEX-file? */
#include "simulink.c"      /* MEX-file interface mechanism */
#else
#include "cg_sfun.h"       /* Code generation registration function */
#endif
