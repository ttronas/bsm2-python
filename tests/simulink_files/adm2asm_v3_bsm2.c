/*
 * New version (no 3) of the ADM1 to ASM1 interface based on discussions
 * within the IWA TG BSM community during 2002-2006. Now also including charge
 * balancing and temperature dependency for applicable parameters.
 * Model parameters are defined in adm1init_bsm2.m
 * u is the input in ADM1 terminology + extra dummy states, 33 variables
 * plus two extra inputs: 1) dynamic pH from the ADM1 system (needed for
 * accurate charge balancing - also used the ASM1 to ADM1 interface) and
 * 2) wastewater temperature into the ASM2ADM interface, which is used as
 * the output temperature from the ADM2ASM interface (assume heat exchangers etc).
 * If temperature control of AD is used then the operational temperature
 * of the ADM1 should also be an input rather than a defined parameter.
 * Temperature in the ADM1 and the ASM1 to ADM1 and the ADM1 to ASM1
 * interfaces should be identical at every time instant.
 * The interface assumes identical N-content of particulate inerts in both
 * AD and AS. The same holds for biomass. The N-content of soluble inerts may vary.
 *
 * u is the input in ADM1 terminology + extra dummy states, 33 variables
 * u[0] : Ssu = monosacharides (kg COD/m3)
 * u[1] : Saa = amino acids (kg COD/m3)
 * u[2] : Sfa = long chain fatty acids (LCFA) (kg COD/m3)
 * u[3] : Sva = total valerate (kg COD/m3)
 * u[4] : Sbu = total butyrate (kg COD/m3)
 * u[5] : Spro = total propionate (kg COD/m3)
 * u[6] : Sac = total acetate (kg COD/m3)
 * u[7] : Sh2 = hydrogen gas (kg COD/m3)
 * u[8] : Sch4 = methane gas (kg COD/m3)
 * u[9] : Sic = inorganic carbon (kmole C/m3)
 * u[10] : Sin = inorganic nitrogen (kmole N/m3)
 * u[11] : Si = soluble inerts (kg COD/m3)
 * u[12] : Xc = composites (kg COD/m3)
 * u[13] : Xch = carbohydrates (kg COD/m3)
 * u[14] : Xpr = proteins (kg COD/m3)
 * u[15] : Xli = lipids (kg COD/m3)
 * u[16] : Xsu = sugar degraders (kg COD/m3)
 * u[17] : Xaa = amino acid degraders (kg COD/m3)
 * u[18] : Xfa = LCFA degraders (kg COD/m3)
 * u[19] : Xc4 = valerate and butyrate degraders (kg COD/m3)
 * u[20] : Xpro = propionate degraders (kg COD/m3)
 * u[21] : Xac = acetate degraders (kg COD/m3)
 * u[22] : Xh2 = hydrogen degraders (kg COD/m3)
 * u[23] : Xi = particulate inerts (kg COD/m3)
 * u[24] : scat+ = cations (metallic ions, strong base) (kmole/m3)
 * u[25] : san- = anions (metallic ions, strong acid) (kmole/m3)
 * u[26] : flow rate (m3/d)
 * u[27] : temperature (deg C)
 * u[28:32] : dummy states for future use
 * u[33] : dynamic pH from the ADM1
 * u[34] : wastewater temperature into the ASM2ADM interface, deg C
 *
 * Output vector:
 * y[0] : Si = soluble inert organic material (g COD/m3)
 * y[1] : Ss = readily biodegradable substrate (g COD/m3)
 * y[2] : Xi = particulate inert organic material (g COD/m3)
 * y[3] : Xs = slowly biodegradable substrate (g COD/m3)
 * y[4] : Xbh = active heterotrophic biomass (g COD/m3)
 * y[5] : Xba = active autotrophic biomass (g COD/m3)
 * y[6] : Xp = particulate product arising from biomass decay (g COD/m3)
 * y[7] : So = oxygen (g -COD/m3)
 * y[8] : Sno = nitrate and nitrite nitrogen (g N/m3)
 * y[9] : Snh = ammonia and ammonium nitrogen (g N/m3)
 * y[10] : Snd = soluble biogradable organic nitrogen (g N/m3)
 * y[11] : Xnd = particulate biogradable organic nitrogen (g N/m3)
 * y[12] : Salk = alkalinity (mole HCO3-/m3)
 * y[13] : TSS = total suspended solids (internal use) (mg SS/l)
 * y[14] : flow rate (m3/d)
 * y[15] : temperature (deg C)
 * y[16:20] : dummy states for future use
 *
 * ADM1 --> ASM1 conversion, version 3 for BSM2
 * Copyright: John Copp, Primodal Inc., Canada; Ulf Jeppsson, Lund
 *            University, Sweden; Damien Batstone, Univ of Queensland,
 *            Australia, Ingmar Nopens, Univ of Ghent, Belgium,
 *            Marie-Noelle Pons, Nancy, France, Peter Vanrolleghem,
 *            Univ. Laval, Canada, Jens Alex, IFAK, Germany and
 *            Eveline Volcke, Univ of Ghent, Belgium.
 */

