/*
 * Sh2solv_bsm2.c is a C-file S-function level 2 that solves the algebraic equation for Sh2 of the ADM1 model,
 * thereby reducing the stiffness of the system considerably (if used together with a pHsolver). 
 * 
 * Copyright (2006):
 * Dr Christian Rosen, Dr Darko Vrecko and Dr Ulf Jeppsson
 * Dept. Industrial Electrical Engineering and Automation (IEA)
 * Lund University, Sweden
 * http://www.iea.lth.se/ 
 */


#define S_FUNCTION_NAME Sh2solv_bsm2
#define S_FUNCTION_LEVEL 2

#include "simstruc.h"
#include <math.h>

#define XINIT(S) ssGetSFcnParam(S,0)
#define PAR(S) ssGetSFcnParam(S,1)
#define V(S)      ssGetSFcnParam(S,2)


/* 
 * mdlInitializeSizes:
 * The sizes information is used by Simulink to determine the S-function
 * block's characteristics (number of inputs, outputs, states, etc.).
 */
static void mdlInitializeSizes(SimStruct *S)
{
    ssSetNumSFcnParams(S, 3); /* Number of expected parameters */
    if (ssGetNumSFcnParams(S) != ssGetSFcnParamsCount(S)) {
    /* Return if number of expected != number of actual parameters */
    return;
}

    ssSetNumContStates(S, 0);
    ssSetNumDiscStates(S, 1);

    if (!ssSetNumInputPorts(S, 1)) return;
    ssSetInputPortWidth(S, 0, 52); /*(S, port index, port width)*/

    ssSetInputPortDirectFeedThrough(S, 0, 0);

    if (!ssSetNumOutputPorts(S, 1)) return;
    ssSetOutputPortWidth(S, 0, 1);

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
    real_T *x0 = ssGetDiscStates(S); /*x0 is pointer*/
        
    x0[0] = mxGetPr(XINIT(S))[0];   
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
    
    y[0] = x[0]; /* state variable is passed on as output variable */   
}


