---
hide:
  - toc
---

![Activated sludge reactor](../../assets/icons/bsm2python/activated-sludge-reactor.svg){ align=right }

### Introduction and Model

The activated sludge reactor is designed to remove organic matter and nutrients from wastewater through processes such as carbon oxidation, nitrification and denitrification. This treatment relies on microorganisms, which are supplied with oxygen in an aerated tank. The implementation is based on the Activated Sludge Model No. 1 (ASM1) by Henze et al. (1987). ASM1 represents the activated sludge reactor as a continuous stirred tank reactor (CSTR) that is assumed to be completely mixed. The oxygen transfer provided by the aeration equipment is defined by the mass transfer coefficient K~L~a. Additionally, it is possible to maintain a fixed dissolved oxygen (DO) concentration in the reactor using an aeration controller.

The model incorporates 13 relevant [components](#components), which are categorized into insoluble components (X) and soluble components (S). The transformation of these components is controlled by eight fundamental [process rate equations](#process-rates) that describe four key processes:

- the growth of biomass
- the decay of biomass
- the ammonification of organic nitrogen
- the 'hydrolysis' of particulate organics trapped within the biofloc

The reaction rate for a component $i$ is then described by the [conversation rate equation](#conversion-rate), which sums up the products of the [stoichiometric coefficients](#stoichiometric-coefficients-nu_ij) $\nu_{ij}$ and the process rates $\rho_j$ across all processes $j$. For dynamic state modeling, these equations are expressed as a set of coupled ordinary differential equations, which are solved using numerical integration techniques.

ASM1 also supports connecting multiple reactors with different parameters in series, allowing the simulation of distinct reactor zones (e.g. anoxic denitrification).


### Equations

#### Components

| $i$ | Component                                       | Symbol    | Unit                |
| --  | ----------------------------------------------  | --------- | ------------------- |
| 1   | Soluble inert organic matter                    | $S_I$     | g(COD)$\cdot$m^-3^  |
| 2   | Readily biodegradable substrate                 | $S_S$     | g(COD)$\cdot$m^-3^  |
| 3   | Particulate inert organic matter                | $X_I$     | g(COD)$\cdot$m^-3^  |
| 4   | Slowly biodegradable substrate                  | $X_S$     | g(COD)$\cdot$m^-3^  |
| 5   | Active heterotrophic biomass                    | $X_{B,H}$ | g(COD)$\cdot$m^-3^  |
| 6   | Active autotrophic biomass                      | $X_{B,A}$ | g(COD)$\cdot$m^-3^  |
| 7   | Particulate products arising from biomass decay | $X_P$     | g(COD)$\cdot$m^-3^  |
| 8   | Dissolved oxygen                                | $S_O$     | g(O~2~)$\cdot$m^-3^ |
| 9   | Nitrate and nitrite nitrogen                    | $S_{NO}$  | g(N)$\cdot$m^-3^    |
| 10  | Ammonium plus ammonia nitrogen                  | $S_{NH}$  | g(N)$\cdot$m^-3^    |
| 11  | Soluble biodegradable organic nitrogen          | $S_{ND}$  | g(N)$\cdot$m^-3^    |
| 12  | Particulate biodegradable organic nitrogen      | $X_{ND}$  | g(N)$\cdot$m^-3^    |
| 13  | Alkalinity                                      | $S_{ALK}$ | mol(HCO$_3^-$)$\cdot$m^-3^   |


#### Process rates

| $\rho_j$ | Process rate [g(COD)$\cdot$m^-3^$\cdot$d^-1^] | Equation  |
| -------- | --------------------------------------------- | --------- |
| $\rho_1$ | Aerobic growth of heterotrophs                | $\hat \mu_H \left( \frac{S_S}{K_S + S_S} \right) \left( \frac{S_O}{K_{O,H} + S_O} \right) X_{B,H}$ |
| $\rho_2$ | Anoxic growth of heterotrophs                 | $\hat \mu_H \left( \frac{S_S}{K_S + S_S} \right) \left( \frac{K_{O,H}}{K_{O,H} + S_O} \right) \left( \frac{S_{NO}}{K_{NO} + S_{NO}} \right) \eta_g X_{B,H}$     |
| $\rho_3$ | Aerobic growth of autotrophs                  | $\hat \mu_A \left( \frac{S_{NH}}{K_{NH} + S_{NH}} \right) \left( \frac{S_O}{K_{O,A} + S_O} \right) X_{B,A}$ |
| $\rho_4$ | 'Decay' of heterotrophs                       | $b_H X_{B,H}$ |
| $\rho_5$ | 'Decay' of autotrophs                         | $b_A X_{B,A}$ |
| $\rho_6$ | Ammonification of soluble organic nitrogen    | $k_a S_{ND} X_{B,H}$ |
| $\rho_7$ | 'Hydrolysis' of entrapped organics            | $k_h \frac{X_S / X_{B,H}}{K_X + (X_S / X_{B,H})} \left[ \left( \frac{S_O}{K_{O,H} + S_O} \right) + \eta_h \left( \frac{K_{O,H}}{K_{O,H} + S_O} \right) \left( \frac{S_{NO}}{K_{NO} + S_{NO}} \right) \right] X_{B,H}$ |
| $\rho_8$ | 'Hydrolysis' of entrapped organic nitrogen    | $\rho_7 \cdot (X_{ND} / X_S)$ |


**Process rate parameters**

| Symbol       | Description | Unit  |
| ------------ | ----------- | ----- |
| $\hat \mu_H$ | Maximum heterotrophic growth rate | d^-1^ |
| $\hat \mu_A$ | Maximum autotrophic growth rate | d^-1^ |
| $b_H$ | Heterotrophic decay rate | d^-1^ |
| $b_A$ | Autotrophic decay rate | d^-1^ |
| $K_S$ | Substrate half-saturation coefficient for heterotrophic growth | g(COD)$\cdot$m^-3^ |
| $K_{O,H}$ | Oxygen half-saturation coefficient for heterotrophic growth | g(O~2~)$\cdot$m^-3^ |
| $K_{NO}$ | Nitrate half-saturation coefficient for anoxic heterotrophic growth | g(N)$\cdot$m^-3^ |
| $K_{NH}$ | Ammonia half-saturation coefficient for autotrophic growth | g(N)$\cdot$m^-3^ |
| $K_{O,A}$ | Oxygen half-saturation coefficient for autotrophic growth | g(O~2~)$\cdot$m^-3^ |
| $K_X$ | Particulate substrate half-saturation coefficient for hydrolysis | g(COD)$\cdot$(g(COD))^-1^ |
| $k_a$ | Ammonification rate | m^3^$\cdot$(g(COD))^-1^$\cdot$d^-1^ |
| $k_h$ | Maximum specific hydrolysis rate | g(COD)$\cdot$(g(COD))^-1^$\cdot$d^-1^ |
| $\eta_g$ | Anoxic growth rate correction factor | - |
| $\eta_h$ | Anoxic hydrolysis rate correction factor | - |


#### Conversion rate

$$
r_i = \sum_j \nu_{ij}\rho_j
$$

#### Stoichiometric coefficients $\nu_{ij}$

$$
\begin{array}{c|ccccccccccccc}
\text{component} \, i \rightarrow & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 & 11 & 12 & 13 \\
\text{process} \, j \downarrow & S_I & S_S & X_I & X_S & X_{B,H} & X_{B,A} & X_P & S_O & S_{NO} & S_{NH} & S_{ND} & X_{ND} & S_{ALK} \\ \hline
1 &  & - \frac{1}{Y_H} &  &  & 1 &  &  & - \frac{1-Y_H}{Y_H} &  & -i_{XB} &  &  & - \frac{i_{XB}}{14} \\
2 &  & - \frac{1}{Y_H} &  &  & 1 &  &  &  & - \frac{1-Y_H}{2.86 Y_H} & -i_{XB} &  &  & \frac{1-Y_H}{14 \cdot 2.86 Y_H} - \frac{i_{XB}}{14} \\
3 &  &  &  &  &  & 1 &  &  - \frac{4.57-Y_A}{Y_A} & \frac{1}{Y_A} & -i_{XB}- \frac{1}{Y_A} &  &  & - \frac{i_{XB}}{14} - \frac{1}{7 Y_A} \\
4 &  &  &  & 1-f_P & -1 &  & f_P &  &  &  &  & i_{XB}-f_P i_{XP} &  & \\
5 &  &  &  & 1-f_P &  & -1 & f_P &  &  &  &  & i_{XB}-f_P i_{XP} &  & \\
6 &  &  &  &  &  &  &  &  &  & 1 & -1 &  & \frac{1}{14} \\
7 &  & 1 &  & -1 &  &  &  &  &  &  &  &  & \\
8 &  &  &  &  &  &  &  &  &  &  & 1 & -1 & \\
\end{array}
$$

**Stoichiometric parameters**

| Symbol   | Description                                               | Unit                      |
| -------- | --------------------------------------------------------- | ------------------------- |
| $Y_H$    | Heterotrophic yield                                       | g(COD)$\cdot$(g(COD))^-1^ |
| $Y_A$    | Autotrophic yield                                         | g(COD)$\cdot$(g(N))^-1^   |
| $f_P$    | Fraction of biomass leading to particulate inert products | -                         |
| $i_{XB}$ | Fraction of nitrogen in biomass                           | g(N)$\cdot$(g(COD))^-1^   |
| $i_{XP}$ | Fraction of nitrogen in organic particulate inerts        | g(N)$\cdot$(g(COD))^-1^   |


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [asm1_bsm2](/reference/bsm2_python/bsm2/asm1_bsm2)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [asm1init_bsm2](/reference/bsm2_python/bsm2/init/asm1init_bsm2)


[^1]: [Benchmarking of Control Strategies for Wastewater Treatment Plants](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf), chap. 4.2.1 Activated Sludge Model No. 1
[^2]: [Benchmark Simulation Model no. 2 (BSM2)](http://iwa-mia.org/wp-content/uploads/2022/09/TR3_BSM_TG_Tech_Report_no_3_BSM2_General_Description.pdf), chap. 2. Modeling of the activated sludge section
[^3]: [Activated Sludge Model No. 1, Henze et al. (1987)](https://www.researchgate.net/publication/243624144_Activated_Sludge_Model_No_1)
