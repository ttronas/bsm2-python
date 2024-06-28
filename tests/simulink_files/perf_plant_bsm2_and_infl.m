% Plant performance module for the BSM2
% Updated 2008-07-29 by UJ according to latest BSM2 specifications
% Updated 2009-01-07 by UJ to include Risk estimation package from LEQUIA,
% Girona University

% startime = time where plant evaluation period start (integer)
% stoptime = time where plant evaluation period stops (integer)

% Cut away first and last samples, i.e. t=smaller than starttime and
% t = larger than stoptime. The last 52 weeks of simulated data are used to
% evaluate the plant performance. Set plotflag = 1 to activate plotting.
%
% Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden

close all

start=clock;
disp(' ')
disp('***** Plant evaluation of BSM2 system initiated *****')
disp(['Start time for BSM2 evaluation (hour:min:sec) = ', num2str(round(start(4:6)))]); %Display start time of evaluation
disp(' ')

plotflag = 1;

starttime = 15;
stoptime = 20;

startindex=max(find(t <= starttime));
stopindex=min(find(t >= stoptime));

time_eval=t(startindex:stopindex);

sampletime = time_eval(2)-time_eval(1);
totalt=time_eval(end)-time_eval(1);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The plant performance is calculated using the updated BSM2
% plant performance evaluation criteria. The main criteria are:
% - EQI as for BSM1 (updated since Copp, 2002)
% - Operational Cost Index (OCI) = 1 * pumpenergyperd
%                                + 1 * airenergyperd
%                                + 1 * mixenergyperd
%                                  3 * TSSproducedperd
%                                + 3 * carbonmassperd
%                                - 6 * Methaneproducedperd
%                                + max(0,Heatenergyperd-7*Methaneproducedperd)
% - Violations including time in violation, number of violations and % of
% time in violation as for BSM1 (Copp, 2002)
% - 95 percentile effluent concentrations for SNH, TN and TSS
% - Risk index is calculated in a separate script (called at the end)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Effluent pollutant concentration discharge limits
totalCODemax = 100;
totalNemax = 18;
SNHemax = 4;
TSSemax = 30;
BOD5emax = 10;

% Pollutant weighting factors, effluent pollutants
BSS=2;
BCOD=1;
BNKj=30;
BNO=10;
BBOD5=2;

% Pumping energy factors
PF_Qintr = 0.004; % kWh/m3, pumping energy factor, internal AS recirculation
PF_Qr = 0.008;   % kWh/m3, pumping energy factor, AS sludge recycle
PF_Qw = 0.05;    % kWh/m3, pumping energy factor, AS wastage flow
PF_Qpu = 0.075;  % kWh/m3, pumping energy factor, pumped underflow from primary clarifier
PF_Qtu = 0.060;  % kWh/m3, pumping energy factor, pumped underflow from thickener
PF_Qdo = 0.004;  % kWh/m3, pumping energy factor, pumped underflow from dewatering unit

%cut out the parts of the files to be used
inpart=in(startindex:(stopindex-1),:);
ASinputpart=ASinput(startindex:(stopindex-1),:);
reac1part=reac1(startindex:(stopindex-1),:);
reac2part=reac2(startindex:(stopindex-1),:);
reac3part=reac3(startindex:(stopindex-1),:);
reac4part=reac4(startindex:(stopindex-1),:);
reac5part=reac5(startindex:(stopindex-1),:);
settlerpart=settler(startindex:(stopindex-1),:);
effluentpart=effluent(startindex:(stopindex-1),:);
sludgepart=sludge(startindex:(stopindex-1),:);
recpart=rec(startindex:(stopindex-1),:);

primarypart = primaryout(startindex:(stopindex-1),:);
thickenerpart = thickenerout(startindex:(stopindex-1),:);
digesterinpart = digesterin(startindex:(stopindex-1),:);
digesteroutpart = digesterout(startindex:(stopindex-1),:);
dewateringinpart = dewateringin(startindex:(stopindex-1),:);
dewateringoutpart = dewateringout(startindex:(stopindex-1),:);
storagepart = storageout(startindex:(stopindex-1),:);

qpassplantpart = qpassplant(startindex:(stopindex-1),:); % bypassed wastewater over whole plant, different BOD content
qpassASpart = qpassAS(startindex:(stopindex-1),:); % bypassed wastewater only over AS system, different BOD content

% Influent concentrations
timevector = time_eval(2:end)-time_eval(1:(end-1));

Qinvec = inpart(:,15).*timevector;
SIinvec = inpart(:,1).*Qinvec;
SSinvec = inpart(:,2).*Qinvec;
XIinvec = inpart(:,3).*Qinvec;
XSinvec = inpart(:,4).*Qinvec;
XBHinvec = inpart(:,5).*Qinvec;
XBAinvec = inpart(:,6).*Qinvec;
XPinvec = inpart(:,7).*Qinvec;
SOinvec = inpart(:,8).*Qinvec;
SNOinvec = inpart(:,9).*Qinvec;
SNHinvec = inpart(:,10).*Qinvec;
SNDinvec = inpart(:,11).*Qinvec;
XNDinvec = inpart(:,12).*Qinvec;
SALKinvec = inpart(:,13).*Qinvec;
TSSinvec = inpart(:,14).*Qinvec;
Tempinvec = inpart(:,16).*Qinvec;
if (ACTIVATE > 0.5)
    DUMMY1invec = inpart(:,17).*Qinvec;
    DUMMY2invec = inpart(:,18).*Qinvec;
    DUMMY3invec = inpart(:,19).*Qinvec;
    DUMMY4invec = inpart(:,20).*Qinvec;
    DUMMY5invec = inpart(:,21).*Qinvec;
end
Qintot = sum(Qinvec);
Qinav = Qintot/totalt;

SIinload = sum(SIinvec);
SSinload = sum(SSinvec);
XIinload = sum(XIinvec);
XSinload = sum(XSinvec);
XBHinload = sum(XBHinvec);
XBAinload = sum(XBAinvec);
XPinload = sum(XPinvec);
SOinload = sum(SOinvec);
SNOinload = sum(SNOinvec);
SNHinload = sum(SNHinvec);
SNDinload = sum(SNDinvec);
XNDinload = sum(XNDinvec);
SALKinload = sum(SALKinvec);
TSSinload = sum(TSSinvec);
Tempinload = sum(Tempinvec);
if (ACTIVATE > 0.5)
    DUMMY1inload = sum(DUMMY1invec);
    DUMMY2inload = sum(DUMMY2invec);
    DUMMY3inload = sum(DUMMY3invec);
    DUMMY4inload = sum(DUMMY4invec);
    DUMMY5inload = sum(DUMMY5invec);
end

SIinav = SIinload/Qintot;
SSinav = SSinload/Qintot;
XIinav = XIinload/Qintot;
XSinav = XSinload/Qintot;
XBHinav = XBHinload/Qintot;
XBAinav = XBAinload/Qintot;
XPinav = XPinload/Qintot;
SOinav = SOinload/Qintot;
SNOinav = SNOinload/Qintot;
SNHinav = SNHinload/Qintot;
SNDinav = SNDinload/Qintot;
XNDinav = XNDinload/Qintot;
SALKinav = SALKinload/Qintot;
TSSinav = TSSinload/Qintot;
Tempinav = Tempinload/Qintot;
if (ACTIVATE > 0.5)
    DUMMY1inav = DUMMY1inload/Qintot;
    DUMMY2inav = DUMMY2inload/Qintot;
    DUMMY3inav = DUMMY3inload/Qintot;
    DUMMY4inav = DUMMY4inload/Qintot;
    DUMMY5inav = DUMMY5inload/Qintot;
end

TKNinav = SNHinav+SNDinav+XNDinav+i_XB*(XBHinav+XBAinav)+i_XP*(XIinav+XPinav);
TNinav = SNOinav+TKNinav;
TCODinav = SIinav+SSinav+XIinav+XSinav+XBHinav+XBAinav+XPinav;
BOD5_SSinload = 0.65*(SSinload);
BOD5_XSinload = 0.65*(XSinload);
BOD5_XBHinload = 0.65*(1-f_P)*(XBHinload);
BOD5_XBAinload = 0.65*(1-f_P)*(XBAinload);
BOD5inav = (BOD5_SSinload + BOD5_XSinload + BOD5_XBHinload + BOD5_XBAinload)/Qintot;

Influentav=[Qinav SIinav SSinav XIinav XSinav XBHinav XBAinav XPinav SOinav SNOinav SNHinav SNDinav XNDinav SALKinav TSSinav Tempinav TKNinav TNinav TCODinav BOD5inav]';
if (ACTIVATE > 0.5)
   Influentav=[Qinav SIinav SSinav XIinav XSinav XBHinav XBAinav XPinav SOinav SNOinav SNHinav SNDinav XNDinav SALKinav TSSinav Tempinav TKNinav TNinav TCODinav BOD5inav DUMMY1inav DUMMY2inav DUMMY3inav DUMMY4inav DUMMY5inav ]';
end

