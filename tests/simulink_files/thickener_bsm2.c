/*
 * thickener_bsm2.c calculates the overflow and underflow concentrations   
 * from an 'ideal' thickener unit based on a fixed percentage of sludge in
 * the underflow flow. A defined amount of total solids are removed from
 * the water stream and goes into the sludge stream and the remaining will
 * leave with the water phase. Soluble concentrations are not affected.
 * Temperature is also handled ideally, i.e. T(out)=T(in).
 *  
 * Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden
 */

#define S_FUNCTION_NAME thickener_bsm2

#include "simstruc.h"

#define PAR	ssGetArg(S,0)

/*
 * mdlInitializeSizes - initialize the sizes array
 */
static void mdlInitializeSizes(SimStruct *S)
{
    ssSetNumContStates(    S, 0);   /* number of continuous states           */
    ssSetNumDiscStates(    S, 0);   /* number of discrete states             */
    ssSetNumInputs(        S, 21);  /* number of inputs                      */
    ssSetNumOutputs(       S, 42);  /* number of outputs                     */
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
  double thickener_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS, TSS_removal_perc, thickener_factor, TSSin, Qu_factor, thinning_factor;

  thickener_perc = mxGetPr(PAR)[0];
  TSS_removal_perc = mxGetPr(PAR)[1];
  X_I2TSS = mxGetPr(PAR)[2];
  X_S2TSS = mxGetPr(PAR)[3];
  X_BH2TSS = mxGetPr(PAR)[4];
  X_BA2TSS = mxGetPr(PAR)[5];
  X_P2TSS = mxGetPr(PAR)[6];
  
  TSSin = X_I2TSS*u[2]+X_S2TSS*u[3]+X_BH2TSS*u[4]+X_BA2TSS*u[5]+X_P2TSS*u[6];
  thickener_factor = thickener_perc*10000.0/TSSin; 
  Qu_factor = TSS_removal_perc/(100.0*thickener_factor);
  thinning_factor = (1.0-TSS_removal_perc/100.0)/(1.0-Qu_factor);

  if (thickener_factor > 1) {
    /* underflow */
    y[0]=u[0];
    y[1]=u[1];
    y[2]=u[2]*thickener_factor;
    y[3]=u[3]*thickener_factor;
    y[4]=u[4]*thickener_factor;
    y[5]=u[5]*thickener_factor;
    y[6]=u[6]*thickener_factor;
    y[7]=u[7];
    y[8]=u[8];
    y[9]=u[9];
    y[10]=u[10];
    y[11]=u[11]*thickener_factor;
    y[12]=u[12];
    y[13]=TSSin*thickener_factor;
    y[14]=u[14]*Qu_factor;
    
    y[15]=u[15]; /* Temp */
    
    /* Dummy states */
    y[16]=u[16];
    y[17]=u[17];
    y[18]=u[18];
    y[19]=u[19]*thickener_factor;
    y[20]=u[20]*thickener_factor;
        
   /* overflow */
    y[21]=u[0];
    y[22]=u[1];
    y[23]=u[2]*thinning_factor;
    y[24]=u[3]*thinning_factor;
    y[25]=u[4]*thinning_factor;
    y[26]=u[5]*thinning_factor;
    y[27]=u[6]*thinning_factor;
    y[28]=u[7];
    y[29]=u[8];
    y[30]=u[9];
    y[31]=u[10];
    y[32]=u[11]*thinning_factor;
    y[33]=u[12];
    y[34]=TSSin*thinning_factor;
    y[35]=u[14]*(1.0-Qu_factor);
    
    y[36]=u[15]; /* Temp */
    
    /* Dummy states */
    y[37]=u[16];
    y[38]=u[17];
    y[39]=u[18];
    y[40]=u[19]*thinning_factor;
    y[41]=u[20]*thinning_factor;
    }
  else 
  /* the influent is too high on solids to thicken further */
  /* all the influent leaves with the underflow */
  {
    y[0]=u[0];
    y[1]=u[1];
    y[2]=u[2];
    y[3]=u[3];
    y[4]=u[4];
    y[5]=u[5];
    y[6]=u[6];
    y[7]=u[7];
    y[8]=u[8];
    y[9]=u[9];
    y[10]=u[10];
    y[11]=u[11];
    y[12]=u[12];
    y[13]=TSSin;
    y[14]=u[14];
    y[15]=u[15];
    y[16]=u[16];
    y[17]=u[17];
    y[18]=u[18];
    y[19]=u[19];
    y[20]=u[20];
    
    y[21]=0.0;
    y[22]=0.0;
    y[23]=0.0;
    y[24]=0.0;
    y[25]=0.0;
    y[26]=0.0;
    y[27]=0.0;
    y[28]=0.0;
    y[29]=0.0;
    y[30]=0.0;
    y[31]=0.0;
    y[32]=0.0;
    y[33]=0.0;
    y[34]=0.0;
    y[35]=0.0;
    y[36]=0.0;
    y[37]=0.0;
    y[38]=0.0;
    y[39]=0.0;
    y[40]=0.0;
    y[41]=0.0;
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

