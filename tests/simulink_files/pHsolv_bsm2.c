/*
 * pHsolv_bsm2.c is a C-file S-function level 2 that calculates the algebraic equations for pH and ion states of the ADM1 model. 
 * This solver is based on the implementation proposed by Dr Eveline Volcke, BIOMATH, Ghent University, Belgium.
 * Computational speed could be further enhanced by sending all parameters directly from the adm1 module
 * instead of recalculating them within this module.
 * 
 * Copyright (2006):
 * Dr Christian Rosen, Dr Darko Vrecko and Dr Ulf Jeppsson
 * Dept. Industrial Electrical Engineering and Automation (IEA)
 * Lund University, Sweden
 * http://www.iea.lth.se/ 
 */


#define S_FUNCTION_NAME pHsolv_bsm2
#define S_FUNCTION_LEVEL 2

#include "simstruc.h"
#include <math.h>

#define XINIT(S) ssGetSFcnParam(S,0)
#define PAR(S) ssGetSFcnParam(S,1)


/* 
 * mdlInitializeSizes:
 * The sizes information is used by Simulink to determine the S-function
 * block's characteristics (number of inputs, outputs, states, etc.).
 */
static void mdlInitializeSizes(SimStruct *S)
{
    ssSetNumSFcnParams(S, 2); /* Number of expected parameters */
    if (ssGetNumSFcnParams(S) != ssGetSFcnParamsCount(S)) {
    /* Return if number of expected != number of actual parameters */
    return;
}

    ssSetNumContStates(S, 0);
    ssSetNumDiscStates(S, 7);

    if (!ssSetNumInputPorts(S, 1)) return;
    ssSetInputPortWidth(S, 0, 51); /*(S, port index, port width)*/

    ssSetInputPortDirectFeedThrough(S, 0, 0);

    if (!ssSetNumOutputPorts(S, 1)) return;
    ssSetOutputPortWidth(S, 0, 7);

    ssSetNumSampleTimes(S, 1);

    ssSetOptions(S, SS_OPTION_EXCEPTION_FREE_CODE);
}


/* 
 * mdlInitializeSampleTimes: 
 * This function is used to specify the sample time(s) for your
 * S-function. You must register the same number of sample times as
 * specified in ssSetNumSampleTimes.
 */
static void mdlInitializeSampleTimes(SimStruct *S)
{
    ssSetSampleTime(S, 0, INHERITED_SAMPLE_TIME);
    /* executes whenever driving block executes */
    ssSetOffsetTime(S, 0, 0.0);
}


#define MDL_INITIALIZE_CONDITIONS /* Change to #undef to remove function */
#if defined(MDL_INITIALIZE_CONDITIONS)
/* mdlInitializeConditions: 
 * In this function, you should initialize the continuous and discrete
 * states for your S-function block. The initial states are placed
 * in the state vector, ssGetContStates(S) or ssGetRealDiscStates(S).
 * You can also perform any other initialization activities that your
 * S-function may require. Note, this routine will be called at the
 * start of simulation and if it is present in an enabled subsystem
 * configured to reset states, it will be call when the enabled subsystem
 * restarts execution to reset the states.
 */
static void mdlInitializeConditions(SimStruct *S)
{
    real_T *x0 = ssGetDiscStates(S); /* x0 is pointer */
    int_T i;
    
    for (i = 0;i < 7; i++) {
        x0[i] = mxGetPr(XINIT(S))[i];
    }        
}
#endif /* MDL_INITIALIZE_CONDITIONS */


#undef MDL_START /* Change to #undef to remove function */
#if defined(MDL_START)
/* mdlStart:
 * This function is called once at start of model execution. If you
 * have states that should be initialized once, this is the place
 * to do it.
 */
static void mdlStart(SimStruct *S)
{
}
#endif /* MDL_START */


/* 
 * mdlOutputs
 * In this function, you compute the outputs of your S-function
 * block. Generally outputs are placed in the output vector, ssGetY(S).
 */
