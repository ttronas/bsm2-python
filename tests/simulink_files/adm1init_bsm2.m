% This file initiates parameter values and sets initial conditions for any of the three
% model implementations adm1_ODE, adm1_DAE1 and adm1_DAE2. Note that some of the
% parameter values deviate from the values given in the ADM1-STR (Batstone et al., 2002).
% 
% Copyright 2006:
% Dr Christian Rosen, Dr Darko Vrecko and Dr Ulf Jeppsson
% Dept. Industrial Electrical Engineering and Automation
% Lund University, Sweden
% http://www.iea.lth.se
%
% The state values are based on BSM2 openloop results using the constant
% input file.
%
% Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden

S_su =  0.0124;
S_aa =  0.0055;
S_fa =  0.1074;
S_va =  0.0123;
S_bu = 0.0140;
S_pro = 0.0176;
S_ac =  0.0893;
S_h2 =  2.5055e-7;
S_ch4 = 0.0555;
S_IC = 0.0951;
S_IN = 0.0945;
S_I = 0.1309;
X_xc = 0.1079;
X_ch = 0.0205;
X_pr = 0.0842;
X_li = 0.0436;
X_su = 0.3122;
X_aa = 0.9317;
X_fa = 0.3384;
X_c4 = 0.3258;
X_pro = 0.1011;
X_ac = 0.6772;
X_h2 =  0.2848;
X_I =  17.2162;
S_cat =  3.5659e-43;
S_an =  0.0052;
S_hva = 0.0123;   % is actually Sva-
S_hbu = 0.0140;   % is actually Sbu-
S_hpro =  0.0175; % is actually Spro-
S_hac =  0.0890;   % is actually Sac-
S_hco3 = 0.0857;
S_nh3 = 0.0019;
S_gas_h2 = 1.1032e-5;
S_gas_ch4 = 1.6535;
S_gas_co2 = 0.0135;
Q_D = 178.4674;
T_D = 35;
S_D1_D = 0;
S_D2_D = 0;
S_D3_D = 0;
X_D4_D = 0;
X_D5_D = 0;

S_H_ion = 5.4562e-8;

% used by all three ADM implementations, adm1_ODE, adm1_DAE1 and adm1_DAE2.
DIGESTERINIT = [ S_su S_aa S_fa S_va S_bu S_pro S_ac S_h2 S_ch4 S_IC S_IN S_I X_xc X_ch X_pr X_li X_su X_aa X_fa X_c4 X_pro X_ac X_h2 ... 
                 X_I S_cat S_an S_hva S_hbu S_hpro S_hac S_hco3 S_nh3 S_gas_h2 S_gas_ch4 S_gas_co2 Q_D T_D S_D1_D S_D2_D S_D3_D X_D4_D X_D5_D ];

% used by both DAE ADM implementations, adm1_DAE1 and adm1_DAE2.
PHSOLVINIT = [ S_H_ion S_hva S_hbu S_hpro S_hac S_hco3 S_nh3 ];

% used by one DAE ADM implementation, adm1_DAE2.
SH2SOLVINIT = [ S_h2 ];

f_sI_xc = 0.1;
f_xI_xc = 0.2;
f_ch_xc = 0.2;
f_pr_xc = 0.2;
f_li_xc = 0.3;  
N_xc = 0.0376/14.0;
N_I = 0.06/14.0;
N_aa = 0.007;
C_xc = 0.02786;
C_sI = 0.03;
C_ch = 0.0313;
C_pr = 0.03;
C_li = 0.022;
C_xI = 0.03;
C_su = 0.0313;
C_aa = 0.03;
f_fa_li = 0.95;
C_fa = 0.0217;
f_h2_su = 0.19;
f_bu_su = 0.13;
f_pro_su = 0.27;
f_ac_su = 0.41;
N_bac = 0.08/14.0;
C_bu = 0.025;
C_pro = 0.0268;
C_ac = 0.0313;
C_bac = 0.0313;
Y_su = 0.1;
f_h2_aa = 0.06;
f_va_aa = 0.23;
f_bu_aa = 0.26;
f_pro_aa = 0.05;
f_ac_aa = 0.40;
C_va = 0.024;
Y_aa = 0.08;
Y_fa = 0.06;
Y_c4 = 0.06;
Y_pro = 0.04;
C_ch4 = 0.0156;
Y_ac = 0.05;
Y_h2 = 0.06;
k_dis = 0.5;
k_hyd_ch = 10.0;
k_hyd_pr = 10.0;
k_hyd_li = 10.0;
K_S_IN = 1.0e-4;
k_m_su = 30.0;
K_S_su = 0.5;
pH_UL_aa = 5.5;
pH_LL_aa = 4.0;
k_m_aa = 50.0;
K_S_aa = 0.3;
k_m_fa = 6.0;
K_S_fa = 0.4;
K_Ih2_fa = 5.0e-6;
k_m_c4 = 20.0;
K_S_c4 = 0.2;
K_Ih2_c4 = 1.0e-5;
k_m_pro = 13.0;
K_S_pro = 0.1;
K_Ih2_pro = 3.5e-6;
k_m_ac = 8.0;
K_S_ac = 0.15;
K_I_nh3 = 0.0018;
pH_UL_ac = 7.0;
pH_LL_ac = 6.0;
k_m_h2 = 35.0;
K_S_h2 = 7.0e-6;
pH_UL_h2 = 6.0;
pH_LL_h2 = 5.0;
k_dec_Xsu = 0.02;
k_dec_Xaa = 0.02;
k_dec_Xfa = 0.02;
k_dec_Xc4 = 0.02;
k_dec_Xpro = 0.02;
k_dec_Xac = 0.02;
k_dec_Xh2 = 0.02;
R = 0.083145;       % universal gas constant dm3*bar/(mol*K) = 8.3145 J/(mol*K)
T_base = 298.15;    % 25 degC = 298.15 K
T_op = 308.15;      % operational temperature of AD and interfaces, 35 degC, should really be an input
pK_w_base = 14.0;
pK_a_va_base = 4.86;
pK_a_bu_base = 4.82;
pK_a_pro_base = 4.88;
pK_a_ac_base = 4.76;
pK_a_co2_base = 6.35;
pK_a_IN_base = 9.25;
k_A_Bva = 1.0e10;     % 1e8; according to STR
k_A_Bbu = 1.0e10;     % 1e8; according to STR   
k_A_Bpro = 1.0e10;    % 1e8; according to STR
k_A_Bac = 1.0e10;     % 1e8; according to STR
k_A_Bco2 = 1.0e10;    % 1e8; according to STR
k_A_BIN = 1.0e10;     % 1e8; according to STR
P_atm = 1.013;        % bar
kLa = 200.0;
K_H_h2o_base = 0.0313;
K_H_co2_base = 0.035;
K_H_ch4_base = 0.0014;
K_H_h2_base = 7.8e-4;
k_P = 5.0e4;