static real_T Equ(SimStruct *S)
{
     real_T *x = ssGetDiscStates(S);
     InputRealPtrsType u = ssGetInputPortRealSignalPtrs(S,0);
      
     static real_T eps, f_h2_su, Y_su, f_h2_aa, Y_aa, Y_fa, Y_c4, Y_pro, K_S_IN, k_m_su, K_S_su, pH_UL_aa, pH_LL_aa, k_m_aa;
     static real_T K_S_aa, k_m_fa, K_S_fa, K_Ih2_fa, k_m_c4, K_S_c4, K_Ih2_c4, k_m_pro, K_S_pro, K_Ih2_pro;
     static real_T pH_UL_ac, pH_LL_ac, k_m_h2, K_S_h2, pH_UL_h2, pH_LL_h2, R, T_base, T_op, kLa, K_H_h2, K_H_h2_base, V_liq, pH_op,I_pH_aa;
     static real_T I_pH_h2, I_IN_lim, I_h2_fa, I_h2_c4, I_h2_pro, inhib[6]; 
     static real_T proc5, proc6, proc7, proc8, proc9, proc10, proc12, p_gas_h2, procT8, reac8;
     static real_T pHLim_aa, pHLim_h2, a_aa, a_h2, S_H_ion, n_aa, n_h2;

     eps = 0.000001;
     
     f_h2_su = mxGetPr(PAR(S))[18];
     Y_su = mxGetPr(PAR(S))[27];
     f_h2_aa = mxGetPr(PAR(S))[28];
     Y_aa = mxGetPr(PAR(S))[34];
     Y_fa = mxGetPr(PAR(S))[35];
     Y_c4 = mxGetPr(PAR(S))[36];
     Y_pro = mxGetPr(PAR(S))[37];
     K_S_IN = mxGetPr(PAR(S))[45];
     k_m_su = mxGetPr(PAR(S))[46];
     K_S_su = mxGetPr(PAR(S))[47];
     pH_UL_aa = mxGetPr(PAR(S))[48];
     pH_LL_aa = mxGetPr(PAR(S))[49];
     k_m_aa = mxGetPr(PAR(S))[50];
     K_S_aa = mxGetPr(PAR(S))[51];
     k_m_fa = mxGetPr(PAR(S))[52];
     K_S_fa = mxGetPr(PAR(S))[53];
     K_Ih2_fa = mxGetPr(PAR(S))[54];
     k_m_c4 = mxGetPr(PAR(S))[55];
     K_S_c4 = mxGetPr(PAR(S))[56];
     K_Ih2_c4 = mxGetPr(PAR(S))[57];
     k_m_pro = mxGetPr(PAR(S))[58];
     K_S_pro = mxGetPr(PAR(S))[59];
     K_Ih2_pro = mxGetPr(PAR(S))[60];
     pH_UL_ac = mxGetPr(PAR(S))[64];
     pH_LL_ac = mxGetPr(PAR(S))[65];
     k_m_h2 = mxGetPr(PAR(S))[66];
     K_S_h2 = mxGetPr(PAR(S))[67];
     pH_UL_h2 = mxGetPr(PAR(S))[68];
     pH_LL_h2 = mxGetPr(PAR(S))[69];
     R = mxGetPr(PAR(S))[77];
     T_base = mxGetPr(PAR(S))[78]; 
     T_op = mxGetPr(PAR(S))[79]; 
     kLa = mxGetPr(PAR(S))[94];
     K_H_h2_base = mxGetPr(PAR(S))[98];
     V_liq = mxGetPr(V(S))[0];
  
     K_H_h2 = K_H_h2_base*exp(-4180.0*(1.0/T_base - 1.0/T_op)/(100.0*R));     /* T adjustment for K_H_h2 */
     
     pH_op = *u[33];   /* pH */
     S_H_ion = *u[34]; /* SH+ */
   
   /* STRs function
   if (pH_op < pH_UL_aa)
    I_pH_aa = exp(-3.0*(pH_op-pH_UL_aa)*(pH_op-pH_UL_aa)/((pH_UL_aa-pH_LL_aa)*(pH_UL_aa-pH_LL_aa)));
   else
    I_pH_aa = 1.0;
   if (pH_op < pH_UL_h2)
    I_pH_h2 = exp(-3.0*(pH_op-pH_UL_h2)*(pH_op-pH_UL_h2)/((pH_UL_h2-pH_LL_h2)*(pH_UL_h2-pH_LL_h2)));
   else
    I_pH_h2 = 1.0;
   */
   
/* Hill function on pH inhibition
pHLim_aa = (pH_UL_aa + pH_LL_aa)/2.0;
pHLim_ac = (pH_UL_ac + pH_LL_ac)/2.0;
pHLim_h2 = (pH_UL_h2 + pH_LL_h2)/2.0;
I_pH_aa = pow(pH_op,24)/(pow(pH_op,24)+pow(pHLim_aa ,24));
I_pH_ac = pow(pH_op,45)/(pow(pH_op,45)+pow(pHLim_ac ,45));
I_pH_h2 = pow(pH_op,45)/(pow(pH_op,45)+pow(pHLim_h2 ,45));
*/

/* MNPs function on pH inhibition, ADM1 Workshop, Copenhagen 2005.
a_aa = 25.0/(pH_UL_aa-pH_LL_aa+eps);
a_ac = 25.0/(pH_UL_ac-pH_LL_ac+eps);
a_h2 = 25.0/(pH_UL_h2-pH_LL_h2+eps);

I_pH_aa = 0.5*(1+tanh(a_aa*(pH_op/pHLim_aa - 1.0)));
I_pH_ac = 0.5*(1+tanh(a_ac*(pH_op/pHLim_ac - 1.0)));
I_pH_h2 = 0.5*(1+tanh(a_h2*(pH_op/pHLim_h2 - 1.0)));
*/

/* Hill function on SH+ used within BSM2, ADM1 Workshop, Copenhagen 2005. */
     pHLim_aa = pow(10,(-(pH_UL_aa + pH_LL_aa)/2.0));
     pHLim_h2 = pow(10,(-(pH_UL_h2 + pH_LL_h2)/2.0));
     n_aa=3.0/(pH_UL_aa-pH_LL_aa);
     n_h2=3.0/(pH_UL_h2-pH_LL_h2);
     I_pH_aa = pow(pHLim_aa,n_aa)/(pow(S_H_ion,n_aa)+pow(pHLim_aa ,n_aa));
     I_pH_h2 = pow(pHLim_h2,n_h2)/(pow(S_H_ion,n_h2)+pow(pHLim_h2 ,n_h2));

     I_IN_lim = 1.0/(1.0+K_S_IN/(*u[10]));
     I_h2_fa = 1.0/(1.0+x[0]/K_Ih2_fa);
     I_h2_c4 = 1.0/(1.0+x[0]/K_Ih2_c4);
     I_h2_pro = 1.0/(1.0+x[0]/K_Ih2_pro);
          
     inhib[0] = I_pH_aa*I_IN_lim;
     inhib[1] = inhib[0]*I_h2_fa;
     inhib[2] = inhib[0]*I_h2_c4;
     inhib[3] = inhib[0]*I_h2_pro;
     inhib[5] = I_pH_h2*I_IN_lim;
     
     proc5 = k_m_su**u[0]/(K_S_su+*u[0])**u[16]*inhib[0];
     proc6 = k_m_aa**u[1]/(K_S_aa+*u[1])**u[17]*inhib[0];
     proc7 = k_m_fa**u[2]/(K_S_fa+*u[2])**u[18]*inhib[1];
     proc8 = k_m_c4**u[3]/(K_S_c4+*u[3])**u[19]**u[3]/(*u[3]+*u[4]+eps)*inhib[2];
     proc9 = k_m_c4**u[4]/(K_S_c4+*u[4])**u[19]**u[4]/(*u[3]+*u[4]+eps)*inhib[2];
     proc10 = k_m_pro**u[5]/(K_S_pro+*u[5])**u[20]*inhib[3];
     
     proc12 = k_m_h2*x[0]/(K_S_h2+x[0])**u[22]*inhib[5];
     
     p_gas_h2 = *u[43]*R*T_op/16.0;
     procT8 = kLa*(x[0]-16.0*K_H_h2*p_gas_h2);
     
     reac8 = (1.0-Y_su)*f_h2_su*proc5+(1.0-Y_aa)*f_h2_aa*proc6+(1.0-Y_fa)*0.3*proc7+(1.0-Y_c4)*0.15*proc8+(1.0-Y_c4)*0.2*proc9+(1.0-Y_pro)*0.43*proc10-proc12-procT8; 
     
     return 1/V_liq**u[26]*(*u[51]-x[0])+reac8; /* Sh2 equation */
}