static void mdlOutputs(SimStruct *S, int_T tid)
{
    real_T *y = ssGetOutputPortRealSignal(S,0);
    real_T *x = ssGetDiscStates(S);
    int_T i;

    for (i = 0; i < 7; i++) {
        y[i] = x[i]; /* state variables are passed on as output variables */
    }  
}


static real_T Equ(SimStruct *S)
{
     real_T *x = ssGetDiscStates(S);
     InputRealPtrsType u = ssGetInputPortRealSignalPtrs(S,0);
      
     static real_T K_w, pK_w_base, K_a_va, pK_a_va_base, K_a_bu, pK_a_bu_base, K_a_pro, pK_a_pro_base, K_a_ac, pK_a_ac_base, K_a_co2, pK_a_co2_base, K_a_IN, pK_a_IN_base, T_base, T_op, R, factor;
      
     R = mxGetPr(PAR(S))[77];
     T_base = mxGetPr(PAR(S))[78];
     T_op = mxGetPr(PAR(S))[79];
     pK_w_base = mxGetPr(PAR(S))[80];
     pK_a_va_base = mxGetPr(PAR(S))[81];
     pK_a_bu_base = mxGetPr(PAR(S))[82];
     pK_a_pro_base = mxGetPr(PAR(S))[83];
     pK_a_ac_base = mxGetPr(PAR(S))[84];
     pK_a_co2_base = mxGetPr(PAR(S))[85];
     pK_a_IN_base = mxGetPr(PAR(S))[86];
     
     factor = (1.0/T_base - 1.0/T_op)/(100.0*R);
     K_w = pow(10,-pK_w_base)*exp(55900.0*factor); /* T adjustment for K_w */
     K_a_va = pow(10,-pK_a_va_base);
     K_a_bu = pow(10,-pK_a_bu_base);
     K_a_pro = pow(10,-pK_a_pro_base);
     K_a_ac = pow(10,-pK_a_ac_base);
     K_a_co2 = pow(10,-pK_a_co2_base)*exp(7646.0*factor); /* T adjustment for K_a_co2 */
     K_a_IN = pow(10,-pK_a_IN_base)*exp(51965.0*factor);  /* T adjustment for K_a_IN */
     
     x[1] = K_a_va**u[3]/(K_a_va+x[0]);   /* Sva- */
     x[2] = K_a_bu**u[4]/(K_a_bu+x[0]);   /* Sbu- */
     x[3] = K_a_pro**u[5]/(K_a_pro+x[0]); /* Spro- */
     x[4] = K_a_ac**u[6]/(K_a_ac+x[0]);   /* Sac- */
     x[5] = K_a_co2**u[9]/(K_a_co2+x[0]); /* SHCO3- */
     x[6] = K_a_IN**u[10]/(K_a_IN+x[0]);  /* SNH3 */
     
     return *u[24]+(*u[10]-x[6])+x[0]-x[5]-x[4]/64-x[3]/112-x[2]/160-x[1]/208-K_w/x[0]-*u[25]; /* SH+ equation */   
}


