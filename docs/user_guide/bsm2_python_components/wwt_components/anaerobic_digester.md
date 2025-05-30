---
hide:
  - toc
---

![Anerobic digester](../../../assets/icons/bsm2python/anerobic-digester.svg){ align=right }

### Introduction and Model

The anaerobic digester is designed to break down organic matter in sewage sludge to produce methane gas through four key stages: hydrolysis, acidogenesis, acetogenesis and methanogenesis. Most of this processes rely on microorganisms that metabolize substrates in the absence of oxygen, typically at mesophilic temperature range <br> (20-45&nbsp;°C).

The implementation is based on the Anaerobic Digestion Model No. 1 (ADM1) by Batstone et al. (2002), with some deviations from the original model due to computational issues and to ensure consistency with BSM2. ADM1 represents the anaerobic digester as two separate volumes: one for the liquid phase and one for the gas phase. Both phases are assumed to be completely mixed (CSTR).

The model incorporates 24 relevant [components](#components), which are categorized into insoluble components (X) and soluble components (S). In the liquid phase these components are transformed due to 19 [biochemical processes](#biochemical-process-rates) that can be described by four key processes:

- Disintegration (more complex hydrolysis steps)
- Hydrolysis
- Substrate uptake / biomass growth
- Substrate decay / biomass decay

The uptake processes depend on the pH value, which is accounted for using [inhibition functions](#process-inhibition), while the calculation of the pH value relies heavily on [acid-base processes](#acid-base-rates). The [gas transfer processes](#gas-transfer-rates) describe the transition of dissolved gas from the liquid phase to the gas phase.

In the differential mass balance for a [soluble (i=1-12)](#differential-mass-balance-for-soluble-components) or [particulate (i=13-24)](#differential-mass-balance-for-particulate-components), the reaction term for biochemical processes is expressed as the sum across all processes $j$, which sums up the products of the [stoichiometric coefficients](#stoichiometric-coefficients-nu_ij) $\nu_{ij}$ and the process rates $\rho_j$. For the soluble components $S_{h2}$, $S_{co2}$ and $S_{ch4}$ the gas transfer rate $\rho_{T,i}$ is included. 

The determination of the pH value involves a differential mass balance for [cations](#differential-mass-balance-for-cations) and [anions](#differential-mass-balance-for-anions) (i=4-7, 10-11), along with [differential equations for ion states](#differential-equations-for-ion-states) that incorporate the acid-base process rates $\rho_{A,i}$. 

For the gas phase there are differential mass balances for [hydrogen gas](#differential-mass-balance-for-hydrogen), [methane gas](#differential-mass-balance-for-methane) and [carbon dioxide gas](#differential-mass-balance-for-carbon-dioxide), that use the gas transfer rates $\rho_{T,i}$. For dynamic state modeling, these equations are solved using numerical integration techniques.


### Equations

#### Components

| $i$ | Component                       | Symbol    | Unit                 |
| --- | ------------------------------- | --------- | -------------------- |
| 1   | Monosaccharides                 | $S_{su}$  | kg(COD)$\cdot$m^-3^  |
| 2   | Amino acids                     | $S_{aa}$  | kg(COD)$\cdot$m^-3^  |
| 3   | Long chain fatty acids (LCFA)   | $S_{fa}$  | kg(COD)$\cdot$m^-3^  |
| 4   | Total valerate                  | $S_{va}$  | kg(COD)$\cdot$m^-3^  |
| 5   | Total butyrate                  | $S_{bu}$  | kg(COD)$\cdot$m^-3^  |
| 6   | Total propionate                | $S_{pro}$ | kg(COD)$\cdot$m^-3^  |
| 7   | Total acetate                   | $S_{ac}$  | kg(COD)$\cdot$m^-3^  |
| 8   | Hydrogen gas                    | $S_{h2}$  | kg(COD)$\cdot$m^-3^  |
| 9   | Methane gas                     | $S_{ch4}$ | kg(COD)$\cdot$m^-3^  |
| 10  | Inorganic carbon                | $S_{IC}$  | kmol(C)$\cdot$m^-3^ |
| 11  | Inorganic nitrogen              | $S_{IN}$  | kmol(N)$\cdot$m^-3^ |
| 12  | Soluble inerts                  | $S_I$     | kg(COD)$\cdot$m^-3^  |
| 13  | Composites                      | $X_c$     | kg(COD)$\cdot$m^-3^  |
| 14  | Carbohydrates                   | $X_{ch}$  | kg(COD)$\cdot$m^-3^  |
| 15  | Proteins                        | $X_{pr}$  | kg(COD)$\cdot$m^-3^  |
| 16  | Lipids                          | $X_{li}$  | kg(COD)$\cdot$m^-3^  |
| 17  | Sugar degraders                 | $X_{su}$  | kg(COD)$\cdot$m^-3^  |
| 18  | Amino acid degraders            | $X_{aa}$  | kg(COD)$\cdot$m^-3^  |
| 19  | LCFA degraders                  | $X_{fa}$  | kg(COD)$\cdot$m^-3^  |
| 20  | Valerate and butyrate degraders | $X_{c4}$  | kg(COD)$\cdot$m^-3^  |
| 21  | Propionate degraders            | $X_{pro}$ | kg(COD)$\cdot$m^-3^  |
| 22  | Acetate degraders               | $X_{ac}$  | kg(COD)$\cdot$m^-3^  |
| 23  | Hydrogen degraders              | $X_{h2}$  | kg(COD)$\cdot$m^-3^  |
| 24  | Particulate inerts              | $X_I$     | kg(COD)$\cdot$m^-3^  |


**Process rates**

#### Biochemical process rates

| $\rho_j$  | Biochemical process rate [kg(COD)$\cdot$m^-3^d^-1^] | Equation            |
| --------- | --------------------------------------- | ------------------- |
| $\rho_1$  | Disintegration                          | $k_{dis}X_c$        |
| $\rho_2$  | Hydrolysis of carbohydrates             | $k_{hyd,ch}X_{ch}$  |
| $\rho_3$  | Hydrolysis of proteins                  | $k_{hyd,pr}X_{pr}$  |
| $\rho_4$  | Hydrolysis of lipids                    | $k_{hyd,li}X_{li}$  |
| $\rho_5$  | Uptake of sugars                        | $k_{m,su} \left( \frac{S_{su}}{K_{S,su} + S_{su}} \right) X_{su}I_5$ |
| $\rho_6$  | Uptake of amino acids                   | $k_{m,aa} \left( \frac{S_{aa}}{K_{S,aa} + S_{aa}} \right) X_{aa}I_6$ |
| $\rho_7$  | Uptake of LCFA                          | $k_{m,fa} \left( \frac{S_{fa}}{K_{S,fa} + S_{fa}} \right) X_{fa}I_7$ |
| $\rho_8$  | Uptake of valerate                      | $k_{m,c4} \left( \frac{S_{va}}{K_{S,c4} + S_{va}} \right) X_{c4} \left( \frac{S_{va}}{S_{bu} + S_{va}} \right) I_8$ |
| $\rho_9$  | Uptake of butyrate                      | $k_{m,c4} \left( \frac{S_{bu}}{K_{S,c4} + S_{bu}} \right) X_{c4} \left( \frac{S_{bu}}{S_{va} + S_{bu}} \right) I_9$ |
| $\rho_{10}$ | Uptake of propionate                  | $k_{m,pro} \left( \frac{S_{pro}}{K_{S,pro} + S_{pro}} \right) X_{pro} I_{10}$ |
| $\rho_{11}$ | Uptake of acetate                     | $k_{m,ac} \left( \frac{S_{ac}}{K_{S,ac} + S_{ac}} \right) X_{ac} I_{11}$ |
| $\rho_{12}$ | Uptake of hydrogen                    | $k_{m,h2} \left( \frac{S_{h2}}{K_{S,h2} + S_{h2}} \right) X_{h2} I_{12}$ |
| $\rho_{13}$ | Decay of $X_{su}$                     | $k_{dec,Xsu}X_{su}$ |
| $\rho_{14}$ | Decay of $X_{aa}$                     | $k_{dec,Xaa}X_{aa}$ |
| $\rho_{15}$ | Decay of $X_{fa}$                     | $k_{dec,Xfa}X_{fa}$ |
| $\rho_{16}$ | Decay of $X_{c4}$                     | $k_{dec,Xc4}X_{c4}$ |
| $\rho_{17}$ | Decay of $X_{pro}$                    | $k_{dec,Xpro}X_{pro}$ |
| $\rho_{18}$ | Decay of $X_{ac}$                     | $k_{dec,Xac}X_{ac}$ |
| $\rho_{19}$ | Decay of $X_{h2}$                     | $k_{dec,Xh2}X_{h2}$ |


**Biochemical process rate parameters**

| Symbol        | Description | Unit  |
| ------------- | ----------- | ----- |
| $k_{dis}$     | Disintegration rate | d^-1^ |
| $k_{hyd,ch}$  | Hydrolysis rate of X~ch~ | d^-1^ |
| $k_{hyd,pr}$  | Hydrolysis rate of X~pr~ | d^-1^ |
| $k_{hyd,li}$  | Hydrolysis rate of X~li~ | d^-1^ |
| $k_{m,proc}$  | Monod maximum specific uptake rate for process *proc* | d^-1^ |
| $k_{dec,bac}$ | Decay rate for bacteria of type *bac* | d^-1^ |
| $K_{S}$       | Monod half saturation constant  | kg(COD)$\cdot$m^-3^ |


#### Process inhibition

| $I_i$ | Process inhibition due to pH [-] | Equation |
| ----- | -------------------------------- | -------- |
| $I_5 = I_6$ | Process inhibition for $\rho_5$ and $\rho_6$ | $I_{pH,aa} \left( \frac{1}{1 + K_{S,IN} / S_{IN}} \right)$         |
| $I_7$ | Process inhibition for $\rho_7$ | $I_{pH,aa} \left( \frac{1}{1 + K_{S,IN} / S_{IN}} \right) \left( \frac{1}{1 + S_{h2} / K_{I,h2,fa}} \right)$  |
| $I_8 = I_9$ | Process inhibition for $\rho_8$ and $\rho_9$ | $I_{pH,aa} \left( \frac{1}{1 + K_{S,IN} / S_{IN}} \right) \left( \frac{1}{1 + S_{h2} / K_{I,h2,c4}} \right)$  |
| $I_{10}$ | Process inhibition for $\rho_{10}$ | $I_{pH,aa} \left( \frac{1}{1 + K_{S,IN} / S_{IN}} \right) \left( \frac{1}{1 + S_{h2} / K_{I,h2,pro}} \right)$  |
| $I_{11}$ | Process inhibition for $\rho_{11}$ | $I_{pH,ac} \left( \frac{1}{1 + K_{S,IN} / S_{IN}} \right) \left( \frac{1}{1 + S_{nh3} / K_{I,nh3}} \right)$  |
| $I_{12}$ | Process inhibition for $\rho_{12}$ | $I_{pH,h2} \left( \frac{1}{1 + K_{S,IN} / S_{IN}} \right)$  |

$$
I_{pH,aa} = \frac{K_{pH}^{n_{aa}}}{S_{H^+}^{n_{aa}} + K_{pH}^{n_{aa}}} \quad \text{with} \quad K_{pH} = 10^{-\frac{pH_{LL,aa}+pH_{UL,aa}}{2}} \quad \text{and} \quad n_{aa} = \frac{3.0}{pH_{UL,aa} - pH_{LL,aa}}
$$

$$
I_{pH,ac} = \frac{K_{pH}^{n_{ac}}}{S_{H^+}^{n_{ac}} + K_{pH}^{n_{ac}}} \quad \text{with} \quad K_{pH} = 10^{-\frac{pH_{LL,ac}+pH_{UL,ac}}{2}} \quad \text{and} \quad n_{ac} = \frac{3.0}{pH_{UL,ac} - pH_{LL,ac}}
$$

$$
I_{pH,h2} = \frac{K_{pH}^{n_{h2}}}{S_{H^+}^{n_{h2}} + K_{pH}^{n_{h2}}} \quad \text{with} \quad K_{pH} = 10^{-\frac{pH_{LL,h2}+pH_{UL,h2}}{2}} \quad \text{and} \quad n_{h2} = \frac{3.0}{pH_{UL,h2} - pH_{LL,h2}}
$$


**Process inhibition parameters**

| Symbol        | Description | Unit  |
| ------------- | ----------- | ----- |
| $K_{S,IN}$     | Inhibition parameter for inorganic nitrogen | kmol(N)$\cdot$m^-3^ |
| $K_{I,h2,fa}$     | 50% inhibitory concentration of inhibitor H~2~ on LCFA uptake process | kg(COD)$\cdot$m^-3^ |
| $K_{I,h2,c4}$     | 50% inhibitory concentration of inhibitor H~2~ on valerate and butyrate uptake process | kg(COD)$\cdot$m^-3^ |
| $K_{I,h2,pro}$     | 50% inhibitory concentration of inhibitor H~2~ on propionate uptake process | kg(COD)$\cdot$m^-3^ |
| $K_{I,nh3}$     | 50% inhibitory concentration of inhibitor NH~3~ on acetate uptake process | kmol$\cdot$m^-3^ |
| $S_{nh3}$     | Molar concentration of ammonia | kmol$\cdot$m^-3^ |
| $pH_{LL,aa}$     | Lower limit of pH for uptake rate of amino acids | - |
| $pH_{UL,aa}$     | Upper limit of pH for uptake rate of amino acids | - |
| $pH_{LL,ac}$     | Lower limit of pH for uptake rate of acetate | - |
| $pH_{UL,ac}$     | Upper limit of pH for uptake rate of acetate | - |
| $pH_{LL,h2}$     | Lower limit of pH for uptake rate of hydrogen | - |
| $pH_{UL,h2}$     | Upper limit of pH for uptake rate of hydrogen | - |


#### Acid-base rates

| $\rho_{A,i}$  | Acid-base rate [kg(COD)$\cdot$m^-3^d^-1^] | Equation            |
| --------- | --------------------------------------- | ------------------- |
| $\rho_{A,4}$  | Acid-base equilibrium of valerate   | $k_{A,Bva} \left( S_{va^-} (K_{a,va}+S_{H^+}) -K_{a,va}S_{va} \right)$        |
| $\rho_{A,5}$  | Acid-base equilibrium of butyrate    | $k_{A,Bbu} \left( S_{bu^-} (K_{a,bu}+S_{H^+}) -K_{a,bu}S_{bu} \right)$  |
| $\rho_{A,6}$  | Acid-base equilibrium of propionate      | $k_{A,Bpro} \left( S_{pro^-} (K_{a,pro}+S_{H^+}) -K_{a,pro}S_{pro} \right)$  |
| $\rho_{A,7}$  | Acid-base equilibrium of acetate           | $k_{A,Bac} \left( S_{ac^-} (K_{a,ac}+S_{H^+}) -K_{a,ac}S_{ac} \right)$  |
| $\rho_{A,10}$  | Acid-base equilibrium of inorganic carbon       | $k_{A,Bco2} \left( S_{hco3^-} (K_{a,co2}+S_{H^+}) -K_{a,co2}S_{IC} \right)$ |
| $\rho_{A,11}$  | Acid-base equilibrium of inorganic nitrogen   | $k_{A,BIN} \left( S_{nh3} (K_{a,IN}+S_{H^+}) -K_{a,IN}S_{IN} \right)$ |

**Acid-base rate parameters**

| Symbol        | Description | Unit  |
| ------------- | ----------- | ----- |
| $k_{A,Bsub}$     | Acid-base kinetic parameter for substance *sub* | m^3^$\cdot$kmol^-1^$\cdot$d^-1^ |
| $K_{a,acid}$     | Acid-base equilibrium constant for *acid* | kmol$\cdot$m^-3^ |
| $S_{va}$  | Total valerate, sum of acid-base pair ($S_{va}=S_{va^-}+S_{hva}$) | kg(COD)$\cdot$m^-3^ |
| $S_{bu}$  | Total butyrate, sum of acid-base pair ($S_{bu}=S_{bu^-}+S_{hbu}$) | kg(COD)$\cdot$m^-3^ |
| $S_{pro}$  | Total propionate, sum of acid-base pair ($S_{pro}=S_{pro^-}+S_{hpro}$) | kg(COD)$\cdot$m^-3^ |
| $S_{ac}$  | Total acetate, sum of acid-base pair ($S_{ac}=S_{ac^-}+S_{hac}$) | kg(COD)$\cdot$m^-3^ |
| $S_{IC}$  | Inorganic carbon, sum of acid-base pair ($S_{IC}=S_{hco3^-}+S_{h2co3}$) | kmol(C)$\cdot$m^-3^ |
| $S_{IN}$  | Inorganic nitrogen, sum of acid-base pair ($S_{IN}=S_{nh3}+S_{nh4^+}$) | kmol(N)$\cdot$m^-3^ |
| $S_{H^+}$     | Molar concentration of hydrogen | kmol$\cdot$m^-3^ |


#### Gas transfer rates

| $\rho_{T,i}$  | Gas transfer rate [kmol$\cdot$m^-3^d^-1^] | Equation            |
| --------- | --------------------------------------- | ------------------- |
| $\rho_{T,8}$  | Transfer rate of hydrogen   | $K_{L}a_{h2}(S_{h2}-16 \cdot K_{H,h2}p_{gas,h2})$        |
| $\rho_{T,9}$  | Transfer rate of methane    | $K_{L}a_{ch4}(S_{ch4}-64 \cdot K_{H,ch4}p_{gas,ch4})$  |
| $\rho_{T,10}$  | Transfer rate of carbon dioxide      | $K_{L}a_{co2}(S_{co_2}-K_{H,co2}p_{gas,co2})$  |


**Gas transfer rate parameters**

| Symbol        | Description | Unit  |
| ------------- | ----------- | ----- |
| $K_{L}a_{gas}$     | Transfer coefficient of *gas* | d^-1^ |
| $K_{H,h2}$     | Henry’s law coefficient for hydrogen | kmol$\cdot$m^-3^$\cdot$bar^-1^ |
| $K_{H,ch4}$     | Henry’s law coefficient for methane | kmol$\cdot$m^-3^$\cdot$bar^-1^ |
| $K_{H,co2}$     | Henry’s law coefficient for carbon dioxide | kmol$\cdot$m^-3^$\cdot$bar^-1^ |
| $p_{gas,h2}$     | Partial pressure of hydrogen | bar |
| $p_{gas,ch4}$     | Partial pressure of methane | bar |
| $p_{gas,co2}$     | Partial pressure of carbon dioxide | bar |
| $S_{co2}$  | Molar concentration of carbon dioxide | kmol$\cdot$m^-3^ |


#### Liquid phase equations

##### Differential mass balance for soluble components:

$$
\frac{dS_i}{dt} = \frac{Q}{V_{liq}} \left( S_{i,in} - S_{i,out} \right) + \left( \sum_{j} \nu_{ij}\rho_j \right) - \rho_{T,i}
$$

##### Differential mass balance for particulate components:

$$
\frac{dX_i}{dt} = \frac{Q}{V_{liq}} \left( X_{i,in} - X_{i,out} \right) + \sum_{j} \nu_{ij}\rho_j
$$

##### Differential mass balance for cations:

$$
\frac{dS_{i,cat^+}}{dt} = \frac{Q}{V_{liq}} \left( S_{i,cat^+,in} - S_{i,cat^+,out} \right)
$$

##### Differential mass balance for anions:

$$
\frac{dS_{i,an^-}}{dt} = \frac{Q}{V_{liq}} \left( S_{i,an^-,in} - S_{i,an^-,out} \right)
$$

##### Differential equations for ion states:

$$
\frac{dS_{va^-}}{dt} = - \rho_{A,4}
$$

$$
\frac{dS_{bu^-}}{dt} = - \rho_{A,5}
$$

$$
\frac{dS_{pro^-}}{dt} = - \rho_{A,6}
$$

$$
\frac{dS_{ac^-}}{dt} = - \rho_{A,7}
$$

$$
\frac{dS_{hco3^-}}{dt} = - \rho_{A,10}
$$

$$
\frac{dS_{nh3}}{dt} = - \rho_{A,11}
$$


#### Stoichiometric coefficients $\nu_{ij}$

$$
\begin{array}{c|ccccccccccccccccccccccccc}
\text{component} \, i \rightarrow & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 & 11 & 12 & 13 & 14 & 15 & 16 & 17 & 18 & 19 & 20 & 21 & 22 & 23 & 24 \\
\text{process} \, j \downarrow & S_{su} & S_{aa} & S_{fa} & S_{va} & S_{bu} & S_{pro} & S_{ac} & S_{h2} & S_{ch4} & S_{IC} & S_{IN} & S_I & X_c & X_{ch} & X_{pr} & X_{li} & X_{su} & X_{aa} & X_{fa} & X_{c4} & X_{pro} & X_{ac} & X_{h2} & X_I \\ \hline
1 &  &  &  &  &  &  &  &  &  & \displaystyle -\sum_{i=1-9,12-24} C_i\nu_{i,1} & (N_{xc}-f_{xi,xc}N_I-f_{si,xc}N_I-f_{pr,xc}N_{aa}) & f_{S_I,xc} & -1 & f_{ch,xc} & f_{pr,xc} & f_{li,xc} &  &  &  &  &  &  &  & f_{X_I,xc} \\
2 & 1 &  &  &  &  &  &  &  &  & \displaystyle -\sum_{i=1-9,11-24} C_i\nu_{i,2} &  &  &  & -1 &  &  &  &  &  &  &  &  &  &  \\
3 &  & 1 &  &  &  &  &  &  &  & \displaystyle -\sum_{i=1-9,11-24} C_i\nu_{i,3} &  &  &  &  & -1 &  &  &  &  &  &  &  &  &  \\
4 & 1-f_{fa,li} &  & f_{fa,li} &  &  &  &  &  &  & \displaystyle -\sum_{i=1-9,11-24} C_i\nu_{i,4} &  &  &  &  &  & -1 &  &  &  &  &  &  &  &  \\
5 & -1 &  &  &  & (1-Y_{su})f_{bu,su} & (1-Y_{su})f_{pro,su} & (1-Y_{su})f_{ac,su} & (1-Y_{su})f_{h2,su} &  & \displaystyle -\sum_{i=1-9,11-24 \setminus \{8\}} C_i\nu_{i,5} & -(Y_{su})N_{bac} &  &  &  &  &  & Y_{su} &  &  &  &  &  &  &  \\
6 &  & -1 &  & (1-Y_{aa})f_{va,aa} & (1-Y_{aa})f_{bu,aa} & (1-Y_{aa})f_{pro,aa} & (1-Y_{aa})f_{ac,aa} & (1-Y_{aa})f_{h2,aa} &  & \displaystyle -\sum_{i=1-9,11-24 \setminus \{8\}} C_i\nu_{i,6} & N_{aa}-(Y_{aa})N_{bac} &  &  &  &  &  &  & Y_{aa} &  &  &  &  &  &  \\
7 &  &  & -1 &  &  &  & (1-Y_{fa})0.7 & (1-Y_{fa})0.3 &  & \displaystyle -\sum_{i=1-9,11-24 \setminus \{8\}} C_i\nu_{i,7} & -(Y_{fa})N_{bac} &  &  &  &  &  &  &  & Y_{fa} &  &  &  &  &  \\
8 &  &  &  & -1 &  & (1-Y_{c4})0.54 & (1-Y_{c4})0.31 & (1-Y_{c4})0.15 &  & \displaystyle -\sum_{i=1-9,11-24 \setminus \{8\}} C_i\nu_{i,8} & -(Y_{c4})N_{bac} &  &  &  &  &  &  &  &  & Y_{c4} &  &  &  &  \\
9 &  &  &  &  & -1 &  & (1-Y_{c4})0.8 & (1-Y_{c4})0.2 &  & \displaystyle -\sum_{i=1-9,11-24 \setminus \{8\}} C_i\nu_{i,9} & -(Y_{c4})N_{bac} &  &  &  &  &  &  &  &  & Y_{c4} &  &  &  &  \\
10 &  &  &  &  &  & -1 & (1-Y_{pro})0.57 & (1-Y_{pro})0.43 &  & \displaystyle -\sum_{i=1-9,11-24 \setminus \{8\}} C_i\nu_{i,10} & -(Y_{pro})N_{bac} &  &  &  &  &  &  &  &  &  & Y_{pro} &  &  &  \\
11 &  &  &  &  &  &  & -1 &  & (1-Y_{ac}) & \displaystyle -\sum_{i=1-9,11-24} C_i\nu_{i,11} & -(Y_{ac})N_{bac} &  &  &  &  &  &  &  &  &  &  & Y_{ac} &  &  \\
12 &  &  &  &  &  &  &  & -1 & (1-Y_{h2}) & \displaystyle -\sum_{i=1-9,11-24 \setminus \{8\}} C_i\nu_{i,12} & -(Y_{h2})N_{bac} &  &  &  &  &  &  &  &  &  &  &  & Y_{h2} &  \\
13 &  &  &  &  &  &  &  &  &  & \displaystyle -\sum_{i=1-9,11-24} C_i\nu_{i,13} & N_{bac}-N_{xc} &  & 1 &  &  &  & -1 &  &  &  &  &  &  &  \\
14 &  &  &  &  &  &  &  &  &  & \displaystyle -\sum_{i=1-9,11-24} C_i\nu_{i,14} & N_{bac}-N_{xc} &  & 1 &  &  &  &  & -1 &  &  &  &  &  &  \\
15 &  &  &  &  &  &  &  &  &  & \displaystyle -\sum_{i=1-9,11-24} C_i\nu_{i,15} & N_{bac}-N_{xc} &  & 1 &  &  &  &  &  & -1 &  &  &  &  &  \\
16 &  &  &  &  &  &  &  &  &  & \displaystyle -\sum_{i=1-9,11-24} C_i\nu_{i,16} & N_{bac}-N_{xc} &  & 1 &  &  &  &  &  &  & -1 &  &  &  &  \\
17 &  &  &  &  &  &  &  &  &  & \displaystyle -\sum_{i=1-9,11-24} C_i\nu_{i,17} & N_{bac}-N_{xc} &  & 1 &  &  &  &  &  &  &  & -1 &  &  &  \\
18 &  &  &  &  &  &  &  &  &  & \displaystyle -\sum_{i=1-9,11-24} C_i\nu_{i,18} & N_{bac}-N_{xc} &  & 1 &  &  &  &  &  &  &  &  & -1 &  &  \\
19 &  &  &  &  &  &  &  &  &  & \displaystyle -\sum_{i=1-9,11-24} C_i\nu_{i,19} & N_{bac}-N_{xc} &  & 1 &  &  &  &  &  &  &  &  &  & -1 &  \\
\end{array}
$$


**Stoichiometric parameters**

| Symbol   | Description              | Unit                      |
| -------- | ----------------------------- | --------------- |
| $f_{fa,li}$    | Yield (catabolism only) of S~fa~ on X~li~ | - |
| $f_{va,aa}$    | Yield (catabolism only) of S~va~ on S~aa~ | - |
| $f_{bu,su}$    | Yield (catabolism only) of S~bu~ on S~su~ | - |
| $f_{bu,aa}$ | Yield (catabolism only) of S~bu~ on S~aa~ | - |
| $f_{pro,su}$ | Yield (catabolism only) of S~pro~ on S~su~ | - |
| $f_{pro,aa}$ | Yield (catabolism only) of S~pro~ on S~aa~ | - |
| $f_{ac,su}$ | Yield (catabolism only) of S~ac~ on S~su~ | - |
| $f_{ac,aa}$ | Yield (catabolism only) of S~ac~ on S~aa~ | - |
| $f_{h2,su}$ | Yield (catabolism only) of S~h2~ on S~su~ | - |
| $f_{h2,aa}$ | Yield (catabolism only) of S~h2~ on S~aa~ | - |
| $f_{S_I,xc}$ | Fraction of composites to S~I~ by disintegration | - |
| $f_{ch,xc}$ | Fraction of composites to X~ch~ by disintegration | - |
| $f_{pr,xc}$ | Fraction of composites to X~pr~ by disintegration | - |
| $f_{li,xc}$ | Fraction of composites to X~li~ by disintegration | - |
| $f_{X_I,xc}$ | Fraction of composites to X~I~ by disintegration | - |
| $Y_{su}$ | Yield of biomass, sugar degraders | kg(COD)$\cdot$(kg(COD))^-1^ |
| $Y_{aa}$ | Yield of biomass, amino acid degraders | kg(COD)$\cdot$(kg(COD))^-1^ |
| $Y_{fa}$ | Yield of biomass, long chain fatty acid degraders | kg(COD)$\cdot$(kg(COD))^-1^ |
| $Y_{c4}$ | Yield of biomass, valerate and butyrate degraders | kg(COD)$\cdot$(kg(COD))^-1^ |
| $Y_{pro}$ | Yield of biomass, protein degraders | kg(COD)$\cdot$(kg(COD))^-1^ |
| $Y_{ac}$ | Yield of biomass, acetate degraders | kg(COD)$\cdot$(kg(COD))^-1^ |
| $Y_{h2}$ | Yield of biomass, hydrogen degraders | kg(COD)$\cdot$(kg(COD))^-1^ |
| $N_{bac}$ | Nitrogen content of biomass | kmol(N)$\cdot$(kg(COD))^-1^ |
| $C_i$ | Carbon content of component $i$ | kmol(C)$\cdot$(kg(COD))^-1^ |


#### Gas phase equations

##### Differential mass balance for hydrogen:

$$
\frac{dS_{gas,h2}}{dt} = -\frac{S_{gas,h2} Q_{gas}}{V_{gas}} + \rho_{T,8} \frac{V_{liq}}{V_{gas}}
$$

##### Differential mass balance for methane:

$$
\frac{dS_{gas,ch4}}{dt} = -\frac{S_{gas,ch4} Q_{gas}}{V_{gas}} + \rho_{T,9} \frac{V_{liq}}{V_{gas}}
$$

##### Differential mass balance for carbon dioxide:

$$
\frac{dS_{gas,co2}}{dt} = -\frac{S_{gas,co2} Q_{gas}}{V_{gas}} + \rho_{T,10} \frac{V_{liq}}{V_{gas}}
$$


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [adm1_bsm2](/reference/bsm2_python/bsm2/adm1_bsm2)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [adm1init_bsm2](/reference/bsm2_python/bsm2/init/adm1init_bsm2)

[^1]: [Benchmarking of Control Strategies for Wastewater Treatment Plants](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf), chap. 4.2.1 Anaerobic Digestion Model No. 1
[^2]: [Benchmark Simulation Model no. 2 (BSM2)](http://iwa-mia.org/wp-content/uploads/2022/09/TR3_BSM_TG_Tech_Report_no_3_BSM2_General_Description.pdf), chap. 2. Modeling of the activated sludge section
[^3]: [Anaerobic Digestion Model No. 1, Batstone et al. (2002)](https://www.researchgate.net/publication/11198259_Anaerobic_digestion_model_No_1_ADM1)
