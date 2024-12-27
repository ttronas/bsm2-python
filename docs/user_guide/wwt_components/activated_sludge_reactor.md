---
hide:
  - toc
---

![Activated sludge reactor](https://gitlab.rrze.fau.de/evt/klaeffizient/bsm2-python/-/raw/doc_new2/docs/assets/.icons/bsm2python/activated-sludge-reactor.svg){ align=right }
<!-- TODO: change link to main branch before merging -->

### Introduction and Model

The activated sludge reactor is designed to remove organic matter and nutrients from wastewater through processes such as carbon oxidation, nitrification and denitrification. This treatment relies on microorganisms, which are supplied with oxygen in an aerated tank. The implementation is based on the Activated Sludge Model No. 1 (ASM1) by Henze et al. (1987). ASM1 represents the activated sludge reactor as a continuous stirred tank reactor (CSTR) that is assumed to be completely mixed. The oxygen transfer provided by the aeration equipment is defined by the mass transfer coefficient K~L~a. Additionally, it is possible to maintain a fixed dissolved oxygen (DO) concentration in the reactor using an aeration controller.

The model incorporates 13 relevant [components](#components), which are categorized into insoluble components (X) and soluble components (S). The transformation of these components is controlled by eight fundamental [process rate equations](#process-rate-equations) that describe four key processes:

- the growth of biomass
- the decay of biomass
- the ammonification of organic nitrogen
- the 'hydrolysis' of particulate organics trapped within the biofloc

The reaction rate for a component $i$ across all processes $\rho_j$ is then described by the [observed conversation rate equation](#observed-conversion-rate-equation), which sums up the products of the [stoichiometric coefficients](#stoichiometric-coefficients-nu_ij) $\nu_{ij}$ and the process rates $\rho_j$. For dynamic state modeling, these equations are expressed as a set of coupled ordinary differential equations, which are solved using numerical integration techniques.

ASM1 also supports connecting multiple reactors with different parameters in series, allowing the simulation of distinct reactor zones (e.g. anoxic denitrification).

### Components

| $i$ | Component                                       | Symbol    | Unit         |
| --  | ----------------------------------------------  | --------- | ------------ |
| 1   | Soluble inert organic matter                    | $S_I$     | M(COD)L^-3^  |
| 2   | Readily biodegradable substrate                 | $S_S$     | M(COD)L^-3^  |
| 3   | Particulate inert organic matter                | $X_I$     | M(COD)L^-3^  |
| 4   | Slowly biodegradable substrate                  | $X_S$     | M(COD)L^-3^  |
| 5   | Active heterotrophic biomass                    | $X_{B,H}$ | M(COD)L^-3^  |
| 6   | Active autotrophic biomass                      | $X_{B,A}$ | M(COD)L^-3^  |
| 7   | Particulate products arising from biomass decay | $X_P$     | M(COD)L^-3^  |
| 8   | Oxygen (negative COD)                           | $S_O$     | M(-COD)L^-3^ |
| 9   | Nitrate and nitrite nitrogen                    | $S_{NO}$  | M(N)L^-3^    |
| 10  | $NH^+_4 + NH_3$ nitrogen                        | $S_{NH}$  | M(N)L^-3^    |
| 11  | Soluble biodegradable organic nitrogen          | $S_{ND}$  | M(N)L^-3^    |
| 12  | Particulate biodegradable organic nitrogen      | $X_{ND}$  | M(N)L^-3^    |
| 13  | Alkalinity                                      | $S_{ALK}$ | Molar unit   |


### Process rate equations

| $\rho_j$ | Process rate in [ML^-3^T^-1^]              | Equation  |
| --       | ------------------------------------------ | --------- |
| 1        | Aerobic growth of heterotrophs             | $\rho_1 = \hat \mu_H \left( \frac{S_S}{K_S + S_S} \right) \left( \frac{S_O}{K_{O,H} + S_O} \right) X_{B,H}$ |
| 2        | Anoxic growth of heterotrophs              | $\rho_2 = \hat \mu_H \left( \frac{S_S}{K_S + S_S} \right) \left( \frac{K_{O,H}}{K_{O,H} + S_O} \right) \times \left( \frac{S_{NO}}{K_{NO} + S_{NO}} \right) \eta_g X_{B,H}$ |
| 3        | Aerobic growth of autotrophs               | $\rho_3 = \hat \mu_A \left( \frac{S_{NH}}{K_{NH} + S_{NH}} \right) \left( \frac{S_O}{K_{O,A} + S_O} \right) X_{B,A}$ |
| 4        | 'Decay' of heterotrophs                    | $\rho_4 = b_H X_{B,H}$ |
| 5        | 'Decay' of autotrophs                      | $\rho_5 = b_A X_{B,A}$ |
| 6        | Ammonification of soluble organic nitrogen | $\rho_6 = k_a S_{ND} X_{B,H}$ |
| 7        | 'Hydrolysis' of entrapped organics         | $\rho_7 = k_h \frac{X_S / X_{B,H}}{K_X + (X_S / X_{B,H})} \left[ \left( \frac{S_O}{K_{O,H} + S_O} \right) + \eta_h \left( \frac{K_{O,H}}{K_{O,H} + S_O} \right) \left( \frac{S_{NO}}{K_{NO} + S_{NO}} \right) \right] X_{B,H}$ |
| 8        | 'Hydrolysis' of entrapped organic nitrogen | $\rho_8 = \rho_7 (X_{ND} / X_S)$ |


#### Kinetic parameters

- $\hat \mu$: Maximum specific growth rate

- $K$: Half-velocity constant

- $b$: Specific decay rate

- Heterotrophic growth and decay: $\hat \mu_H, K_S, K_{O,H}, K_{NO}, b_H$

- Autotrophic growth and decay: $\hat \mu_A, K_{NH}, K_{O,A}, b_A$

- Correction factor for anoxic growth of heterotrophs: $\eta_g$

- Ammonification: $k_a$

- Hydrolysis: $k_h, K_X$

- Correction factor for anoxic hydrolysis: $\eta_h$


### Observed conversion rate equation

$$
r_i = \sum_j \nu_{ij}\rho_j
$$

### Stoichiometric coefficients $\nu_{ij}$

$$
\begin{array}{r|rrrrrrrrrrrrr}
\text{component} \rightarrow j & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 & 11 & 12 & 13 \\
\text{process} \downarrow i & S_I & S_S & X_I & X_S & X_{B,H} & X_{B,A} & X_P & S_O & S_{NO} & S_{NH} & S_{ND} & X_{ND} & S_{ALK} \\ \hline
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

#### Stoichiometric parameters

- $Y$: True growth yield

- Heterotrophic yield: $Y_H$

- Autotrophic yield: $Y_A$

- Fraction of biomass yielding particulate products: $f_P$

- Mass N/Mass COD in biomass: $i_{XB}$

- Mass N/Mass COD in products from biomass: $i_{XP}$


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

[^1]: (For more information visit: [Activated Sludge Model No. 1, Henze et al. (1987)](https://www.researchgate.net/publication/243624144_Activated_Sludge_Model_No_1))
[^2]: ([Benchmarking of Control Strategies for Wastewater Treatment Plants](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf), chap. 4.2.1 Activated Sludge Model No. 1)