static real_T gradEqu(SimStruct *S)
{
    real_T *x = ssGetDiscStates(S);
    InputRealPtrsType u = ssGetInputPortRealSignalPtrs(S,0);

    static real_T K_w, pK_w_base, K_a_va, pK_a_va_base, K_a_bu, pK_a_bu_base, K_a_pro, pK_a_pro_base, K_a_ac, pK_a_ac_base, K_a_co2, pK_a_co2_base, K_a_IN, pK_a_IN_base, T_base, T_op, R, factor;
      
     R = mxGetPr(PAR(S))[77];
     T_base = mxGetPr(PAR(S))[78];
     T_op = mxGetPr(PAR(S))[79];
     pK_w_base = mxGetPr(PAR(S))[80];
     pK_a_va_base = mxGetPr(PAR(S))[81];
     pK_a_bu_base = mxGetPr(PAR(S))[82];
     pK_a_pro_base = mxGetPr(PAR(S))[83];
     pK_a_ac_base = mxGetPr(PAR(S))[84];
     pK_a_co2_base = mxGetPr(PAR(S))[85];
     pK_a_IN_base = mxGetPr(PAR(S))[86];
     
     factor = (1.0/T_base - 1.0/T_op)/(100.0*R);
     K_w = pow(10,-pK_w_base)*exp(55900.0*factor); /* T adjustment for K_w */
     K_a_va = pow(10,-pK_a_va_base);
     K_a_bu = pow(10,-pK_a_bu_base);
     K_a_pro = pow(10,-pK_a_pro_base);
     K_a_ac = pow(10,-pK_a_ac_base);
     K_a_co2 = pow(10,-pK_a_co2_base)*exp(7646.0*factor); /* T adjustment for K_a_co2 */
     K_a_IN = pow(10,-pK_a_IN_base)*exp(51965.0*factor);  /* T adjustment for K_a_IN */
     
    return 1+K_a_IN**u[10]/((K_a_IN+x[0])*(K_a_IN+x[0]))           /* Gradient of SH+ equation */
           +K_a_co2**u[9]/((K_a_co2+x[0])*(K_a_co2+x[0]))          
           +1/64.0*K_a_ac**u[6]/((K_a_ac+x[0])*(K_a_ac+x[0]))
           +1/112.0*K_a_pro**u[5]/((K_a_pro+x[0])*(K_a_pro+x[0]))
           +1/160.0*K_a_bu**u[4]/((K_a_bu+x[0])*(K_a_bu+x[0]))
           +1/208.0*K_a_va**u[3]/((K_a_va+x[0])*(K_a_va+x[0]))
           +K_w/(x[0]*x[0]);
}


static void pHsolver(SimStruct *S)
{
    real_T *x = ssGetDiscStates(S);
        
    static real_T delta;
    static real_T S_H_ion0;
    static int_T i;
    
    static const real_T TOL = 1e-12;
    static const real_T MaxSteps= 1000;
    
    S_H_ion0 = x[0]; /* SH+ */
    
    i = 1; 
    delta = 1.0;
    
    /* Newton-Raphson algorithm */
    
    while ( (delta > TOL || delta < -TOL) && (i <= MaxSteps) ) {
        delta = Equ(S);
        x[0] = S_H_ion0 - delta/gradEqu(S); /* Calculate the new SH+ */
        
        if (x[0] <= 0) {
            x[0] = 1e-12; /* to avoid numerical problems */
        }
        
        S_H_ion0 = x[0];
        ++i;
    }     
}


#define MDL_UPDATE /* Change to #undef to remove function */
#if defined(MDL_UPDATE)
/* 
 * mdlUpdate:
 * This function is called once for every major integration time step.
 * Discrete states are typically updated here, but this function is useful
 * for performing any tasks that should only take place once per
 * integration step.
 */
static void mdlUpdate(SimStruct *S, int_T tid)
{   
   pHsolver(S);       
}
#endif /* MDL_UPDATE */


#undef MDL_DERIVATIVES /* Change to #undef to remove function */
#if defined(MDL_DERIVATIVES)
/* 
 * mdlDerivatives:
 * In this function, you compute the S-function block's derivatives. 
 * The derivatives are placed in the derivative vector, ssGetdX(S).
 */
static void mdlDerivatives(SimStruct *S)
{
}
#endif /* MDL_DERIVATIVES */


/* 
 * mdlTerminate:
 * In this function, you should perform any actions that are necessary
 * at the termination of a simulation. For example, if memory was
 * allocated in mdlStart, this is the place to free it.
 */
static void mdlTerminate(SimStruct *S)
{
}


#ifdef MATLAB_MEX_FILE /* Is this file being compiled as a MEX-file? */
#include "simulink.c" /* MEX-file interface mechanism */
#else
#include "cg_sfun.h" /* Code generation registration function */
#endif