totalNKjinvec2=(SNHinvec+SNDinvec+XNDinvec+i_XB*(XBHinvec+XBAinvec)+i_XP*(XPinvec+XIinvec))./Qinvec;
totalNinvec2=(SNOinvec+SNHinvec+SNDinvec+XNDinvec+i_XB*(XBHinvec+XBAinvec)+i_XP*(XPinvec+XIinvec))./Qinvec;
totalCODinvec2=(SIinvec+SSinvec+XIinvec+XSinvec+XBHinvec+XBAinvec+XPinvec)./Qinvec;
SNHinvec2=SNHinvec./Qinvec;
TSSinvec2=TSSinvec./Qinvec;
BOD5_SSinloadvec = 0.65*(SSinvec);
BOD5_XSinloadvec = 0.65*(XSinvec);
BOD5_XBHinloadvec = 0.65*(1-f_P)*(XBHinvec);
BOD5_XBAinloadvec = 0.65*(1-f_P)*(XBAinvec);
BOD5invec2 = (BOD5_SSinloadvec + BOD5_XSinloadvec + BOD5_XBHinloadvec + BOD5_XBAinloadvec)./Qinvec;

totalNKjinload=SNHinload+SNDinload+XNDinload+i_XB*(XBHinload+XBAinload)+i_XP*(XPinload+XIinload);
totalNinload=SNOinload+totalNKjinload;
totalCODinload=(SIinload+SSinload+XIinload+XSinload+XBHinload+XBAinload+XPinload);
BOD5inload = (BOD5_SSinload + BOD5_XSinload + BOD5_XBHinload + BOD5_XBAinload);

Inload=[SIinload SSinload XIinload XSinload XBHinload XBAinload XPinload SOinload SNOinload SNHinload SNDinload XNDinload SALKinload TSSinload Tempinload totalNKjinload totalNinload totalCODinload BOD5inload]'./(1000*totalt);
if (ACTIVATE > 0.5)
   Inload=[SIinload SSinload XIinload XSinload XBHinload XBAinload XPinload SOinload SNOinload SNHinload SNDinload XNDinload SALKinload TSSinload Tempinload totalNKjinload totalNinload totalCODinload BOD5inload DUMMY1inload DUMMY2inload DUMMY3inload DUMMY4inload DUMMY5inload ]'./(1000*totalt);
end

% Effluent concentrations
Qevec = effluentpart(:,15).*timevector;
SIevec = effluentpart(:,1).*Qevec;
SSevec = effluentpart(:,2).*Qevec;
XIevec = effluentpart(:,3).*Qevec;
XSevec = effluentpart(:,4).*Qevec;
XBHevec = effluentpart(:,5).*Qevec;
XBAevec = effluentpart(:,6).*Qevec;
XPevec = effluentpart(:,7).*Qevec;
SOevec = effluentpart(:,8).*Qevec;
SNOevec = effluentpart(:,9).*Qevec;
SNHevec = effluentpart(:,10).*Qevec;
SNDevec = effluentpart(:,11).*Qevec;
XNDevec = effluentpart(:,12).*Qevec;
SALKevec = effluentpart(:,13).*Qevec;
TSSevec = effluentpart(:,14).*Qevec;
Tempevec = effluentpart(:,16).*Qevec;
if (ACTIVATE > 0.5)
    DUMMY1evec = effluentpart(:,17).*Qevec;
    DUMMY2evec = effluentpart(:,18).*Qevec;
    DUMMY3evec = effluentpart(:,19).*Qevec;
    DUMMY4evec = effluentpart(:,20).*Qevec;
    DUMMY5evec = effluentpart(:,21).*Qevec;
end
Qetot = sum(Qevec);
Qeav = Qetot/totalt;

% special to handle different BOD content in bypassed effluent
Qbypassplantvec = qpassplantpart(:,15).*timevector;
SSbypassplantvec = qpassplantpart(:,2).*Qbypassplantvec;
XSbypassplantvec = qpassplantpart(:,4).*Qbypassplantvec;
XBHbypassplantvec = qpassplantpart(:,5).*Qbypassplantvec;
XBAbypassplantvec = qpassplantpart(:,6).*Qbypassplantvec;
QbypassASvec = qpassASpart(:,15).*timevector;
SSbypassASvec = qpassASpart(:,2).*QbypassASvec;
XSbypassASvec = qpassASpart(:,4).*QbypassASvec;
XBHbypassASvec = qpassASpart(:,5).*QbypassASvec;
XBAbypassASvec = qpassASpart(:,6).*QbypassASvec;
Qbypassplanttot = sum(Qbypassplantvec);
SSbypassplantload = sum(SSbypassplantvec);
XSbypassplantload = sum(XSbypassplantvec);
XBHbypassplantload = sum(XBHbypassplantvec);
XBAbypassplantload = sum(XBAbypassplantvec);
QbypassAStot = sum(QbypassASvec);
SSbypassASload = sum(SSbypassASvec);
XSbypassASload = sum(XSbypassASvec);
XBHbypassASload = sum(XBHbypassASvec);
XBAbypassASload = sum(XBAbypassASvec);


SIeload = sum(SIevec);
SSeload = sum(SSevec);
XIeload = sum(XIevec);
XSeload = sum(XSevec);
XBHeload = sum(XBHevec);
XBAeload = sum(XBAevec);
XPeload = sum(XPevec);
SOeload = sum(SOevec);
SNOeload = sum(SNOevec);
SNHeload = sum(SNHevec);
SNDeload = sum(SNDevec);
XNDeload = sum(XNDevec);
SALKeload = sum(SALKevec);
TSSeload = sum(TSSevec);
Tempeload = sum(Tempevec);
if (ACTIVATE > 0.5)
    DUMMY1eload = sum(DUMMY1evec);
    DUMMY2eload = sum(DUMMY2evec);
    DUMMY3eload = sum(DUMMY3evec);
    DUMMY4eload = sum(DUMMY4evec);
    DUMMY5eload = sum(DUMMY5evec);
end

SIeav = SIeload/Qetot;
SSeav = SSeload/Qetot;
XIeav = XIeload/Qetot;
XSeav = XSeload/Qetot;
XBHeav = XBHeload/Qetot;
XBAeav = XBAeload/Qetot;
XPeav = XPeload/Qetot;
SOeav = SOeload/Qetot;
SNOeav = SNOeload/Qetot;
SNHeav = SNHeload/Qetot;
SNDeav = SNDeload/Qetot;
XNDeav = XNDeload/Qetot;
SALKeav = SALKeload/Qetot;
TSSeav = TSSeload/Qetot;
Tempeav = Tempeload/Qetot;
if (ACTIVATE > 0.5)
    DUMMY1eav = DUMMY1eload/Qetot;
    DUMMY2eav = DUMMY2eload/Qetot;
    DUMMY3eav = DUMMY3eload/Qetot;
    DUMMY4eav = DUMMY4eload/Qetot;
    DUMMY5eav = DUMMY5eload/Qetot;
end

TKNeav = SNHeav+SNDeav+XNDeav+i_XB*(XBHeav+XBAeav)+i_XP*(XIeav+XPeav);
TNeav = SNOeav+TKNeav;
TCODeav = SIeav+SSeav+XIeav+XSeav+XBHeav+XBAeav+XPeav;
% special to handle different BOD factors in normal effluent and bypassed effluent
BOD5_SSload = 0.25*(SSeload-SSbypassplantload-SSbypassASload)+0.65*(SSbypassplantload+SSbypassASload);
BOD5_XSload = 0.25*(XSeload-XSbypassplantload-XSbypassASload)+0.65*(XSbypassplantload+XSbypassASload);
BOD5_XBHload = 0.25*(1-f_P)*(XBHeload-XBHbypassplantload-XBHbypassASload)+0.65*(1-f_P)*(XBHbypassplantload+XBHbypassASload);
BOD5_XBAload = 0.25*(1-f_P)*(XBAeload-XBAbypassplantload-XBAbypassASload)+0.65*(1-f_P)*(XBAbypassplantload+XBAbypassASload);
BOD5eav = (BOD5_SSload + BOD5_XSload + BOD5_XBHload + BOD5_XBAload)/Qetot;

Effluentav=[Qeav SIeav SSeav XIeav XSeav XBHeav XBAeav XPeav SOeav SNOeav SNHeav SNDeav XNDeav SALKeav TSSeav Tempeav TKNeav TNeav TCODeav BOD5eav]';
if (ACTIVATE > 0.5)
   Effluentav=[Qeav SIeav SSeav XIeav XSeav XBHeav XBAeav XPeav SOeav SNOeav SNHeav SNDeav XNDeav SALKeav TSSeav Tempeav TKNeav TNeav TCODeav BOD5eav DUMMY1eav DUMMY2eav DUMMY3eav DUMMY4eav DUMMY5eav ]';
end

