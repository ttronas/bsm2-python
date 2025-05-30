/*
 * The adm1_DAE2.c is a C-file S-function level 2 for a fully speed-enhanced IAWQ AD Model No 1.
 * In this the model derivatives of ion states anf hydrogen gas are set to zero.
 * Instead they are calculated using algebraic equations and a pH solver
 * using the Newton-Raphson method nd an equivalent H2-solver). This way the main stiffness is removed.
 * In addition to the ADM1, temperature dependency and dummy states are added.
 * Some details are adjusted for BSM2 (pH inhibition, gas flow output etc).
 *
 * Copyright (2006):
 * Dr Christian Rosen, Dr Darko Vrecko and Dr Ulf Jeppsson
 * Dept. Industrial Electrical Engineering and Automation (IEA)
 * Lund University, Sweden
 * http://www.iea.lth.se/
*/


#define S_FUNCTION_NAME  adm1_DAE2_bsm2
#define S_FUNCTION_LEVEL 2

#include "simstruc.h"
#include <math.h>

/* Input Parameters */
#define XINIT(S)  ssGetSFcnParam(S,0)
#define PAR(S)	  ssGetSFcnParam(S,1)
#define V(S)      ssGetSFcnParam(S,2)


/*
 * mdlInitializeSizes:
 *    The sizes information is used by Simulink to determine the S-function
 *    block's characteristics (number of inputs, outputs, states, etc.).
 */