DIGESTERPAR = [ f_sI_xc f_xI_xc f_ch_xc f_pr_xc f_li_xc N_xc N_I N_aa C_xc C_sI C_ch C_pr C_li C_xI C_su C_aa f_fa_li C_fa ...
f_h2_su f_bu_su f_pro_su f_ac_su N_bac C_bu C_pro C_ac C_bac Y_su f_h2_aa f_va_aa f_bu_aa f_pro_aa f_ac_aa C_va Y_aa Y_fa ...
Y_c4 Y_pro C_ch4 Y_ac Y_h2 k_dis k_hyd_ch k_hyd_pr k_hyd_li K_S_IN k_m_su K_S_su pH_UL_aa pH_LL_aa k_m_aa K_S_aa k_m_fa ...
K_S_fa K_Ih2_fa k_m_c4 K_S_c4 K_Ih2_c4 k_m_pro K_S_pro K_Ih2_pro k_m_ac K_S_ac K_I_nh3 pH_UL_ac pH_LL_ac k_m_h2 K_S_h2 ...
pH_UL_h2 pH_LL_h2 k_dec_Xsu k_dec_Xaa k_dec_Xfa k_dec_Xc4 k_dec_Xpro k_dec_Xac k_dec_Xh2 R T_base T_op pK_w_base pK_a_va_base pK_a_bu_base ...
pK_a_pro_base pK_a_ac_base pK_a_co2_base pK_a_IN_base k_A_Bva k_A_Bbu k_A_Bpro k_A_Bac k_A_Bco2 k_A_BIN P_atm kLa ...
K_H_h2o_base K_H_co2_base K_H_ch4_base K_H_h2_base k_P ];

V_liq = 3400; %m3, size of BSM2 AD
V_gas = 300;  %m3, size of BSM2 AD

DIM_D = [ V_liq V_gas ];

% parameters for ASM2ADM and ADM2ASM interfaces
% could be put it their own initialisation file
CODequiv = 40.0/14.0;
fnaa = N_aa*14.0;    % fraction of N in amino acids and Xpr as in ADM1 report
fnxc = N_xc*14.0;    % N content of composite material based on BSM2
fnbac = N_bac*14.0;  % N content of biomass based on BSM1, same in AS and AD
fxni = N_I*14.0;     % N content of inerts XI and XP, same in AS and AD
fsni = 0.0;          % N content of SI, assumed zero in ASM1 and BSM1
fsni_adm = N_I*14.0; % N content of SI in the AD system
% fnbac, fxni and fsni are adjusted to fit the benchmark values of iXB=0.08 and
% iXP=0.06 in the AS. 	
frlixs = 0.7;           % lipid fraction of non-nitrogenous XS in BSM2
frlibac = 0.4;          % lipid fraction of non-nitrogenous biomass in BSM2
frxs_adm = 0.68;        % anaerobically degradable fraction of AS biomass in BSM2
fdegrade_adm = 0;	    % amount of AS XI and XP degradable in AD, zero in BSM2
frxs_as = 0.79;         % aerobically degradable fraction of AD biomass in BSM2
fdegrade_as = 0;	    % amount of AD XI and XP degradable in AS, zero in BSM2

pH_adm_init = 7.0;      % initial value of pH in ADM to be used by interfaces for the first sample

INTERFACEPAR = [ CODequiv fnaa fnxc fnbac fxni fsni fsni_adm frlixs frlibac frxs_adm fdegrade_adm frxs_as fdegrade_as ...
R T_base T_op pK_w_base pK_a_va_base pK_a_bu_base pK_a_pro_base pK_a_ac_base pK_a_co2_base pK_a_IN_base ];

% parameters for the pHdelay function
PHINIT = pH_adm_init;
PHTIMECONST = 0.01;