totalNKjevec2=(SNHevec+SNDevec+XNDevec+i_XB*(XBHevec+XBAevec)+i_XP*(XPevec+XIevec))./Qevec;
totalNevec2=(SNOevec+SNHevec+SNDevec+XNDevec+i_XB*(XBHevec+XBAevec)+i_XP*(XPevec+XIevec))./Qevec;
totalCODevec2=(SIevec+SSevec+XIevec+XSevec+XBHevec+XBAevec+XPevec)./Qevec;
SNHevec2=SNHevec./Qevec;
TSSevec2=TSSevec./Qevec;
% special to handle different BOD factors in normal effluent and bypassed effluent
BOD5_SSloadvec = 0.25*(SSevec-SSbypassplantvec-SSbypassASvec)+0.65*(SSbypassplantvec+SSbypassASvec);
BOD5_XSloadvec = 0.25*(XSevec-XSbypassplantvec-XSbypassASvec)+0.65*(XSbypassplantvec+XSbypassASvec);
BOD5_XBHloadvec = 0.25*(1-f_P)*(XBHevec-XBHbypassplantvec-XBHbypassASvec)+0.65*(1-f_P)*(XBHbypassplantvec+XBHbypassASvec);
BOD5_XBAloadvec = 0.25*(1-f_P)*(XBAevec-XBAbypassplantvec-XBAbypassASvec)+0.65*(1-f_P)*(XBAbypassplantvec+XBAbypassASvec);
BOD5evec2 = (BOD5_SSloadvec + BOD5_XSloadvec + BOD5_XBHloadvec + BOD5_XBAloadvec)./Qevec;

totalNKjeload=SNHeload+SNDeload+XNDeload+i_XB*(XBHeload+XBAeload)+i_XP*(XPeload+XIeload);
totalNeload=SNOeload+totalNKjeload;
totalCODeload=(SIeload+SSeload+XIeload+XSeload+XBHeload+XBAeload+XPeload);
BOD5eload = (BOD5_SSload + BOD5_XSload + BOD5_XBHload + BOD5_XBAload);

Effload=[SIeload SSeload XIeload XSeload XBHeload XBAeload XPeload SOeload SNOeload SNHeload SNDeload XNDeload SALKeload TSSeload Tempeload totalNKjeload totalNeload totalCODeload BOD5eload]'./(1000*totalt);
if (ACTIVATE > 0.5)
   Effload=[SIeload SSeload XIeload XSeload XBHeload XBAeload XPeload SOeload SNOeload SNHeload SNDeload XNDeload SALKeload TSSeload Tempeload totalNKjeload totalNeload totalCODeload BOD5eload DUMMY1eload DUMMY2eload DUMMY3eload DUMMY4eload DUMMY5eload ]'./(1000*totalt);
end

% Sludge disposal concentrations
Qsvec = sludgepart(:,15).*timevector;
SIsvec = sludgepart(:,1).*Qsvec;
SSsvec = sludgepart(:,2).*Qsvec;
XIsvec = sludgepart(:,3).*Qsvec;
XSsvec = sludgepart(:,4).*Qsvec;
XBHsvec = sludgepart(:,5).*Qsvec;
XBAsvec = sludgepart(:,6).*Qsvec;
XPsvec = sludgepart(:,7).*Qsvec;
SOsvec = sludgepart(:,8).*Qsvec;
SNOsvec = sludgepart(:,9).*Qsvec;
SNHsvec = sludgepart(:,10).*Qsvec;
SNDsvec = sludgepart(:,11).*Qsvec;
XNDsvec = sludgepart(:,12).*Qsvec;
SALKsvec = sludgepart(:,13).*Qsvec;
TSSsvec = sludgepart(:,14).*Qsvec;
Tempsvec = sludgepart(:,16).*Qsvec;
if (ACTIVATE > 0.5)
    DUMMY1svec = sludgepart(:,17).*Qsvec;
    DUMMY2svec = sludgepart(:,18).*Qsvec;
    DUMMY3svec = sludgepart(:,19).*Qsvec;
    DUMMY4svec = sludgepart(:,20).*Qsvec;
    DUMMY5svec = sludgepart(:,21).*Qsvec;
end
Qstot = sum(Qsvec);
Qsav = Qstot/totalt;

SIsload = sum(SIsvec);
SSsload = sum(SSsvec);
XIsload = sum(XIsvec);
XSsload = sum(XSsvec);
XBHsload = sum(XBHsvec);
XBAsload = sum(XBAsvec);
XPsload = sum(XPsvec);
SOsload = sum(SOsvec);
SNOsload = sum(SNOsvec);
SNHsload = sum(SNHsvec);
SNDsload = sum(SNDsvec);
XNDsload = sum(XNDsvec);
SALKsload = sum(SALKsvec);
TSSsload = sum(TSSsvec);
Tempsload = sum(Tempsvec);
if (ACTIVATE > 0.5)
    DUMMY1sload = sum(DUMMY1svec);
    DUMMY2sload = sum(DUMMY2svec);
    DUMMY3sload = sum(DUMMY3svec);
    DUMMY4sload = sum(DUMMY4svec);
    DUMMY5sload = sum(DUMMY5svec);
end

SIsav = SIsload/Qstot;
SSsav = SSsload/Qstot;
XIsav = XIsload/Qstot;
XSsav = XSsload/Qstot;
XBHsav = XBHsload/Qstot;
XBAsav = XBAsload/Qstot;
XPsav = XPsload/Qstot;
SOsav = SOsload/Qstot;
SNOsav = SNOsload/Qstot;
SNHsav = SNHsload/Qstot;
SNDsav = SNDsload/Qstot;
XNDsav = XNDsload/Qstot;
SALKsav = SALKsload/Qstot;
TSSsav = TSSsload/Qstot;
Tempsav = Tempsload/Qstot;
if (ACTIVATE > 0.5)
    DUMMY1sav = DUMMY1sload/Qstot;
    DUMMY2sav = DUMMY2sload/Qstot;
    DUMMY3sav = DUMMY3sload/Qstot;
    DUMMY4sav = DUMMY4sload/Qstot;
    DUMMY5sav = DUMMY5sload/Qstot;
end

TKNsav = SNHsav+SNDsav+XNDsav+i_XB*(XBHsav+XBAsav)+i_XP*(XIsav+XPsav);
TNsav = SNOsav+TKNsav;
TCODsav = SIsav+SSsav+XIsav+XSsav+XBHsav+XBAsav+XPsav;
BOD5sav = 0.25*(SSsav+XSsav+(1-f_P)*(XBHsav+XBAsav));

Sludgeav=[Qsav SIsav SSsav XIsav XSsav XBHsav XBAsav XPsav SOsav SNOsav SNHsav SNDsav XNDsav SALKsav TSSsav Tempsav TKNsav TNsav TCODsav BOD5sav]';
if (ACTIVATE > 0.5)
   Sludgeav=[Qsav SIsav SSsav XIsav XSsav XBHsav XBAsav XPsav SOsav SNOsav SNHsav SNDsav XNDsav SALKsav TSSsav Tempsav TKNsav TNsav TCODsav BOD5sav DUMMY1sav DUMMY2sav DUMMY3sav DUMMY4sav DUMMY5sav ]';
end

totalNKjsvec2=(SNHsvec+SNDsvec+XNDsvec+i_XB*(XBHsvec+XBAsvec)+i_XP*(XPsvec+XIsvec))./Qsvec;
totalNsvec2=(SNOsvec+SNHsvec+SNDsvec+XNDsvec+i_XB*(XBHsvec+XBAsvec)+i_XP*(XPsvec+XIsvec))./Qsvec;
totalCODsvec2=(SIsvec+SSsvec+XIsvec+XSsvec+XBHsvec+XBAsvec+XPsvec)./Qsvec;
SNHsvec2=SNHsvec./Qsvec;
TSSsvec2=TSSsvec./Qsvec;
BOD5svec2=(0.25*(SSsvec+XSsvec+(1-f_P)*(XBHsvec+XBAsvec)))./Qsvec;

totalNKjsload=SNHsload+SNDsload+XNDsload+i_XB*(XBHsload+XBAsload)+i_XP*(XPsload+XIsload);
totalNsload=SNOsload+totalNKjsload;
totalCODsload=(SIsload+SSsload+XIsload+XSsload+XBHsload+XBAsload+XPsload);
BOD5sload=(0.25*(SSsload+XSsload+(1-f_P)*(XBHsload+XBAsload)));

Sludgeload=[SIsload SSsload XIsload XSsload XBHsload XBAsload XPsload SOsload SNOsload SNHsload SNDsload XNDsload SALKsload TSSsload Tempsload totalNKjsload totalNsload totalCODsload BOD5sload]'./(1000*totalt);
if (ACTIVATE > 0.5)
   Sludgeload=[SIsload SSsload XIsload XSsload XBHsload XBAsload XPsload SOsload SNOsload SNHsload SNDsload XNDsload SALKsload TSSsload Tempsload totalNKjsload totalNsload totalCODsload BOD5sload DUMMY1sload DUMMY2sload DUMMY3sload DUMMY4sload DUMMY5sload ]'./(1000*totalt);
end