#define S_FUNCTION_NAME adm2asm_v3_bsm2

#include "simstruc.h"
#include <math.h>

#define PAR  	ssGetArg(S,0)

/*
 * mdlInitializeSizes - initialize the sizes array
 */
static void mdlInitializeSizes(SimStruct *S)
{
    ssSetNumContStates(    S, 0);   /* number of continuous states           */
    ssSetNumDiscStates(    S, 0);   /* number of discrete states             */
    ssSetNumInputs(        S, 35);  /* number of inputs                      */
    ssSetNumOutputs(       S, 21);  /* number of outputs                     */
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
	double 	CODequiv, fnaa, fnxc, fnbac, fxni, fsni, fsni_adm, frlixs, frlibac, frxs_adm, fdegrade_adm, frxs_as, fdegrade_as;
    double  R, T_base, T_op, pK_w_base, pK_a_va_base, pK_a_bu_base, pK_a_pro_base, pK_a_ac_base, pK_a_co2_base, pK_a_IN_base;
    double  pH_adm, pK_w, pK_a_co2, pK_a_IN, alfa_va, alfa_bu, alfa_pro, alfa_ac, alfa_co2, alfa_IN, alfa_NH, alfa_alk, alfa_NO, factor;
	double 	XPtemp, XStemp, XStemp2;
    double  biomass, biomass_nobio, biomass_bioN, remainCOD, inertX, noninertX, inertS, utemp[35];
	int	i;

    /* parameters defined in adm1init_bsm2.m, INTERFACEPAR */
    CODequiv = mxGetPr(PAR)[0];         /* not used in ADM2ASM */
    fnaa = mxGetPr(PAR)[1];
    fnxc = mxGetPr(PAR)[2];
    fnbac = mxGetPr(PAR)[3];
    fxni = mxGetPr(PAR)[4];
    fsni = mxGetPr(PAR)[5];
    fsni_adm = mxGetPr(PAR)[6];
    frlixs = mxGetPr(PAR)[7];           /* not used in ADM2ASM */
    frlibac = mxGetPr(PAR)[8];          /* not used in ADM2ASM */
    frxs_adm = mxGetPr(PAR)[9];         /* not used in ADM2ASM */
    fdegrade_adm = mxGetPr(PAR)[10];    /* not used in ADM2ASM */
    frxs_as = mxGetPr(PAR)[11];
    fdegrade_as = mxGetPr(PAR)[12];
    R = mxGetPr(PAR)[13];
    T_base = mxGetPr(PAR)[14];
    T_op = mxGetPr(PAR)[15];          /* should be an input variable if dynamic temperature control is used */
    pK_w_base = mxGetPr(PAR)[16];
    pK_a_va_base = mxGetPr(PAR)[17];
    pK_a_bu_base = mxGetPr(PAR)[18];
    pK_a_pro_base = mxGetPr(PAR)[19];
    pK_a_ac_base = mxGetPr(PAR)[20];
    pK_a_co2_base = mxGetPr(PAR)[21];
    pK_a_IN_base = mxGetPr(PAR)[22];

    pH_adm = u[33];

    factor = (1.0/T_base - 1.0/T_op)/(100.0*R);
    pK_w = pK_w_base - log10(exp(55900.0*factor));
    pK_a_co2 = pK_a_co2_base - log10(exp(7646.0*factor));
    pK_a_IN = pK_a_IN_base - log10(exp(51965.0*factor));
    alfa_va = 1.0/208.0*(-1.0/(1.0 + pow(10, pK_a_va_base - pH_adm)));
    alfa_bu = 1.0/160.0*(-1.0/(1.0 + pow(10, pK_a_bu_base - pH_adm)));
    alfa_pro = 1.0/112.0*(-1.0/(1.0 + pow(10, pK_a_pro_base - pH_adm)));
    alfa_ac = 1.0/64.0*(-1.0/(1.0 + pow(10, pK_a_ac_base - pH_adm)));
    alfa_co2 = -1.0/(1.0 + pow(10, pK_a_co2 - pH_adm));
    alfa_IN = (pow(10, pK_a_IN - pH_adm))/(1.0 + pow(10, pK_a_IN - pH_adm));
    alfa_NH = 1.0/14000.0;  /* convert mgN/l into kmoleN/m3 */
    alfa_alk = -0.001;      /* convert moleHCO3/m3 into kmoleHCO3/m3 */
    alfa_NO = -1.0/14000.0; /* convert mgN/l into kmoleN/m3 */

	for (i = 0; i < 35; i++)
     	utemp[i] = u[i];

	for (i = 0; i < 21; i++)
		y[i] = 0.0;

    /*================================================================================================*/
    /* Biomass becomes part of XS and XP when transformed into ASM
	* Assume Npart of formed XS to be fnxc and Npart of XP to be fxni
	* Remaining N goes into the ammonia pool (also used as source if necessary) */

    biomass = 1000.0*(utemp[16] + utemp[17] + utemp[18] + utemp[19] + utemp[20] + utemp[21] + utemp[22]);
    biomass_nobio = biomass*(1.0 - frxs_as);   /* part which is mapped to XP */
    biomass_bioN = (biomass*fnbac - biomass_nobio*fxni);
    remainCOD = 0.0;
    if (biomass_bioN < 0.0) {
        /* Problems: if here we should print 'WARNING: not enough biomass N to map the requested inert part of biomass' */
        /* We map as much as we can, and the remains go to XS! */
        XPtemp = biomass*fnbac/fxni;
        biomass_nobio = XPtemp;
        biomass_bioN = 0.0;
    }
    else  {
        XPtemp = biomass_nobio;
        }
    if ((biomass_bioN/fnxc) <= (biomass - biomass_nobio)) {
        XStemp = biomass_bioN/fnxc;        /* all biomass N used */
        remainCOD = biomass - biomass_nobio - XStemp;
        if ((utemp[10]*14000.0/fnaa) >= remainCOD) {  /* use part of remaining S_IN to form XS */
            XStemp = XStemp + remainCOD;
        }
        else {
            /* Problems: if here we should print 'ERROR: not enough nitrogen to map the requested XS part of biomass' */
            /* System failure! */
        }
    }
    else {
        XStemp = biomass - biomass_nobio; /* all biomass COD used */
    }

    utemp[10] = utemp[10] + biomass*fnbac/14000.0 - XPtemp*fxni/14000.0 - XStemp*fnxc/14000.0;  /* any remaining N in S_IN */
    y[3] = (utemp[12] + utemp[13] + utemp[14] + utemp[15])*1000.0 + XStemp;     /* Xs = sum all X except Xi, + biomass as handled above */
    y[6] = XPtemp;      /* inert part of biomass */


    /*================================================================================================*/
    /*  mapping of inert XI in AD into XI and possibly XS in AS
	* assumption: same N content in both ASM1 and ADM1 particulate inerts
	* special case: if part of XI in AD can be degraded in AS
	* we have no knowledge about the contents so we put it in as part substrate (XS)
	* we need to keep track of the associated nitrogen
	* N content may be different, take first from XI-N then S_IN,
	* Similar principle could be used for other states. */
    inertX = (1.0-fdegrade_as)*utemp[23]*1000.0;
    XStemp2 = 0.0;
    noninertX = 0.0;
    if (fdegrade_as > 0.0) {
        noninertX = fdegrade_as*utemp[23]*1000.0;
        if (fxni < fnxc)  {     /* N in XI(AD) not enough */
            XStemp2 = noninertX*fxni/fnxc;
            noninertX = noninertX - noninertX*fxni/fnxc;
            if ((utemp[10]*14000.0) < (noninertX*fnxc))  {  /* N in SNH not enough */
                XStemp2 = XStemp2 + (utemp[10]*14000.0)/fnxc;
                noninertX = noninertX - (utemp[10]*14000.0)/fnxc;
                utemp[10] = 0.0;
                /* Problems: if here we should print 'WARNING: Nitrogen shortage when converting biodegradable XI' */
                /* Mapping what we can to XS and putting remaining XI back into XI of ASM */
                inertX = inertX + noninertX;
                }
            else  {   /* N in S_IN enough for mapping */
                XStemp2 = XStemp2 + noninertX;
                utemp[10] = utemp[10] - noninertX*fnxc/14000.0;
                noninertX = 0.0;
                }
            }
        else  {   /* N in XI(AD) enough for mapping */
            XStemp2 = XStemp2 + noninertX;
            utemp[10] = utemp[10] + noninertX*(fxni - fnxc)/14000.0;    /* put remaining N as S_IN */
            noninertX = 0;
            }
        }

    y[2] = inertX;          /* Xi = Xi*fdegrade_AS + possibly nonmappable XS */
    y[3] = y[3] + XStemp2;  /* extra added XS (biodegradable XI) */

    /*================================================================================================*/
    /* Mapping of ADM SI to ASM1 SI
    * It is assumed that this mapping will be 100% on COD basis
	* N content may be different, take first from SI-N then from S_IN.
	* Similar principle could be used for other states. */

    inertS = 0.0;
    if (fsni_adm < fsni) {   /* N in SI(AD) not enough */
        inertS = utemp[11]*fsni_adm/fsni;
        utemp[11] = utemp[11] - utemp[11]*fsni_adm/fsni;
        if ((utemp[10]*14.0) < (utemp[11]*fsni))  {  /* N in S_IN not enough */
            inertS = inertS + utemp[10]*14.0/fsni;
            utemp[11] = utemp[11] - utemp[10]*14.0/fsni;
            utemp[10] = 0.0;
            /* Problems: if here we should print 'ERROR: Nitrogen shortage when converting SI' */
            /* System failure: nowhere to put SI */
            }
        else  {  /* N in S_IN enough for mapping */
            inertS = inertS + utemp[11];
            utemp[10] = utemp[10] - utemp[11]*fsni/14.0;
            utemp[11] = 0.0;
            }
        }
    else  {    /* N in SI(AD) enough for mapping */
        inertS = inertS + utemp[11];
        utemp[10] = utemp[10] + utemp[11]*(fsni_adm - fsni)/14.0;  /* put remaining N as S_IN */
        utemp[11] = 0.0;
        }

    y[0] = inertS*1000.0;		/* Si = Si */

    /*================================================================================================*/
    /* Define the outputs including charge balance */

    /* nitrogen in biomass, composites, proteins
	* Xnd is the nitrogen part of Xs in ASM1. Therefore Xnd should be based on the
	* same variables as constitutes Xs, ie AD biomass (part not mapped to XP), xc and xpr if we assume
	* there is no nitrogen in carbohydrates and lipids. The N content of Xi is
    * not included in Xnd in ASM1 and should in my view not be included. */

    y[11] = fnxc*(XStemp + XStemp2) + fnxc*1000.0*utemp[12] + fnaa*1000.0*utemp[14];

    /* Snd is the nitrogen part of Ss in ASM1. Therefore Snd should be based on the
	* same variables as constitutes Ss, and we assume
	* there is only nitrogen in the amino acids. The N content of Si is
    * not included in Snd in ASM1 and should in my view not be included. */

    y[10] = fnaa*1000.0*utemp[1];

    /* sh2 and sch4 assumed to be stripped upon reentry to ASM side */

    y[1] = (utemp[0] + utemp[1] + utemp[2] + utemp[3] + utemp[4] + utemp[5] + utemp[6])*1000.0;	/* Ss = sum all S except Sh2, Sch4, Si, Sic, Sin */

    y[9] = utemp[10]*14000.0;		/* Snh = S_IN including adjustments above */

    y[13] = 0.75*(y[2] + y[3] + y[4] + y[5] + y[6]);
    y[14] = utemp[26];  /* flow rate */
    y[15] = u[34];   /* temperature, degC, should be equal to AS temperature into the AD/AS interface */
    y[16] = utemp[28];  /* dummy state */
    y[17] = utemp[29];  /* dummy state */
    y[18] = utemp[30];  /* dummy state */
    y[19] = utemp[31];  /* dummy state */
    y[20] = utemp[32];  /* dummy state */

    /* charge balance, output S_alk (molHCO3/m3) */
    y[12] = (u[3]*alfa_va + u[4]*alfa_bu + u[5]*alfa_pro + u[6]*alfa_ac + u[9]*alfa_co2 + u[10]*alfa_IN - y[8]*alfa_NO - y[9]*alfa_NH)/alfa_alk;

    /* Finally there should be a input-output mass balance check here of COD and N */

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
