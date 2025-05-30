asm1init_bsm1;
settler1dinit_bsm2;  % no changes from BSM1
hyddelayinit_bsm2;
reginit_bsm1;

load ./Influent_data/constinfluent_bsm1;
load ./Influent_data/dyninfluent_bsm2;


% General parameter for all subsystems
% TEMPMODEL: 0 - influent wastewater temperature is just passed through process reactors
%            1 - mass balance for the wastewater temperature is used in
%            process reactors
% Note: thickener and dewatering are ideal models, i.e. no impact since T_out =
% T_in, in flow splitters T_out = T_in and in flow combiners mass balance based heat balance is always used.

TEMPMODEL = [ 0 ];

% to activate calculation of  dummy states in settler, AS reactors and storage tank set ACTIVATE = 1
ACTIVATE = [ 0 ];