% Influent and Effluent quality index
% Note: DUMMY variables should be added here if they have COD, BOD or N content
SSin=inpart(:,14);
CODin=inpart(:,1)+inpart(:,2)+inpart(:,3)+inpart(:,4)+inpart(:,5)+inpart(:,6)+inpart(:,7);
SNKjin=inpart(:,10)+inpart(:,11)+inpart(:,12)+i_XB*(inpart(:,5)+inpart(:,6))+i_XP*(inpart(:,3)+inpart(:,7));
SNOin=inpart(:,9);
BOD5in=0.65*(inpart(:,2)+inpart(:,4)+(1-f_P)*(inpart(:,5)+inpart(:,6)));

SSe=effluentpart(:,14);
CODe=effluentpart(:,1)+effluentpart(:,2)+effluentpart(:,3)+effluentpart(:,4)+effluentpart(:,5)+effluentpart(:,6)+effluentpart(:,7);
SNKje=effluentpart(:,10)+effluentpart(:,11)+effluentpart(:,12)+i_XB*(effluentpart(:,5)+effluentpart(:,6))+i_XP*(effluentpart(:,3)+effluentpart(:,7));
SNOe=effluentpart(:,9);
BOD5e=BOD5evec2;

EQIvecinst=(BSS*SSe+BCOD*CODe+BNKj*SNKje+BNO*SNOe+BBOD5*BOD5e).*effluentpart(:,15);

IQIvec=(BSS*SSin+BCOD*CODin+BNKj*SNKjin+BNO*SNOin+BBOD5*BOD5in).*Qinvec;
IQI=sum(IQIvec)/(totalt*1000);
EQIvec=(BSS*SSe+BCOD*CODe+BNKj*SNKje+BNO*SNOe+BBOD5*BOD5e).*Qevec;
EQI=sum(EQIvec)/(totalt*1000);

% Sludge production (calculated as kg TSS produced for the complete evaluation period)
TSSreactors_start = (reac1part(1,14)*VOL1+reac2part(1,14)*VOL2+reac3part(1,14)*VOL3+reac4part(1,14)*VOL4+reac5part(1,14)*VOL5)/1000;
TSSreactors_end = (reac1part(end,14)*VOL1+reac2part(end,14)*VOL2+reac3part(end,14)*VOL3+reac4part(end,14)*VOL4+reac5part(end,14)*VOL5)/1000;

TSSsettler_start=(settlerpart(1,44)*DIM(1)*DIM(2)/10+settlerpart(1,45)*DIM(1)*DIM(2)/10+settlerpart(1,46)*DIM(1)*DIM(2)/10+settlerpart(1,47)*DIM(1)*DIM(2)/10+settlerpart(1,48)*DIM(1)*DIM(2)/10+settlerpart(1,49)*DIM(1)*DIM(2)/10+settlerpart(1,50)*DIM(1)*DIM(2)/10+settlerpart(1,51)*DIM(1)*DIM(2)/10+settlerpart(1,52)*DIM(1)*DIM(2)/10+settlerpart(1,53)*DIM(1)*DIM(2)/10)/1000;
TSSsettler_end=(settlerpart(end,44)*DIM(1)*DIM(2)/10+settlerpart(end,45)*DIM(1)*DIM(2)/10+settlerpart(end,46)*DIM(1)*DIM(2)/10+settlerpart(end,47)*DIM(1)*DIM(2)/10+settlerpart(end,48)*DIM(1)*DIM(2)/10+settlerpart(end,49)*DIM(1)*DIM(2)/10+settlerpart(end,50)*DIM(1)*DIM(2)/10+settlerpart(end,51)*DIM(1)*DIM(2)/10+settlerpart(end,52)*DIM(1)*DIM(2)/10+settlerpart(end,53)*DIM(1)*DIM(2)/10)/1000;

TSSprimary_start = primarypart(1,56)*VOL_P/1000;
TSSprimary_end = primarypart(end,56)*VOL_P/1000;

TSSdigester_start = digesteroutpart(1,14)*V_liq/1000;
TSSdigester_end = digesteroutpart(end,14)*V_liq/1000;

TSSstorage_start = storagepart(1,14)*storagepart(1,22)/1000;
TSSstorage_end = storagepart(end,14)*storagepart(end,22)/1000;

TSSsludgeconc=sludgepart(:,14)/1000;  %kg/m3
Qsludgeflow=sludgepart(:,15);         %m3/d

TSSsludgevec=TSSsludgeconc.*Qsludgeflow.*timevector;

TSSproduced=sum(TSSsludgevec)+TSSreactors_end+TSSsettler_end+TSSprimary_end+TSSdigester_end+TSSstorage_end-TSSreactors_start-TSSsettler_start-TSSprimary_start-TSSdigester_start-TSSstorage_start;
TSSproducedperd=TSSproduced/totalt;

Sludgetoeff=TSSeload/1000;
Sludgetoeffperd=TSSeload/(1000*totalt);

Totsludgeprod=TSSproduced+TSSeload/1000;
Totsludgeprodperd=TSSproduced/totalt+TSSeload/(1000*totalt);

% Aeration energy (calculated as kWh consumed for the complete evaluation period)
%Script to modify the workspace variables (Kla, carb) from scalars to
%vectors in the openloop simulations. The function changeScalarToVector is
%defined at the end of this script.
invecsize = size(t);
kla1in=changeScalarToVector(kla1in,invecsize);
kla2in=changeScalarToVector(kla2in,invecsize);
kla3in=changeScalarToVector(kla3in,invecsize);
kla4in=changeScalarToVector(kla4in,invecsize);
kla5in=changeScalarToVector(kla5in,invecsize);

carbon1in=changeScalarToVector(carbon1in,invecsize);
carbon2in=changeScalarToVector(carbon2in,invecsize);
carbon3in=changeScalarToVector(carbon3in,invecsize);
carbon4in=changeScalarToVector(carbon4in,invecsize);
carbon5in=changeScalarToVector(carbon5in,invecsize);
kla1vec = kla1in(startindex:(stopindex-1),:);
kla2vec = kla2in(startindex:(stopindex-1),:);
kla3vec = kla3in(startindex:(stopindex-1),:);
kla4vec = kla4in(startindex:(stopindex-1),:);
kla5vec = kla5in(startindex:(stopindex-1),:);

kla1newvec = SOSAT1*VOL1*kla1vec;
kla2newvec = SOSAT2*VOL2*kla2vec;
kla3newvec = SOSAT3*VOL3*kla3vec;
kla4newvec = SOSAT4*VOL4*kla4vec;
kla5newvec = SOSAT5*VOL5*kla5vec;
airenergyvec = (kla1newvec+kla2newvec+kla3newvec+kla4newvec+kla5newvec)/(1.8*1000);
airenergy = sum(airenergyvec.*timevector);
airenergyperd = airenergy/totalt; % for OCI

% Mixing energy (calculated as kWh consumed for the complete evaluation period)
mixnumreac1 = length(find(kla1vec<20));
mixnumreac2 = length(find(kla2vec<20));
mixnumreac3 = length(find(kla3vec<20));
mixnumreac4 = length(find(kla4vec<20));
mixnumreac5 = length(find(kla5vec<20));

mixenergyunitreac = 0.005; %kW/m3

mixenergyreac1 = mixnumreac1*mixenergyunitreac*VOL1;
mixenergyreac2 = mixnumreac2*mixenergyunitreac*VOL2;
mixenergyreac3 = mixnumreac3*mixenergyunitreac*VOL3;
mixenergyreac4 = mixnumreac4*mixenergyunitreac*VOL4;
mixenergyreac5 = mixnumreac5*mixenergyunitreac*VOL5;

mixenergyreac = 24*(mixenergyreac1+mixenergyreac2+mixenergyreac3+mixenergyreac4+mixenergyreac5)*sampletime;

mixenergyunitAD = 0.005; %0.01 kW/m3 (Keller and Hartley, 2003)
mixenergyAD = 24*mixenergyunitAD*V_liq*totalt;

mixenergy = mixenergyreac+mixenergyAD;
mixenergyperd = mixenergy/totalt;

% Pumping energy (calculated as kWh consumed for the complete evaluation period)
Qintrflow = recpart(:,15);
Qrflow = settlerpart(:,15);
Qwflow = settlerpart(:,22);
Quprimaryflow = primarypart(:,36);
Quthickenerflow = thickenerpart(:,15);
Qodewateringflow = dewateringoutpart(:,36);
% should we add pumping energy for storage tank pumping?

pumpenergyvec = PF_Qintr*Qintrflow+PF_Qr*Qrflow+PF_Qw*Qwflow+PF_Qpu*Quprimaryflow+PF_Qtu*Quthickenerflow+PF_Qdo*Qodewateringflow;
pumpenergy = sum(pumpenergyvec.*timevector);
pumpenergyperd=pumpenergy/totalt;

% Carbon source addition
carbon1vec = carbon1in(startindex:(stopindex-1),:);
carbon2vec = carbon2in(startindex:(stopindex-1),:);
carbon3vec = carbon3in(startindex:(stopindex-1),:);
carbon4vec = carbon4in(startindex:(stopindex-1),:);
carbon5vec = carbon5in(startindex:(stopindex-1),:);
Qcarbonvec = (carbon1vec+carbon2vec+carbon3vec+carbon4vec+carbon5vec);
carbonmassvec = Qcarbonvec*CARBONSOURCECONC/1000;
Qcarbon = sum(Qcarbonvec.*timevector); %m3
carbonmass = sum(carbonmassvec.*timevector); %kg COD
carbonmassperd = carbonmass/totalt; %for OCI

