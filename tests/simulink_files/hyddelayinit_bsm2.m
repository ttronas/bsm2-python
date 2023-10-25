% hyddelayinit_bsm2
%
% The following states represent mass (g/d), flow is still in m3/d and the temperature is
% still in C, used by the hydraulic delay functions
% The state values are based on BSM2 openloop results using the constant
% input file.
%
% Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden

% hyddelay prior to AS reactors
S_I_ASin =  2.9056e+06;
S_S_ASin =  1.2920e+06;
X_I_ASin =  1.5864e+08;
X_S_ASin =  7.1895e+06;
X_BH_ASin = 2.3118e+08;
X_BA_ASin = 1.7266e+07;
X_P_ASin =  9.9818e+07;
S_O_ASin =  1.1391e+05;
S_NO_ASin = 7.6188e+05;
S_NH_ASin = 7.4430e+05;
S_ND_ASin = 1.6232e+05;
X_ND_ASin = 4.1923e+05;
S_ALK_ASin = 5.3815e+05;
TSS_ASin = 3.8557e+08;
Q_ASin = 1.03531e+05;
T_ASin = 14.8581;
S_D1_ASin = 0;
S_D2_ASin = 0;
S_D3_ASin = 0;
X_D4_ASin = 0;
X_D5_ASin = 0;

% hyddelay prior to primary clarifier
S_I_Pin =  5.9183e+05;
S_S_Pin =  1.2451e+06;
X_I_Pin =  1.9896e+06;
X_S_Pin =  7.5245e+06;
X_BH_Pin = 1.0732e+06;
X_BA_Pin = 1.9956e+03;
X_P_Pin =  1.3772e+04;
S_O_Pin =  369.9972;
S_NO_Pin = 2.4747e+03;
S_NH_Pin = 7.3637e+05;
S_ND_Pin = 1.1694e+05;
X_ND_Pin = 3.3344e+05;
S_ALK_Pin = 1.6229e+05;
TSS_Pin = 7.9523e+06;
Q_Pin = 2.1086e+04;
T_Pin = 14.8581;
S_D1_Pin = 0;
S_D2_Pin = 0;
S_D3_Pin = 0;
X_D4_Pin = 0;
X_D5_Pin = 0;

XINITDELAY = [ S_I_ASin  S_S_ASin  X_I_ASin  X_S_ASin  X_BH_ASin  X_BA_ASin  X_P_ASin  S_O_ASin  S_NO_ASin  S_NH_ASin  S_ND_ASin  X_ND_ASin  S_ALK_ASin TSS_ASin Q_ASin T_ASin S_D1_ASin S_D2_ASin S_D3_ASin X_D4_ASin X_D5_ASin ];
XINITDELAYPRIMARY = [ S_I_Pin  S_S_Pin  X_I_Pin  X_S_Pin  X_BH_Pin  X_BA_Pin  X_P_Pin  S_O_Pin  S_NO_Pin  S_NH_Pin  S_ND_Pin  X_ND_Pin  S_ALK_Pin TSS_Pin Q_Pin T_Pin S_D1_Pin S_D2_Pin S_D3_Pin X_D4_Pin X_D5_Pin ];

% time constant for hyddelay (days)
T = 0.0001;