static real_T gradEqu(SimStruct *S)
{
     real_T *x = ssGetDiscStates(S);
     InputRealPtrsType u = ssGetInputPortRealSignalPtrs(S,0);
      
     static real_T eps, f_h2_su, Y_su, f_h2_aa, Y_aa, Y_fa, Y_c4, Y_pro, K_S_IN, k_m_su, K_S_su, pH_UL_aa, pH_LL_aa, k_m_aa;
     static real_T K_S_aa, k_m_fa, K_S_fa, K_Ih2_fa, k_m_c4, K_S_c4, K_Ih2_c4, k_m_pro, K_S_pro, K_Ih2_pro;
     static real_T pH_UL_ac, pH_LL_ac, k_m_h2, K_S_h2, pH_UL_h2, pH_LL_h2, R, T_base, T_op, kLa, K_H_h2, K_H_h2_base, V_liq, pH_op, I_pH_aa, I_pH_h2;
     static real_T pHLim_aa, pHLim_h2, a_aa, a_h2, S_H_ion, n_aa, n_h2;
     
     eps = 0.000001;
     
     f_h2_su = mxGetPr(PAR(S))[18];
     Y_su = mxGetPr(PAR(S))[27];
     f_h2_aa = mxGetPr(PAR(S))[28];
     Y_aa = mxGetPr(PAR(S))[34];
     Y_fa = mxGetPr(PAR(S))[35];
     Y_c4 = mxGetPr(PAR(S))[36];
     Y_pro = mxGetPr(PAR(S))[37];
     K_S_IN = mxGetPr(PAR(S))[45];
     k_m_su = mxGetPr(PAR(S))[46];
     K_S_su = mxGetPr(PAR(S))[47];
     pH_UL_aa = mxGetPr(PAR(S))[48];
     pH_LL_aa = mxGetPr(PAR(S))[49];
     k_m_aa = mxGetPr(PAR(S))[50];
     K_S_aa = mxGetPr(PAR(S))[51];
     k_m_fa = mxGetPr(PAR(S))[52];
     K_S_fa = mxGetPr(PAR(S))[53];
     K_Ih2_fa = mxGetPr(PAR(S))[54];
     k_m_c4 = mxGetPr(PAR(S))[55];
     K_S_c4 = mxGetPr(PAR(S))[56];
     K_Ih2_c4 = mxGetPr(PAR(S))[57];
     k_m_pro = mxGetPr(PAR(S))[58];
     K_S_pro = mxGetPr(PAR(S))[59];
     K_Ih2_pro = mxGetPr(PAR(S))[60];
     pH_UL_ac = mxGetPr(PAR(S))[64];
     pH_LL_ac = mxGetPr(PAR(S))[65];
     k_m_h2 = mxGetPr(PAR(S))[66];
     K_S_h2 = mxGetPr(PAR(S))[67];
     pH_UL_h2 = mxGetPr(PAR(S))[68];
     pH_LL_h2 = mxGetPr(PAR(S))[69];
     R = mxGetPr(PAR(S))[77];
     T_base = mxGetPr(PAR(S))[78]; 
     T_op = mxGetPr(PAR(S))[79]; 
     kLa = mxGetPr(PAR(S))[94];
     K_H_h2_base = mxGetPr(PAR(S))[98];
     V_liq = mxGetPr(V(S))[0];

     K_H_h2 = K_H_h2_base*exp(-4180.0*(1.0/T_base - 1.0/T_op)/(100.0*R));     /* T adjustment for K_H_h2 */
          
     pH_op = *u[33];   /* pH */
     S_H_ion = *u[34]; /* SH+ */
    
   /* STRs function
   if (pH_op < pH_UL_aa)
    I_pH_aa = exp(-3.0*(pH_op-pH_UL_aa)*(pH_op-pH_UL_aa)/((pH_UL_aa-pH_LL_aa)*(pH_UL_aa-pH_LL_aa)));
   else
    I_pH_aa = 1.0;
   if (pH_op < pH_UL_h2)
    I_pH_h2 = exp(-3.0*(pH_op-pH_UL_h2)*(pH_op-pH_UL_h2)/((pH_UL_h2-pH_LL_h2)*(pH_UL_h2-pH_LL_h2)));
   else
    I_pH_h2 = 1.0;
   */
   
   /* Hill function on pH inhibition
   pHLim_aa = (pH_UL_aa + pH_LL_aa)/2.0;
   pHLim_ac = (pH_UL_ac + pH_LL_ac)/2.0;
   pHLim_h2 = (pH_UL_h2 + pH_LL_h2)/2.0;
   I_pH_aa = pow(pH_op,24)/(pow(pH_op,24)+pow(pHLim_aa ,24));
   I_pH_ac = pow(pH_op,45)/(pow(pH_op,45)+pow(pHLim_ac ,45));
   I_pH_h2 = pow(pH_op,45)/(pow(pH_op,45)+pow(pHLim_h2 ,45));
   */

   /* MNPs function on pH inhibition, ADM1 Workshop, Copenhagen 2005.
   a_aa = 25.0/(pH_UL_aa-pH_LL_aa+eps);
   a_ac = 25.0/(pH_UL_ac-pH_LL_ac+eps);
   a_h2 = 25.0/(pH_UL_h2-pH_LL_h2+eps);

   I_pH_aa = 0.5*(1+tanh(a_aa*(pH_op/pHLim_aa - 1.0)));
   I_pH_ac = 0.5*(1+tanh(a_ac*(pH_op/pHLim_ac - 1.0)));
   I_pH_h2 = 0.5*(1+tanh(a_h2*(pH_op/pHLim_h2 - 1.0)));
   */

   /* Hill function on SH+ used within BSM2, ADM1 Workshop, Copenhagen 2005. */
   pHLim_aa = pow(10,(-(pH_UL_aa + pH_LL_aa)/2.0));
   pHLim_h2 = pow(10,(-(pH_UL_h2 + pH_LL_h2)/2.0));
   n_aa=3.0/(pH_UL_aa-pH_LL_aa);
   n_h2=3.0/(pH_UL_h2-pH_LL_h2);
   I_pH_aa = pow(pHLim_aa,n_aa)/(pow(S_H_ion,n_aa)+pow(pHLim_aa ,n_aa));
   I_pH_h2 = pow(pHLim_h2,n_h2)/(pow(S_H_ion,n_h2)+pow(pHLim_h2 ,n_h2));
     
    /* Gradient of Sh2 equation */
    return -1/V_liq**u[26]
            -3.0/10.0*(1-Y_fa)*k_m_fa**u[2]/(K_S_fa+*u[2])**u[18]*I_pH_aa/(1+K_S_IN/(*u[10]))/((1+x[0]/K_Ih2_fa)*(1+x[0]/K_Ih2_fa))/K_Ih2_fa
            -3.0/20.0*(1-Y_c4)*k_m_c4**u[3]**u[3]/(K_S_c4+*u[3])**u[19]/(*u[4]+*u[3]+eps)*I_pH_aa/(1+K_S_IN/(*u[10]))/((1+x[0]/K_Ih2_c4)*(1+x[0]/K_Ih2_c4))/K_Ih2_c4
            -1.0/5.0*(1-Y_c4)*k_m_c4**u[4]**u[4]/(K_S_c4+*u[4])**u[19]/(*u[4]+*u[3]+eps)*I_pH_aa/(1+K_S_IN/(*u[10]))/((1+x[0]/K_Ih2_c4)*(1+x[0]/K_Ih2_c4))/K_Ih2_c4
            -43.0/100.0*(1-Y_pro)*k_m_pro**u[5]/(K_S_pro+*u[5])**u[20]*I_pH_aa/(1+K_S_IN/(*u[10]))/((1+x[0]/K_Ih2_pro)*(1+x[0]/K_Ih2_pro))/K_Ih2_pro
            -k_m_h2/(K_S_h2+x[0])**u[22]*I_pH_h2/(1+K_S_IN/(*u[10]))+k_m_h2*x[0]/((K_S_h2+x[0])*(K_S_h2+x[0]))**u[22]*I_pH_h2/(1+K_S_IN/(*u[10]))
            -kLa;          
}
    
    
static void Sh2solver(SimStruct *S)
{

    real_T *x = ssGetDiscStates(S);
        
    static real_T delta;
    static real_T Sh20;
    static int_T i;
    
    static const real_T TOL = 1e-12;
    static const real_T MaxSteps= 1000;
    
    Sh20 = x[0]; /* Sh2 */
    
    i = 1; 
    delta = 1.0;
    
    /* Newton-Raphson algorithm */
    
    while ( (delta > TOL || delta < -TOL) && (i <= MaxSteps) ) {
        delta = Equ(S);
        x[0] = Sh20-delta/gradEqu(S);     /* Calculate the new Sh2 */ 
        
        if (x[0] <= 0) {
            x[0] = 1e-12; /* to avoid numerical problems */
        }
        
        Sh20 = x[0];
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
   Sh2solver(S);  
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