% Methane, H2, CO2 production, updated for new order of variables, UJ 2007-01-15
Methanevec = digesteroutpart(:,48)./digesteroutpart(:,50)*P_atm*16/(R*T_op); %kg CH4/m3
Methaneflowvec = Methanevec.*digesteroutpart(:,51);
Methaneprod = sum(Methaneflowvec.*timevector);
Methaneprodperd = Methaneprod/totalt; %kg CH4/d
EnergyfromMethaneperd = Methaneprodperd*50014/3600; %kWh/d
Hydrogenvec = digesteroutpart(:,47)./digesteroutpart(:,50)*P_atm*2/(R*T_op); %kg H2/m3
Hydrogenflowvec = Hydrogenvec.*digesteroutpart(:,51);
Hydrogenprod = sum(Hydrogenflowvec.*timevector);
Hydrogenprodperd = Hydrogenprod/totalt; %kg H2/d
Carbondioxidevec = digesteroutpart(:,49)./digesteroutpart(:,50)*P_atm*44/(R*T_op); %kg CO2/m3
Carbondioxideflowvec = Carbondioxidevec.*digesteroutpart(:,51);
Carbondioxideprod = sum(Carbondioxideflowvec.*timevector);
Carbondioxideprodperd = Carbondioxideprod/totalt; %kg CO2/d

Qgasvec=digesteroutpart(:,51).*timevector;
Qgastot = sum(Qgasvec);
Qgasav = Qgastot/totalt;

% Heating energy for anaerobic digester
ro = 1000; %Water density in kg/m3
cp = 4.186; %Specific heat capacity for water in Ws/gC
% Potential truck input to AD has been removed below
Tdigesterin = (primarypart(:,37).*primarypart(:,36)+thickenerpart(:,16).*thickenerpart(:,15))./(primarypart(:,36)+thickenerpart(:,15));
Heatpower = (35-Tdigesterin).*digesterinpart(:,27)*ro*cp/86400; %kW
Heatenergyperd = 24*sum(Heatpower.*timevector)/totalt; %kWh/d

% Operational Cost Index, OCI
TSScost=3*TSSproducedperd;
airenergycost=1*airenergyperd;
mixenergycost=1*mixenergyperd;
pumpenergycost=1*pumpenergyperd;
carbonmasscost=3*carbonmassperd;
EnergyfromMethaneperdcost = 6*Methaneprodperd;
Heatenergycost = max(0,Heatenergyperd-7*Methaneprodperd);

OCI=TSScost+airenergycost+mixenergycost+pumpenergycost+carbonmasscost-EnergyfromMethaneperdcost+Heatenergycost;

% Calculate 95% percentiles for effluent SNH, TN and TSS
SNHeffprctile=prctile(SNHevec2,95);
TNeffprctile=prctile(totalNevec2,95);
TSSeffprctile=prctile(TSSevec2,95);

disp(' ')
disp(['Overall plant performance during time ',num2str(time_eval(1)),' to ',num2str(time_eval(end)),' days'])
disp('*****************************************************')
disp(' ')
disp('Influent average concentrations based on load')
disp('---------------------------------------------')
disp(['Influent average flow rate = ',num2str(Qinav),' m3/d'])
disp(['Influent average SI conc = ',num2str(SIinav),' g COD/m3'])
disp(['Influent average SS conc = ',num2str(SSinav),' g COD/m3'])
disp(['Influent average XI conc = ',num2str(XIinav),' g COD/m3'])
disp(['Influent average XS conc = ',num2str(XSinav),' g COD/m3'])
disp(['Influent average XBH conc = ',num2str(XBHinav),' g COD/m3'])
disp(['Influent average XBA conc = ',num2str(XBAinav),' g COD/m3'])
disp(['Influent average XP conc = ',num2str(XPinav),' g COD/m3'])
disp(['Influent average SO conc = ',num2str(SOinav),' g (-COD)/m3'])
disp(['Influent average SNO conc = ',num2str(SNOinav),' g N/m3'])
disp(['Influent average SNH conc = ',num2str(SNHinav),' g N/m3'])
disp(['Influent average SND conc = ',num2str(SNDinav),' g N/m3'])
disp(['Influent average XND conc = ',num2str(XNDinav),' g N/m3'])
disp(['Influent average SALK conc = ',num2str(SALKinav),' mol HCO3/m3'])
disp(['Influent average TSS conc = ',num2str(TSSinav),' g SS/m3'])
disp(['Influent average Temperature = ',num2str(Tempinav),' degC'])
if (ACTIVATE > 0.5)
    disp(['Influent average DUMMY1 conc = ',num2str(DUMMY1inav),' g xxx/m3'])
    disp(['Influent average DUMMY2 conc = ',num2str(DUMMY2inav),' g xxx/m3'])
    disp(['Influent average DUMMY3 conc = ',num2str(DUMMY3inav),' g xxx/m3'])
    disp(['Influent average DUMMY4 conc = ',num2str(DUMMY4inav),' g xxx/m3'])
    disp(['Influent average DUMMY5 conc = ',num2str(DUMMY5inav),' g xxx/m3'])
end
disp(' ')
disp(['Influent average Kjeldahl N conc = ',num2str(TKNinav),' g N/m3'])
disp(['Influent average total N conc = ',num2str(TNinav),' g N/m3'])
disp(['Influent average total COD conc = ',num2str(TCODinav),' g COD/m3'])
disp(['Influent average BOD5 conc = ',num2str(BOD5inav),' g/m3'])
disp(' ')
disp('Influent average load')
disp('---------------------')
disp(['Influent average SI load = ',num2str(SIinload/(1000*totalt)),' kg COD/day'])
disp(['Influent average SS load = ',num2str(SSinload/(1000*totalt)),' kg COD/day'])
disp(['Influent average XI load = ',num2str(XIinload/(1000*totalt)),' kg COD/day'])
disp(['Influent average XS load = ',num2str(XSinload/(1000*totalt)),' kg COD/day'])
disp(['Influent average XBH load = ',num2str(XBHinload/(1000*totalt)),' kg COD/day'])
disp(['Influent average XBA load = ',num2str(XBAinload/(1000*totalt)),' kg COD/day'])
disp(['Influent average XP load = ',num2str(XPinload/(1000*totalt)),' kg COD/day'])
disp(['Influent average SO load = ',num2str(SOinload/(1000*totalt)),' kg (-COD)/day'])
disp(['Influent average SNO load = ',num2str(SNOinload/(1000*totalt)),' kg N/day'])
disp(['Influent average SNH load = ',num2str(SNHinload/(1000*totalt)),' kg N/day'])
disp(['Influent average SND load = ',num2str(SNDinload/(1000*totalt)),' kg N/day'])
disp(['Influent average XND load = ',num2str(XNDinload/(1000*totalt)),' kg N/day'])
disp(['Influent average SALK load = ',num2str(SALKinload/(1000*totalt)),' kmol HCO3/day'])
disp(['Influent average TSS load = ',num2str(TSSinload/(1000*totalt)),' kg SS/day'])
if (ACTIVATE > 0.5)
    disp(['Influent average DUMMY1 load = ',num2str(DUMMY1inload/(1000*totalt)),' kg xxx/day'])
    disp(['Influent average DUMMY2 load = ',num2str(DUMMY2inload/(1000*totalt)),' kg xxx/day'])
    disp(['Influent average DUMMY3 load = ',num2str(DUMMY3inload/(1000*totalt)),' kg xxx/day'])
    disp(['Influent average DUMMY4 load = ',num2str(DUMMY4inload/(1000*totalt)),' kg xxx/day'])
    disp(['Influent average DUMMY5 load = ',num2str(DUMMY5inload/(1000*totalt)),' kg xxx/day'])
end
disp(' ')
disp(['Influent average Kjeldahl N load = ',num2str(totalNKjinload/(1000*totalt)),' kg N/d'])
disp(['Influent average total N load = ',num2str(totalNinload/(1000*totalt)),' kg N/d'])
disp(['Influent average total COD load = ',num2str(totalCODinload/(1000*totalt)),' kg COD/d'])
disp(['Influent average BOD5 load = ',num2str(BOD5inload/(1000*totalt)),' kg BOD5/d'])

