% This initialisation file will set parameters and initial values for
% the primary clarifier. 
% The state values are based on BSM2 openloop results using the constant
% input file.
%
% Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden

% Volume of the primary clarifier
VOL_P = 900; % m3

% Efficiency Correction factor
f_corr = 0.65;

% CODpart/CODtot ratio (mean value)
f_X = 0.85;

% Smoothing time constant for qm calculation
t_m = 0.125;

% Ratio of primary sludge flow rate to the influent flow 
f_PS = 0.007;

% Initial values
S_I_P =  28.0670;
S_S_P =  59.0473;
X_I_P =  94.3557;
X_S_P =  356.8434;
X_BH_P = 50.8946;
X_BA_P = 0.0946;
X_P_P =  0.6531;
S_O_P =  0.0175;
S_NO_P = 0.1174;
S_NH_P = 34.9215;
S_ND_P = 5.5457;
X_ND_P = 15.8132;
S_ALK_P = 7.6965;
TSS_P = 377.1311;
Q_P = 2.1086e+04;
T_P = 14.8581;
S_D1_P = 0;
S_D2_P = 0;
S_D3_P = 0;
X_D4_P = 0;
X_D5_P = 0;

XINIT_P = [ S_I_P  S_S_P  X_I_P  X_S_P  X_BH_P  X_BA_P  X_P_P  S_O_P  S_NO_P  S_NH_P  S_ND_P  X_ND_P  S_ALK_P TSS_P Q_P T_P S_D1_P S_D2_P S_D3_P X_D4_P X_D5_P ];

% Vector with settleability of different components,
% compare with f_sx,i in Otterpohl/Freund
% XVEKTOR_P = [S_I  S_S  X_I  X_S  X_BH  X_BA  X_P  S_0  S_NO S_NH S_ND X_ND S_ALK TSS Q T S_D1 S_D2 S_D3 X_D4 X_D5]
XVEKTOR_P = [0  0  1  1  1  1  1  0  0  0  0  1  0  0  0  0  0  0  0  1  1];

PAR_P = [ f_corr  f_X  t_m  f_PS ];