static void mdlInitializeSizes(SimStruct *S)
{
    ssSetNumSFcnParams(S, 3);  /* Number of expected parameters */
    if (ssGetNumSFcnParams(S) != ssGetSFcnParamsCount(S)) {
        return;  /* Return if number of expected != number of actual parameters */
    }

    ssSetNumContStates(S, 42);
    ssSetNumDiscStates(S, 0);

    if (!ssSetNumInputPorts(S, 1)) return;
    ssSetInputPortWidth(S, 0, 41); /*(S, port index, port width) */

    ssSetInputPortDirectFeedThrough(S, 0, 1);

    if (!ssSetNumOutputPorts(S, 1)) return;
    ssSetOutputPortWidth(S, 0, 52);

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


#define MDL_INITIALIZE_CONDITIONS   /* Change to #undef to remove function */
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

  real_T *x0 = ssGetContStates(S);
  int_T i;

  for (i = 0; i < 42; i++) {
      x0[i] = mxGetPr(XINIT(S))[i];
  }
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
  real_T *x = ssGetContStates(S);
  real_T *y = ssGetOutputPortRealSignal(S,0);
  InputRealPtrsType u = ssGetInputPortRealSignalPtrs(S,0);

  real_T R, T_op, T_base, P_atm, p_gas_h2o, P_gas, k_P, q_gas, V_liq, procT8, procT9, procT10, p_gas_h2, p_gas_ch4, p_gas_co2, kLa, K_H_h2o_base, K_H_h2, K_H_h2_base, K_H_ch4, K_H_ch4_base, K_H_co2, K_H_co2_base, K_w, pK_w_base, factor;
  int_T i;

  R = mxGetPr(PAR(S))[77];
  T_base = mxGetPr(PAR(S))[78];
  T_op = mxGetPr(PAR(S))[79];
  P_atm = mxGetPr(PAR(S))[93];
  V_liq = mxGetPr(V(S))[0];
  kLa = mxGetPr(PAR(S))[94];
  K_H_h2_base = mxGetPr(PAR(S))[98];
  K_H_ch4_base = mxGetPr(PAR(S))[97];
  K_H_co2_base = mxGetPr(PAR(S))[96];
  K_H_h2o_base = mxGetPr(PAR(S))[95];
  pK_w_base = mxGetPr(PAR(S))[80];
  k_P = mxGetPr(PAR(S))[99];

  factor = (1.0/T_base - 1.0/T_op)/(100.0*R);
  K_H_h2 = K_H_h2_base*exp(-4180.0*factor);     /* T adjustment for K_H_h2 */
  K_H_ch4 = K_H_ch4_base*exp(-14240.0*factor);  /* T adjustment for K_H_ch4 */
  K_H_co2 = K_H_co2_base*exp(-19410.0*factor);  /* T adjustment for K_H_co2 */
  K_w = pow(10,-pK_w_base)*exp(55900.0*factor); /* T adjustment for K_w */
  p_gas_h2o = K_H_h2o_base*exp(5290.0*(1.0/T_base - 1.0/T_op));  /* T adjustement for water vapour saturation pressure */

  for (i = 0; i < 7; i++) {
      y[i] = x[i];
  }

  y[7] = *u[40];   /* Sh2 */

  for (i = 0; i < 18; i++) {
      y[i+8] = x[i+8];
  }

  y[26] = *u[26];   /* flow */

  y[27] = T_op - 273.15;      /* Temp = 35 degC */

  y[28] = *u[28];   /* Dummy state 1, soluble */
  y[29] = *u[29];   /* Dummy state 2, soluble */
  y[30] = *u[30];   /* Dummy state 3, soluble */
  y[31] = *u[31];   /* Dummy state 1, particulate */
  y[32] = *u[32];   /* Dummy state 2, particulate */

  p_gas_h2 = x[32]*R*T_op/16.0;
  p_gas_ch4 = x[33]*R*T_op/64.0;
  p_gas_co2 = x[34]*R*T_op;
  P_gas = p_gas_h2 + p_gas_ch4 + p_gas_co2 + p_gas_h2o;

  q_gas = k_P*(P_gas - P_atm);
  if (q_gas < 0)
    q_gas = 0.0;

  procT8 = kLa*(*u[40]-16.0*K_H_h2*p_gas_h2);
  procT9 = kLa*(x[8]-64.0*K_H_ch4*p_gas_ch4);
  procT10 = kLa*((x[9]-*u[38])-K_H_co2*p_gas_co2);

  y[33] = -log10(*u[33]);    /* pH */
  y[34] = *u[33];            /* SH+ */
  y[35] = *u[34];  /* Sva- */
  y[36] = *u[35];  /* Sbu- */
  y[37] = *u[36];  /* Spro- */
  y[38] = *u[37];  /* Sac- */
  y[39] = *u[38];  /* SHCO3- */
  y[40] = x[9] - *u[38];        /* SCO2 */
  y[41] = *u[39];  /* SNH3 */
  y[42] = x[10] - *u[39];       /* SNH4+ */
  y[43] = x[32];               /* Sgas,h2 */
  y[44] = x[33];               /* Sgas,ch4 */
  y[45] = x[34];               /* Sgas,co2 */
  y[46] = p_gas_h2;
  y[47] = p_gas_ch4;
  y[48] = p_gas_co2;
  y[49] = P_gas;                /* total head space pressure from H2, CH4, CO2 and H2O */
  y[50] = q_gas * P_gas/P_atm; /* The output gas flow is recalculated to atmospheric pressure (normalization) */
  y[51] = *u[7]; /* S_h2_in */
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


#define MDL_DERIVATIVES  /* Change to #undef to remove function */
#if defined(MDL_DERIVATIVES)
  /*
   * mdlDerivatives:
   *    In this function, you compute the S-function block's derivatives.
   *    The derivatives are placed in the derivative vector, ssGetdX(S).
   */
  static void mdlDerivatives(SimStruct *S)
  {
   real_T *dx   = ssGetdX(S);
   real_T *x = ssGetContStates(S);
   InputRealPtrsType u = ssGetInputPortRealSignalPtrs(S,0);

   real_T f_sI_xc, f_xI_xc, f_ch_xc, f_pr_xc, f_li_xc, N_xc, N_I, N_aa, C_xc, C_sI, C_ch;
   real_T C_pr, C_li, C_xI, C_su, C_aa, f_fa_li, C_fa, f_h2_su, f_bu_su, f_pro_su, f_ac_su;
   real_T N_bac, C_bu, C_pro, C_ac, C_bac, Y_su, f_h2_aa, f_va_aa, f_bu_aa, f_pro_aa, f_ac_aa;
   real_T C_va, Y_aa, Y_fa, Y_c4, Y_pro, C_ch4, Y_ac, Y_h2;
   real_T k_dis, k_hyd_ch, k_hyd_pr, k_hyd_li, K_S_IN, k_m_su, K_S_su, pH_UL_aa, pH_LL_aa;
   real_T k_m_aa, K_S_aa, k_m_fa, K_S_fa, K_Ih2_fa, k_m_c4, K_S_c4, K_Ih2_c4, k_m_pro, K_S_pro;
   real_T K_Ih2_pro, k_m_ac, K_S_ac, K_I_nh3, pH_UL_ac, pH_LL_ac, k_m_h2, K_S_h2, pH_UL_h2, pH_LL_h2;
   real_T k_dec_Xsu, k_dec_Xaa, k_dec_Xfa, k_dec_Xc4, k_dec_Xpro, k_dec_Xac, k_dec_Xh2;
   real_T R, T_base, T_op;
   real_T K_H_h2o_base, K_H_co2_base, K_H_ch4_base, K_H_h2_base, factor;
   real_T P_atm, p_gas_h2o, P_gas, k_P, kLa, K_H_co2, K_H_ch4, K_H_h2;
   real_T V_liq, V_gas;
   real_T eps, pH_op, S_H_ion;
   real_T proc1, proc2, proc3, proc4, proc5, proc6, proc7, proc8, proc9, proc10, proc11, proc12, proc13;
   real_T proc14, proc15, proc16, proc17, proc18, proc19;
   real_T procT8, procT9, procT10;
   real_T I_pH_aa, I_pH_ac, I_pH_h2, I_IN_lim, I_h2_fa, I_h2_c4, I_h2_pro, I_nh3;
   real_T reac1, reac2, reac3, reac4, reac5, reac6, reac7, reac8, reac9, reac10, reac11, reac12, reac13;
   real_T reac14, reac15, reac16, reac17, reac18, reac19, reac20, reac21, reac22, reac23, reac24;
   real_T stoich1, stoich2, stoich3, stoich4, stoich5, stoich6, stoich7, stoich8, stoich9, stoich10, stoich11, stoich12, stoich13;
   real_T xtemp[42], inhib[6];
   real_T p_gas_h2, p_gas_ch4, p_gas_co2, q_gas;
   real_T pHLim_aa, pHLim_ac, pHLim_h2, a_aa, a_ac, a_h2, n_aa, n_ac, n_h2;
   int_T i;

   eps = 0.000001;

   f_sI_xc = mxGetPr(PAR(S))[0];
   f_xI_xc = mxGetPr(PAR(S))[1];
   f_ch_xc = mxGetPr(PAR(S))[2];
   f_pr_xc = mxGetPr(PAR(S))[3];
   f_li_xc = mxGetPr(PAR(S))[4];
   N_xc = mxGetPr(PAR(S))[5];
   N_I = mxGetPr(PAR(S))[6];
   N_aa = mxGetPr(PAR(S))[7];
   C_xc = mxGetPr(PAR(S))[8];
   C_sI = mxGetPr(PAR(S))[9];
   C_ch = mxGetPr(PAR(S))[10];
   C_pr = mxGetPr(PAR(S))[11];
   C_li = mxGetPr(PAR(S))[12];
   C_xI = mxGetPr(PAR(S))[13];
   C_su = mxGetPr(PAR(S))[14];
   C_aa = mxGetPr(PAR(S))[15];
   f_fa_li = mxGetPr(PAR(S))[16];
   C_fa = mxGetPr(PAR(S))[17];
   f_h2_su = mxGetPr(PAR(S))[18];
   f_bu_su = mxGetPr(PAR(S))[19];
   f_pro_su = mxGetPr(PAR(S))[20];
   f_ac_su = mxGetPr(PAR(S))[21];
   N_bac = mxGetPr(PAR(S))[22];
   C_bu = mxGetPr(PAR(S))[23];
   C_pro = mxGetPr(PAR(S))[24];
   C_ac = mxGetPr(PAR(S))[25];
   C_bac = mxGetPr(PAR(S))[26];
   Y_su = mxGetPr(PAR(S))[27];
   f_h2_aa = mxGetPr(PAR(S))[28];
   f_va_aa = mxGetPr(PAR(S))[29];
   f_bu_aa = mxGetPr(PAR(S))[30];
   f_pro_aa = mxGetPr(PAR(S))[31];
   f_ac_aa = mxGetPr(PAR(S))[32];
   C_va = mxGetPr(PAR(S))[33];
   Y_aa = mxGetPr(PAR(S))[34];
   Y_fa = mxGetPr(PAR(S))[35];
   Y_c4 = mxGetPr(PAR(S))[36];
   Y_pro = mxGetPr(PAR(S))[37];
   C_ch4 = mxGetPr(PAR(S))[38];
   Y_ac = mxGetPr(PAR(S))[39];
   Y_h2 = mxGetPr(PAR(S))[40];
   k_dis = mxGetPr(PAR(S))[41];
   k_hyd_ch = mxGetPr(PAR(S))[42];
   k_hyd_pr = mxGetPr(PAR(S))[43];
   k_hyd_li = mxGetPr(PAR(S))[44];
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
   k_m_ac = mxGetPr(PAR(S))[61];
   K_S_ac = mxGetPr(PAR(S))[62];
   K_I_nh3 = mxGetPr(PAR(S))[63];
   pH_UL_ac = mxGetPr(PAR(S))[64];
   pH_LL_ac = mxGetPr(PAR(S))[65];
   k_m_h2 = mxGetPr(PAR(S))[66];
   K_S_h2 = mxGetPr(PAR(S))[67];
   pH_UL_h2 = mxGetPr(PAR(S))[68];
   pH_LL_h2 = mxGetPr(PAR(S))[69];
   k_dec_Xsu = mxGetPr(PAR(S))[70];
   k_dec_Xaa = mxGetPr(PAR(S))[71];
   k_dec_Xfa = mxGetPr(PAR(S))[72];
   k_dec_Xc4 = mxGetPr(PAR(S))[73];
   k_dec_Xpro = mxGetPr(PAR(S))[74];
   k_dec_Xac = mxGetPr(PAR(S))[75];
   k_dec_Xh2 = mxGetPr(PAR(S))[76];
   R = mxGetPr(PAR(S))[77];
   T_base = mxGetPr(PAR(S))[78];
   T_op = mxGetPr(PAR(S))[79];
   P_atm = mxGetPr(PAR(S))[93];
   kLa = mxGetPr(PAR(S))[94];
   K_H_h2o_base = mxGetPr(PAR(S))[95];
   K_H_co2_base = mxGetPr(PAR(S))[96];
   K_H_ch4_base = mxGetPr(PAR(S))[97];
   K_H_h2_base = mxGetPr(PAR(S))[98];
   k_P = mxGetPr(PAR(S))[99];

   V_liq = mxGetPr(V(S))[0];
   V_gas = mxGetPr(V(S))[1];

   for (i = 0; i < 42; i++) {
       if (x[i] < 0)
           xtemp[i] = 0;
       else
           xtemp[i] = x[i];
   }

   factor = (1.0/T_base - 1.0/T_op)/(100.0*R);
   K_H_h2 = K_H_h2_base*exp(-4180.0*factor);     /* T adjustment for K_H_h2 */
   K_H_ch4 = K_H_ch4_base*exp(-14240.0*factor);  /* T adjustment for K_H_ch4 */
   K_H_co2 = K_H_co2_base*exp(-19410.0*factor);  /* T adjustment for K_H_co2 */

   p_gas_h2 = x[32]*R*T_op/16.0;
   p_gas_ch4 = x[33]*R*T_op/64.0;
   p_gas_co2 = x[34]*R*T_op;
   p_gas_h2o = K_H_h2o_base*exp(5290.0*(1.0/T_base - 1.0/T_op));  /* T adjustement for water vapour saturation pressure */
   P_gas = p_gas_h2 + p_gas_ch4 + p_gas_co2 + p_gas_h2o;

   S_H_ion = *u[33];
   pH_op = -log10(*u[33]);   /* pH */

/* STRs function
if (pH_op < pH_UL_aa)
   I_pH_aa = exp(-3.0*(pH_op-pH_UL_aa)*(pH_op-pH_UL_aa)/((pH_UL_aa-pH_LL_aa)*(pH_UL_aa-pH_LL_aa)));
else
   I_pH_aa = 1.0;
if (pH_op < pH_UL_ac)
   I_pH_ac = exp(-3.0*(pH_op-pH_UL_ac)*(pH_op-pH_UL_ac)/((pH_UL_ac-pH_LL_ac)*(pH_UL_ac-pH_LL_ac)));
else
   I_pH_ac = 1.0;
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
   pHLim_ac = pow(10,(-(pH_UL_ac + pH_LL_ac)/2.0));
   pHLim_h2 = pow(10,(-(pH_UL_h2 + pH_LL_h2)/2.0));
   n_aa=3.0/(pH_UL_aa-pH_LL_aa);
   n_ac=3.0/(pH_UL_ac-pH_LL_ac);
   n_h2=3.0/(pH_UL_h2-pH_LL_h2);
   I_pH_aa = pow(pHLim_aa,n_aa)/(pow(S_H_ion,n_aa)+pow(pHLim_aa ,n_aa));
   I_pH_ac = pow(pHLim_ac,n_ac)/(pow(S_H_ion,n_ac)+pow(pHLim_ac ,n_ac));
   I_pH_h2 = pow(pHLim_h2,n_h2)/(pow(S_H_ion,n_h2)+pow(pHLim_h2 ,n_h2));

   I_IN_lim = 1.0/(1.0+K_S_IN/xtemp[10]);
   I_h2_fa = 1.0/(1.0+*u[40]/K_Ih2_fa);
   I_h2_c4 = 1.0/(1.0+*u[40]/K_Ih2_c4);
   I_h2_pro = 1.0/(1.0+*u[40]/K_Ih2_pro);
   I_nh3 = 1.0/(1.0+*u[39]/K_I_nh3);

   inhib[0] = I_pH_aa*I_IN_lim;
   inhib[1] = inhib[0]*I_h2_fa;
   inhib[2] = inhib[0]*I_h2_c4;
   inhib[3] = inhib[0]*I_h2_pro;
   inhib[4] = I_pH_ac*I_IN_lim*I_nh3;
   inhib[5] = I_pH_h2*I_IN_lim;

   proc1 = k_dis*xtemp[12];
   proc2 = k_hyd_ch*xtemp[13];
   proc3 = k_hyd_pr*xtemp[14];
   proc4 = k_hyd_li*xtemp[15];
   proc5 = k_m_su*xtemp[0]/(K_S_su+xtemp[0])*xtemp[16]*inhib[0];
   proc6 = k_m_aa*xtemp[1]/(K_S_aa+xtemp[1])*xtemp[17]*inhib[0];
   proc7 = k_m_fa*xtemp[2]/(K_S_fa+xtemp[2])*xtemp[18]*inhib[1];
   proc8 = k_m_c4*xtemp[3]/(K_S_c4+xtemp[3])*xtemp[19]*xtemp[3]/(xtemp[3]+xtemp[4]+eps)*inhib[2];
   proc9 = k_m_c4*xtemp[4]/(K_S_c4+xtemp[4])*xtemp[19]*xtemp[4]/(xtemp[3]+xtemp[4]+eps)*inhib[2];
   proc10 = k_m_pro*xtemp[5]/(K_S_pro+xtemp[5])*xtemp[20]*inhib[3];
   proc11 = k_m_ac*xtemp[6]/(K_S_ac+xtemp[6])*xtemp[21]*inhib[4];
   proc12 = k_m_h2**u[40]/(K_S_h2+*u[40])*xtemp[22]*inhib[5];
   proc13 = k_dec_Xsu*xtemp[16];
   proc14 = k_dec_Xaa*xtemp[17];
   proc15 = k_dec_Xfa*xtemp[18];
   proc16 = k_dec_Xc4*xtemp[19];
   proc17 = k_dec_Xpro*xtemp[20];
   proc18 = k_dec_Xac*xtemp[21];
   proc19 = k_dec_Xh2*xtemp[22];

   procT8 = kLa*(*u[40]-16.0*K_H_h2*p_gas_h2);
   procT9 = kLa*(xtemp[8]-64.0*K_H_ch4*p_gas_ch4);
   procT10 = kLa*((xtemp[9]-*u[38])-K_H_co2*p_gas_co2);

   stoich1 = -C_xc+f_sI_xc*C_sI+f_ch_xc*C_ch+f_pr_xc*C_pr+f_li_xc*C_li+f_xI_xc*C_xI;
   stoich2 = -C_ch+C_su;
   stoich3 = -C_pr+C_aa;
   stoich4 = -C_li+(1.0-f_fa_li)*C_su+f_fa_li*C_fa;
   stoich5 = -C_su+(1.0-Y_su)*(f_bu_su*C_bu+f_pro_su*C_pro+f_ac_su*C_ac)+Y_su*C_bac;
   stoich6 = -C_aa+(1.0-Y_aa)*(f_va_aa*C_va+f_bu_aa*C_bu+f_pro_aa*C_pro+f_ac_aa*C_ac)+Y_aa*C_bac;
   stoich7 = -C_fa+(1.0-Y_fa)*0.7*C_ac+Y_fa*C_bac;
   stoich8 = -C_va+(1.0-Y_c4)*0.54*C_pro+(1.0-Y_c4)*0.31*C_ac+Y_c4*C_bac;
   stoich9 = -C_bu+(1.0-Y_c4)*0.8*C_ac+Y_c4*C_bac;
   stoich10 = -C_pro+(1.0-Y_pro)*0.57*C_ac+Y_pro*C_bac;
   stoich11 = -C_ac+(1.0-Y_ac)*C_ch4+Y_ac*C_bac;
   stoich12 = (1.0-Y_h2)*C_ch4+Y_h2*C_bac;
   stoich13 = -C_bac+C_xc;

   reac1 = proc2+(1.0-f_fa_li)*proc4-proc5;
   reac2 = proc3-proc6;
   reac3 = f_fa_li*proc4-proc7;
   reac4 = (1.0-Y_aa)*f_va_aa*proc6-proc8;
   reac5 = (1.0-Y_su)*f_bu_su*proc5+(1.0-Y_aa)*f_bu_aa*proc6-proc9;
   reac6 = (1.0-Y_su)*f_pro_su*proc5+(1.0-Y_aa)*f_pro_aa*proc6+(1.0-Y_c4)*0.54*proc8-proc10;
   reac7 = (1.0-Y_su)*f_ac_su*proc5+(1.0-Y_aa)*f_ac_aa*proc6+(1.0-Y_fa)*0.7*proc7+(1.0-Y_c4)*0.31*proc8+(1.0-Y_c4)*0.8*proc9+(1.0-Y_pro)*0.57*proc10-proc11;
   reac8 = (1.0-Y_su)*f_h2_su*proc5+(1.0-Y_aa)*f_h2_aa*proc6+(1.0-Y_fa)*0.3*proc7+(1.0-Y_c4)*0.15*proc8+(1.0-Y_c4)*0.2*proc9+(1.0-Y_pro)*0.43*proc10-proc12-procT8;
   reac9 = (1.0-Y_ac)*proc11+(1.0-Y_h2)*proc12-procT9;
   reac10 = -stoich1*proc1-stoich2*proc2-stoich3*proc3-stoich4*proc4-stoich5*proc5-stoich6*proc6-stoich7*proc7-stoich8*proc8-stoich9*proc9-stoich10*proc10-stoich11*proc11-stoich12*proc12-stoich13*proc13-stoich13*proc14-stoich13*proc15-stoich13*proc16-stoich13*proc17-stoich13*proc18-stoich13*proc19-procT10;
   reac11 = (N_xc-f_xI_xc*N_I-f_sI_xc*N_I-f_pr_xc*N_aa)*proc1-Y_su*N_bac*proc5+(N_aa-Y_aa*N_bac)*proc6-Y_fa*N_bac*proc7-Y_c4*N_bac*proc8-Y_c4*N_bac*proc9-Y_pro*N_bac*proc10-Y_ac*N_bac*proc11-Y_h2*N_bac*proc12+(N_bac-N_xc)*(proc13+proc14+proc15+proc16+proc17+proc18+proc19);
   reac12 = f_sI_xc*proc1;
   reac13 = -proc1+proc13+proc14+proc15+proc16+proc17+proc18+proc19;
   reac14 = f_ch_xc*proc1-proc2;
   reac15 = f_pr_xc*proc1-proc3;
   reac16 = f_li_xc*proc1-proc4;
   reac17 = Y_su*proc5-proc13;
   reac18 = Y_aa*proc6-proc14;
   reac19 = Y_fa*proc7-proc15;
   reac20 = Y_c4*proc8+Y_c4*proc9-proc16;
   reac21 = Y_pro*proc10-proc17;
   reac22 = Y_ac*proc11-proc18;
   reac23 = Y_h2*proc12-proc19;
   reac24 = f_xI_xc*proc1;

   q_gas = k_P*(P_gas-P_atm);
   if (q_gas < 0)
       q_gas = 0.0;

   dx[0] = 1.0/V_liq*(*u[26]*(*u[0]-x[0]))+reac1;
   dx[1] = 1.0/V_liq*(*u[26]*(*u[1]-x[1]))+reac2;
   dx[2] = 1.0/V_liq*(*u[26]*(*u[2]-x[2]))+reac3;
   dx[3] = 1.0/V_liq*(*u[26]*(*u[3]-x[3]))+reac4;  /* Sva */
   dx[4] = 1.0/V_liq*(*u[26]*(*u[4]-x[4]))+reac5;  /* Sbu */
   dx[5] = 1.0/V_liq*(*u[26]*(*u[5]-x[5]))+reac6;  /* Spro */
   dx[6] = 1.0/V_liq*(*u[26]*(*u[6]-x[6]))+reac7;  /* Sac */
   dx[7] = 0;  /* calculated in Sh2solv.c */
   dx[8] = 1.0/V_liq*(*u[26]*(*u[8]-x[8]))+reac9;     /* Sch4 */
   dx[9] = 1.0/V_liq*(*u[26]*(*u[9]-x[9]))+reac10;    /* SIC */
   dx[10] = 1.0/V_liq*(*u[26]*(*u[10]-x[10]))+reac11; /* SIN */
   dx[11] = 1.0/V_liq*(*u[26]*(*u[11]-x[11]))+reac12;
   dx[12] = 1.0/V_liq*(*u[26]*(*u[12]-x[12]))+reac13;
   dx[13] = 1.0/V_liq*(*u[26]*(*u[13]-x[13]))+reac14;
   dx[14] = 1.0/V_liq*(*u[26]*(*u[14]-x[14]))+reac15;
   dx[15] = 1.0/V_liq*(*u[26]*(*u[15]-x[15]))+reac16;
   dx[16] = 1.0/V_liq*(*u[26]*(*u[16]-x[16]))+reac17;
   dx[17] = 1.0/V_liq*(*u[26]*(*u[17]-x[17]))+reac18;
   dx[18] = 1.0/V_liq*(*u[26]*(*u[18]-x[18]))+reac19;
   dx[19] = 1.0/V_liq*(*u[26]*(*u[19]-x[19]))+reac20;
   dx[20] = 1.0/V_liq*(*u[26]*(*u[20]-x[20]))+reac21;
   dx[21] = 1.0/V_liq*(*u[26]*(*u[21]-x[21]))+reac22;
   dx[22] = 1.0/V_liq*(*u[26]*(*u[22]-x[22]))+reac23;
   dx[23] = 1.0/V_liq*(*u[26]*(*u[23]-x[23]))+reac24;

   dx[24] = 1.0/V_liq*(*u[26]*(*u[24]-x[24])); /* Scat+ */
   dx[25] = 1.0/V_liq*(*u[26]*(*u[25]-x[25])); /* San- */

   /* calculated in pHsolv.c */
   dx[26] = 0;  /* Sva- */
   dx[27] = 0;  /* Sbu- */
   dx[28] = 0;  /* Spro- */
   dx[29] = 0;  /* Sac- */
   dx[30] = 0;  /* SHCO3- */
   dx[31] = 0;  /* SNH3 */

   dx[32] = -xtemp[32]*q_gas/V_gas + procT8*V_liq/V_gas;
   dx[33] = -xtemp[33]*q_gas/V_gas + procT9*V_liq/V_gas;
   dx[34] = -xtemp[34]*q_gas/V_gas + procT10*V_liq/V_gas;

   dx[35] = 0; /* Flow */

   dx[36] = 0; /* Temp */

   /* Dummy states*/
   dx[37] = 0;
   dx[38] = 0;
   dx[39] = 0;
   dx[40] = 0;
   dx[41] = 0;
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