disp(' ')
disp('Effluent average concentrations based on load')
disp('---------------------------------------------')
disp(['Effluent average flow rate = ',num2str(Qeav),' m3/d'])
disp(['Effluent average SI conc = ',num2str(SIeav),' g COD/m3'])
disp(['Effluent average SS conc = ',num2str(SSeav),' g COD/m3'])
disp(['Effluent average XI conc = ',num2str(XIeav),' g COD/m3'])
disp(['Effluent average XS conc = ',num2str(XSeav),' g COD/m3'])
disp(['Effluent average XBH conc = ',num2str(XBHeav),' g COD/m3'])
disp(['Effluent average XBA conc = ',num2str(XBAeav),' g COD/m3'])
disp(['Effluent average XP conc = ',num2str(XPeav),' g COD/m3'])
disp(['Effluent average SO conc = ',num2str(SOeav),' g (-COD)/m3'])
disp(['Effluent average SNO conc = ',num2str(SNOeav),' g N/m3'])
disp(['Effluent average SNH conc = ',num2str(SNHeav),' g N/m3  (limit = 4 g N/m3)'])
disp(['Effluent average SND conc = ',num2str(SNDeav),' g N/m3'])
disp(['Effluent average XND conc = ',num2str(XNDeav),' g N/m3'])
disp(['Effluent average SALK conc = ',num2str(SALKeav),' mol HCO3/m3'])
disp(['Effluent average TSS conc = ',num2str(TSSeav),' g SS/m3  (limit = 30 g SS/m3)'])
disp(['Effluent average Temperature = ',num2str(Tempeav),' degC'])
if (ACTIVATE > 0.5)
    disp(['Effluent average DUMMY1 conc = ',num2str(DUMMY1eav),' g xxx/m3'])
    disp(['Effluent average DUMMY2 conc = ',num2str(DUMMY2eav),' g xxx/m3'])
    disp(['Effluent average DUMMY3 conc = ',num2str(DUMMY3eav),' g xxx/m3'])
    disp(['Effluent average DUMMY4 conc = ',num2str(DUMMY4eav),' g xxx/m3'])
    disp(['Effluent average DUMMY5 conc = ',num2str(DUMMY5eav),' g xxx/m3'])
end
disp(' ')
disp(['Effluent average Kjeldahl N conc = ',num2str(TKNeav),' g N/m3'])
disp(['Effluent average total N conc = ',num2str(TNeav),' g N/m3  (limit = 18 g N/m3)'])
disp(['Effluent average total COD conc = ',num2str(TCODeav),' g COD/m3  (limit = 100 g COD/m3)'])
disp(['Effluent average BOD5 conc = ',num2str(BOD5eav),' g/m3  (limit = 10 g/m3)'])
disp(' ')
disp('Effluent average load')
disp('---------------------')
disp(['Effluent average SI load = ',num2str(SIeload/(1000*totalt)),' kg COD/day'])
disp(['Effluent average SS load = ',num2str(SSeload/(1000*totalt)),' kg COD/day'])
disp(['Effluent average XI load = ',num2str(XIeload/(1000*totalt)),' kg COD/day'])
disp(['Effluent average XS load = ',num2str(XSeload/(1000*totalt)),' kg COD/day'])
disp(['Effluent average XBH load = ',num2str(XBHeload/(1000*totalt)),' kg COD/day'])
disp(['Effluent average XBA load = ',num2str(XBAeload/(1000*totalt)),' kg COD/day'])
disp(['Effluent average XP load = ',num2str(XPeload/(1000*totalt)),' kg COD/day'])
disp(['Effluent average SO load = ',num2str(SOeload/(1000*totalt)),' kg (-COD)/day'])
disp(['Effluent average SNO load = ',num2str(SNOeload/(1000*totalt)),' kg N/day'])
disp(['Effluent average SNH load = ',num2str(SNHeload/(1000*totalt)),' kg N/day'])
disp(['Effluent average SND load = ',num2str(SNDeload/(1000*totalt)),' kg N/day'])
disp(['Effluent average XND load = ',num2str(XNDeload/(1000*totalt)),' kg N/day'])
disp(['Effluent average SALK load = ',num2str(SALKeload/(1000*totalt)),' kmol HCO3/day'])
disp(['Effluent average TSS load = ',num2str(TSSeload/(1000*totalt)),' kg SS/day'])
if (ACTIVATE > 0.5)
    disp(['Effluent average DUMMY1 load = ',num2str(DUMMY1eload/(1000*totalt)),' kg xxx/day'])
    disp(['Effluent average DUMMY2 load = ',num2str(DUMMY2eload/(1000*totalt)),' kg xxx/day'])
    disp(['Effluent average DUMMY3 load = ',num2str(DUMMY3eload/(1000*totalt)),' kg xxx/day'])
    disp(['Effluent average DUMMY4 load = ',num2str(DUMMY4eload/(1000*totalt)),' kg xxx/day'])
    disp(['Effluent average DUMMY5 load = ',num2str(DUMMY5eload/(1000*totalt)),' kg xxx/day'])
end
disp(' ')
disp(['Effluent average Kjeldahl N load = ',num2str(totalNKjeload/(1000*totalt)),' kg N/d'])
disp(['Effluent average total N load = ',num2str(totalNeload/(1000*totalt)),' kg N/d'])
disp(['Effluent average total COD load = ',num2str(totalCODeload/(1000*totalt)),' kg COD/d'])
disp(['Effluent average BOD5 load = ',num2str(BOD5eload/(1000*totalt)),' kg BOD5/d'])

disp(' ')
disp('Sludge for disposal average concentrations based on load')
disp('--------------------------------------------------------')
disp(['Sludge for disposal average flow rate = ',num2str(Qsav),' m3/d'])
disp(['Sludge for disposal average SI conc = ',num2str(SIsav),' g COD/m3'])
disp(['Sludge for disposal average SS conc = ',num2str(SSsav),' g COD/m3'])
disp(['Sludge for disposal average XI conc = ',num2str(XIsav),' g COD/m3'])
disp(['Sludge for disposal average XS conc = ',num2str(XSsav),' g COD/m3'])
disp(['Sludge for disposal average XBH conc = ',num2str(XBHsav),' g COD/m3'])
disp(['Sludge for disposal average XBA conc = ',num2str(XBAsav),' g COD/m3'])
disp(['Sludge for disposal average XP conc = ',num2str(XPsav),' g COD/m3'])
disp(['Sludge for disposal average SO conc = ',num2str(SOsav),' g (-COD)/m3'])
disp(['Sludge for disposal average SNO conc = ',num2str(SNOsav),' g N/m3'])
disp(['Sludge for disposal average SNH conc = ',num2str(SNHsav),' g N/m3'])
disp(['Sludge for disposal average SND conc = ',num2str(SNDsav),' g N/m3'])
disp(['Sludge for disposal average XND conc = ',num2str(XNDsav),' g N/m3'])
disp(['Sludge for disposal average SALK conc = ',num2str(SALKsav),' mol HCO3/m3'])
disp(['Sludge for disposal average TSS conc = ',num2str(TSSsav),' g SS/m3'])
disp(['Sludge for disposal average Temperature = ',num2str(Tempsav),' degC'])
if (ACTIVATE > 0.5)
    disp(['Sludge for disposal average DUMMY1 conc = ',num2str(DUMMY1sav),' g xxx/m3'])
    disp(['Sludge for disposal average DUMMY2 conc = ',num2str(DUMMY2sav),' g xxx/m3'])
    disp(['Sludge for disposal average DUMMY3 conc = ',num2str(DUMMY3sav),' g xxx/m3'])
    disp(['Sludge for disposal average DUMMY4 conc = ',num2str(DUMMY4sav),' g xxx/m3'])
    disp(['Sludge for disposal average DUMMY5 conc = ',num2str(DUMMY5sav),' g xxx/m3'])
end
disp(' ')
disp(['Sludge for disposal average Kjeldahl N conc = ',num2str(TKNsav),' g N/m3'])
disp(['Sludge for disposal average total N conc = ',num2str(TNsav),' g N/m3'])
disp(['Sludge for disposal average total COD conc = ',num2str(TCODsav),' g COD/m3'])
disp(['Sludge for disposal average BOD5 conc = ',num2str(BOD5sav),' g BOD5/m3'])
disp(' ')
disp('Sludge for disposal average load')
disp('--------------------------------')
disp(['Sludge for disposal average SI load = ',num2str(SIsload/(1000*totalt)),' kg COD/day'])
disp(['Sludge for disposal average SS load = ',num2str(SSsload/(1000*totalt)),' kg COD/day'])
disp(['Sludge for disposal average XI load = ',num2str(XIsload/(1000*totalt)),' kg COD/day'])
disp(['Sludge for disposal average XS load = ',num2str(XSsload/(1000*totalt)),' kg COD/day'])
disp(['Sludge for disposal average XBH load = ',num2str(XBHsload/(1000*totalt)),' kg COD/day'])
disp(['Sludge for disposal average XBA load = ',num2str(XBAsload/(1000*totalt)),' kg COD/day'])
disp(['Sludge for disposal average XP load = ',num2str(XPsload/(1000*totalt)),' kg COD/day'])
disp(['Sludge for disposal average SO load = ',num2str(SOsload/(1000*totalt)),' kg (-COD)/day'])
disp(['Sludge for disposal average SNO load = ',num2str(SNOsload/(1000*totalt)),' kg N/day'])
disp(['Sludge for disposal average SNH load = ',num2str(SNHsload/(1000*totalt)),' kg N/day'])
disp(['Sludge for disposal average SND load = ',num2str(SNDsload/(1000*totalt)),' kg N/day'])
disp(['Sludge for disposal average XND load = ',num2str(XNDsload/(1000*totalt)),' kg N/day'])
disp(['Sludge for disposal average SALK load = ',num2str(SALKsload/(1000*totalt)),' kmol HCO3/day'])
disp(['Sludge for disposal average TSS load = ',num2str(TSSsload/(1000*totalt)),' kg SS/day'])
if (ACTIVATE > 0.5)
    disp(['Sludge for disposal average DUMMY1 load = ',num2str(DUMMY1sload/(1000*totalt)),' kg xxx/day'])
    disp(['Sludge for disposal average DUMMY2 load = ',num2str(DUMMY2sload/(1000*totalt)),' kg xxx/day'])
    disp(['Sludge for disposal average DUMMY3 load = ',num2str(DUMMY3sload/(1000*totalt)),' kg xxx/day'])
    disp(['Sludge for disposal average DUMMY4 load = ',num2str(DUMMY4sload/(1000*totalt)),' kg xxx/day'])
    disp(['Sludge for disposal average DUMMY5 load = ',num2str(DUMMY5sload/(1000*totalt)),' kg xxx/day'])
end
disp(' ')
disp(['Sludge for disposal average Kjeldahl N load = ',num2str(totalNKjsload/(1000*totalt)),' kg N/d'])
disp(['Sludge for disposal average total N load = ',num2str(totalNsload/(1000*totalt)),' kg N/d'])
disp(['Sludge for disposal average total COD load = ',num2str(totalCODsload/(1000*totalt)),' kg COD/d'])
disp(['Sludge for disposal average BOD5 load = ',num2str(BOD5sload/(1000*totalt)),' kg BOD5/d'])
disp(' ')
disp('Other effluent quality variables')
disp('--------------------------------')
disp(['Influent Quality Index (IQI) = ',num2str(IQI),' kg poll.units/d'])
disp(['Effluent Quality Index (EQI) = ',num2str(EQI),' kg poll.units/d'])
disp(' ')
disp(['Sludge production for disposal = ',num2str(TSSproduced),' kg SS'])
disp(['Average sludge production for disposal per day = ',num2str(TSSproducedperd),' kg SS/d'])
disp(['Sludge production released into effluent = ',num2str(Sludgetoeff),' kg SS'])
disp(['Average sludge production released into effluent per day = ',num2str(Sludgetoeffperd),' kg SS/d'])
disp(['Total sludge production = ',num2str(Totsludgeprod),' kg SS'])
disp(['Total average sludge production per day = ',num2str(Totsludgeprodperd),' kg SS/d'])

disp(' ')
disp(['Average aeration energy = ',num2str(airenergyperd),' kWh/d'])
disp(['Average pumping energy = ',num2str(pumpenergyperd),' kWh/d'])
disp(['Average carbon source addition = ',num2str(carbonmassperd),' kg COD/d'])
disp(['Average mixing energy = ',num2str(mixenergyperd),' kWh/d'])
disp(['Average heating energy = ',num2str(Heatenergyperd),' kWh/d'])
disp(['Average methane production = ',num2str(Methaneprodperd),' kg CH4/d = ', num2str(Methaneprodperd*50.014/3.6),' kWh/d'])
disp(' ')
disp(['Average hydrogen gas production (kg H2/d) = ', num2str(Hydrogenprodperd),' kg H2/d']);
disp(['Average carbon dioxide gas production (kg CO2/d) = ', num2str(Carbondioxideprodperd),' kg CO2/d']);
disp(['Average total gas flow rate (AD, normalized to P_atm) = ', num2str(Qgasav), ' m3/d']);
disp(' ')

disp('Operational Cost Index')
disp('----------------------')
disp(['Sludge production cost index = ',num2str(TSScost)])
disp(['Aeration energy cost index = ',num2str(airenergycost)])
disp(['Pumping energy cost index = ',num2str(pumpenergycost)])
disp(['Carbon source dosage cost index = ',num2str(carbonmasscost)])
disp(['Mixing energy cost index = ',num2str(mixenergycost)])
disp(['Heating energy cost index = ',num2str(Heatenergycost)])
disp(['Net energy production from methane index = ',num2str(EnergyfromMethaneperdcost)])
disp(['Total Operational Cost Index (OCI) = ',num2str(OCI)])
disp(' ')
disp('Effluent violations')
disp('-------------------')
disp(['95% percentile for effluent SNH (Ammonia95) = ',num2str(SNHeffprctile),' g N/m3'])
disp(['95% percentile for effluent TN (TN95) = ',num2str(TNeffprctile),' g N/m3'])
disp(['95% percentile for effluent TSS (TSS95) = ',num2str(TSSeffprctile),' g SS/m3'])
disp(' ')

output=[Effluentav; Effload; IQI; EQI; TSSproduced; TSSproducedperd; Sludgetoeff; Sludgetoeffperd; Totsludgeprod; Totsludgeprodperd; airenergyperd; pumpenergyperd; carbonmassperd; mixenergyperd; Heatenergyperd; Methaneprodperd; TSScost; airenergycost; pumpenergycost; carbonmasscost; mixenergycost; Heatenergycost; EnergyfromMethaneperdcost; OCI; SNHeffprctile; TNeffprctile; TSSeffprctile];

save results output;

Nviolation=find(totalNevec2>totalNemax);
CODviolation=find(totalCODevec2>totalCODemax);
SNHviolation=find(SNHevec2>SNHemax);
TSSviolation=find(TSSevec2>TSSemax);
BOD5violation=find(BOD5evec2>BOD5emax);

noofNviolation = 1;
noofCODviolation = 1;
noofSNHviolation = 1;
noofTSSviolation = 1;
noofBOD5violation = 1;

if not(isempty(Nviolation))
  disp('The maximum effluent total nitrogen level (18 g N/m3) was violated')
  disp(['during ',num2str(min(totalt,length(Nviolation)*sampletime)),' days, i.e. ',num2str(min(100,length(Nviolation)*sampletime/totalt*100)),'% of the operating time.'])
  Nviolationtime=min(totalt,length(Nviolation)*sampletime);
  Nviolationtimepercent=min(100,length(Nviolation)*sampletime/totalt*100);
  for i=2:length(Nviolation)
    if Nviolation(i-1)~=(Nviolation(i)-1)
      noofNviolation = noofNviolation+1;
    end
  end
  disp(['The limit was violated at ',num2str(noofNviolation),' different occasions.'])
  disp(' ')
  output=[output; Nviolationtime; Nviolationtimepercent; noofNviolation];
end

if not(isempty(CODviolation))
  disp('The maximum effluent total COD level (100 g COD/m3) was violated')
  disp(['during ',num2str(min(totalt,length(CODviolation)*sampletime)),' days, i.e. ',num2str(min(100,length(CODviolation)*sampletime/totalt*100)),'% of the operating time.'])
  CODviolationtime=min(totalt,length(CODviolation)*sampletime);
  CODviolationtimepercent=min(100,length(CODviolation)*sampletime/totalt*100);
  for i=2:length(CODviolation)
    if CODviolation(i-1)~=(CODviolation(i)-1)
      noofCODviolation = noofCODviolation+1;
    end
  end
  disp(['The limit was violated at ',num2str(noofCODviolation),' different occasions.'])
  disp(' ')
  output=[output; CODviolationtime; CODviolationtimepercent; noofCODviolation];
end

if not(isempty(SNHviolation))
  disp('The maximum effluent ammonia nitrogen level (4 g N/m3) was violated')
  disp(['during ',num2str(min(totalt,length(SNHviolation)*sampletime)),' days, i.e. ',num2str(min(100,length(SNHviolation)*sampletime/totalt*100)),'% of the operating time.'])
  SNHviolationtime=min(totalt,length(SNHviolation)*sampletime);
  SNHviolationtimepercent=min(100,length(SNHviolation)*sampletime/totalt*100);
  for i=2:length(SNHviolation)
    if SNHviolation(i-1)~=(SNHviolation(i)-1)
      noofSNHviolation = noofSNHviolation+1;
    end
  end
  disp(['The limit was violated at ',num2str(noofSNHviolation),' different occasions.'])
  disp(' ')
  output=[output; SNHviolationtime; SNHviolationtimepercent; noofSNHviolation];
end

if not(isempty(TSSviolation))
  disp('The maximum effluent total suspended solids level (30 g SS/m3) was violated')
  disp(['during ',num2str(min(totalt,length(TSSviolation)*sampletime)),' days, i.e. ',num2str(min(100,length(TSSviolation)*sampletime/totalt*100)),'% of the operating time.'])
  TSSviolationtime=min(totalt,length(TSSviolation)*sampletime);
  TSSviolationtimepercent=min(100,length(TSSviolation)*sampletime/totalt*100);
  for i=2:length(TSSviolation)
    if TSSviolation(i-1)~=(TSSviolation(i)-1)
      noofTSSviolation = noofTSSviolation+1;
    end
  end
  disp(['The limit was violated at ',num2str(noofTSSviolation),' different occasions.'])
  disp(' ')
  output=[output; TSSviolationtime; TSSviolationtimepercent; noofTSSviolation];
end

if not(isempty(BOD5violation))
  disp('The maximum effluent BOD5 level (10 mg/l) was violated')
  disp(['during ',num2str(min(totalt,length(BOD5violation)*sampletime)),' days, i.e. ',num2str(min(100,length(BOD5violation)*sampletime/totalt*100)),'% of the operating time.'])
  BOD5violationtime=min(totalt,length(BOD5violation)*sampletime);
  BOD5violationtimepercent=min(100,length(BOD5violation)*sampletime/totalt*100);
  for i=2:length(BOD5violation)
    if BOD5violation(i-1)~=(BOD5violation(i)-1)
      noofBOD5violation = noofBOD5violation+1;
    end
  end
  disp(['The limit was violated at ',num2str(noofBOD5violation),' different occasions.'])
  disp(' ')
  output=[output; BOD5violationtime; BOD5violationtimepercent; noofBOD5violation];
end


if plotflag==1
    disp(' ')
    disp('Plotting of BSM2 evaluation results has been initiated')
    disp('******************************************************')
    disp(' ')
    movingaveragewindow = 96; % even number
    timeshift = movingaveragewindow/2;
    b = ones(1,movingaveragewindow)./movingaveragewindow;

    figure(1)
    plot(time_eval(1:(end-1)),totalNevec2,'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,totalNevec2);
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    plot([time_eval(1) time_eval(end-1)],[totalNemax totalNemax],'r','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('TN in effluent (g N/m^3)','FontSize',10,'FontWeight','bold')
    title('Effluent total nitrogen (raw and filtered) and limit value','FontSize',10,'FontWeight','bold')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(2)
    plot(time_eval(1:(end-1)),totalCODevec2,'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,totalCODevec2);
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    plot([time_eval(1) time_eval(end-1)],[totalCODemax totalCODemax],'r','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('Total COD in effluent (g COD/m^3)','FontSize',10,'FontWeight','bold')
    title('Effluent total COD (raw and filtered) and limit value','FontSize',10,'FontWeight','bold')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(3)
    plot(time_eval(1:(end-1)),SNHevec2,'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,SNHevec2);
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    plot([time_eval(1) time_eval(end-1)],[SNHemax SNHemax],'r','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('Ammonia in effluent (g N/m^3)','FontSize',10,'FontWeight','bold')
    title('Effluent total ammonia (raw and filtered) and limit value','FontSize',10,'FontWeight','bold')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(4)
    plot(time_eval(1:(end-1)),TSSevec2,'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,TSSevec2);
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    plot([time_eval(1) time_eval(end-1)],[TSSemax TSSemax],'r','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('Suspended solids in effluent (g SS/m^3)','FontSize',10,'FontWeight','bold')
    title('Effluent suspended solids (raw and filtered) and limit value','FontSize',10,'FontWeight','bold')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(5)
    plot(time_eval(1:(end-1)),BOD5evec2,'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,BOD5evec2);
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    plot([time_eval(1) time_eval(end-1)],[BOD5emax BOD5emax],'r','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('BOD5 in effluent (g/m^3)','FontSize',10,'FontWeight','bold')
    title('Effluent BOD5 (raw and filtered) and limit value','FontSize',10,'FontWeight','bold')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(6)
    plot(time_eval(1:(end-1)),EQIvecinst./1000,'b','LineWidth',1)
    hold on;
    filteredout=filter(b,1,EQIvecinst./1000);
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('Instantaneous EQ index (kg poll.units/d)','FontSize',10,'FontWeight','bold')
    title('Effluent Quality Index (raw and filtered)')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(7)
    plot(time_eval(1:(end-1)),TSSsludgeconc.*Qsludgeflow,'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,TSSsludgeconc.*Qsludgeflow);
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('Instantaneous sludge wastage rate (kg SS/d)','FontSize',10,'FontWeight','bold')
    title('Sludge wastage rate (raw and filtered)')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(8)
    plot(time_eval(1:(end-1)),pumpenergyvec,'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,pumpenergyvec);
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('Instantaneous pumping energy (kWh/d)','FontSize',10,'FontWeight','bold')
    title('Pumping energy (raw and filtered)')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(9)
    plot(time_eval(1:(end-1)),airenergyvec,'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,airenergyvec);
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('Instantaneous aeration energy (kWh/d)','FontSize',10,'FontWeight','bold')
    title('Aeration energy (raw and filtered)')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(10)
    plot(time_eval(1:(end-1)),carbonmassvec,'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,carbonmassvec);
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('Instantaneous carbon source addition (kg COD/d)','FontSize',10,'FontWeight','bold')
    title('Carbon source addition (raw and filtered)')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(11)
    plot(time_eval(1:(end-1)),Methaneflowvec,'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,Methaneflowvec);
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('Instantaneous methane production (kg CH_4/d)','FontSize',10,'FontWeight','bold')
    title('Methane production (raw and filtered)')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(12)
    plot(time_eval(1:(end-1)),digesteroutpart(:,51),'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,digesteroutpart(:,51));
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('Instantaneous total gas flow (Nm^3/d)','FontSize',10,'FontWeight','bold')
    title('Total gas flow from AD normalized to P-atm (raw and filtered)')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(13)
    plot(time_eval(1:(end-1)),storagepart(:,22),'b','LineWidth',1)
    hold on
    filteredout=filter(b,1,storagepart(:,22));
    filteredout=filteredout(movingaveragewindow:end);
    plot(time_eval(timeshift:(end-timeshift-1)),filteredout,'g','LineWidth',1.5)
    xlabel('time (days)','FontSize',10,'FontWeight','bold')
    ylabel('Liquid volume (m^3)','FontSize',10,'FontWeight','bold')
    title('Liquid volume in storage tank (raw and filtered)')
    hold off
    xlim([starttime stoptime])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    % Plot of the SNH, TN and TSS curves
    SNHeffsort=sort(SNHevec2);
    TNeffsort=sort(totalNevec2);
    TSSeffsort=sort(TSSevec2);
    n=size(SNHevec2,1);
    xvalues=[1:n].*(100/n);

    figure(14)
    plot(xvalues,SNHeffsort,'b','LineWidth',1)
    hold on
    plot([0 95],[SNHeffprctile SNHeffprctile],'k--','LineWidth',1.5)
    hold on
    plot([95 95],[0 SNHeffprctile],'k--','LineWidth',1.5)
    xlabel('Ordered S_N_H effluent concentrations (%)','FontSize',10,'FontWeight','bold')
    ylabel('S_N_H effluent concentrations (g N/m^3)','FontSize',10,'FontWeight','bold')
    title('Ordered effluent S_N_H concentrations with 95% percentile','FontSize',10,'FontWeight','bold')
    xlim([0 105])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(15)
    plot(xvalues,TNeffsort,'b','LineWidth',1)
    hold on
    plot([0 95],[TNeffprctile TNeffprctile],'k--','LineWidth',1.5)
    hold on
    plot([95 95],[0 TNeffprctile],'k--','LineWidth',1.5)
    xlabel('Ordered TN effluent concentrations (%)','FontSize',10,'FontWeight','bold')
    ylabel('TN effluent concentrations (g N/m^3)','FontSize',10,'FontWeight','bold')
    title('Ordered effluent TN concentrations with 95% percentile','FontSize',10,'FontWeight','bold')
    xlim([0 105])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    figure(16)
    plot(xvalues,TSSeffsort,'b','LineWidth',1)
    hold on
    plot([0 95],[TSSeffprctile TSSeffprctile],'k--','LineWidth',1.5)
    hold on
    plot([95 95],[0 TSSeffprctile],'k--','LineWidth',1.5)
    xlabel('Ordered TSS effluent concentrations (%)','FontSize',10,'FontWeight','bold')
    ylabel('TSS effluent concentrations (g SS/m^3)','FontSize',10,'FontWeight','bold')
    title('Ordered effluent TSS concentrations with 95% percentile','FontSize',10,'FontWeight','bold')
    xlim([0 105])
    set(gca,'LineWidth',1.5,'FontSize',10,'FontWeight','bold')

    disp('Plotting of BSM2 evaluation results has been completed')
    disp('******************************************************')
    disp(' ')

end

% Call the 'fuzzified' expert module to detect settling problems
disp(' ')
disp('Note: Calculation of risk indices may require 15-60 minutes of CPU time.')
yes = input('Do you want to continue? (yes = 1, no = 0)  >> ');
disp(' ')
if yes > 0.5
   disp('Calculation of BSM2 risk indices has been initiated!')
   disp(' ')
   perf_risk_bsm2;
else
   disp('Calculation of BSM2 risk indices has been aborted!')
   disp(' ')
end

stop=clock;
disp('***** Plant evaluation of BSM2 system successfully finished *****')
disp(['End time (hour:min:sec) = ', num2str(round(stop(4:6)))]); %Display simulation stop time
disp(' ')

function [outvector] = changeScalarToVector(invariable,outvecsize)
%Vector to modify variables like Kla1in, carb1in etc to vectors from
%scalars
%% Inputs
%invariable - input variable that needs to be changed, if required
%outvecsize  - Size of the output vector
%outvector - output vector

if size(invariable,1)>1
    outvector=invariable;
else
    outvector=ones(outvecsize).*invariable;
end
end
