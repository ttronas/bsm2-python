---
hide:
  - toc
---



### Introduction and Model
The aerationcontrol system aims to maintain a constant dissolved oxygen (DO) concentration in all sludge reactors using real time feedback. Hereby the DO concentration is measured in the 5th reactor compartment to adjust the airflow into all other compartments accordingly. This ensures that microorganisms have enough oxygen for metabolism while avoiding over-aeration, which wastes energy.

The implementation of the aerationsystem is based on Benchmark Simulation Model no.2 (BSM2) by J.Alex et al (2008), with only a small deviation ensuring better performance. It consists of a sensor, a PID-controller and an actuator.  Broken down to the key aspects, the sensor measures the DO concentration, passes it on the PID controller which then sends a signal to the acutator controlling the airflow into the tank. Both sensor and actuator are modeled as dynamic systems.


The sensor is equipped with a transfer functions $G_{S}(s)$ which models its response time $t_{r}$ and noise model, which is further transformed into a state space system $y$ in order to simulate the sensor in a time domain.
After measuring the DO concentration in the 5th tank, the original sensor signal $u(t)$ is transformed into a delayed sensor signal $u_{2}(t)$. The transfer function is used to implement the expected time response of the sensor. Enhancing its realistic behaviour noise is modelled with a constant noise level and added to the delayed sensor signal. Before the signal is forwarded to the controller, the limit is checked as the sensor has a minimum and maximum value as well.


The PID controller consists of a proportional, an integral and a deritative term, as well as an antiwindup-mechanism. The primary control objective is to maintain the dissolved oxygen concentration in the 5th reactor at a predetermined set point by manipulating the oxygen transfer coefficient in the 4th reactor in such a way that: $K_{L}a_{3} = K_{L}a_{4}; K_{L}a_{5} = /frac{K_{L}a_{4}}{2}$.
This is achieved by calculating the error value by comparing the measured process value and comparing it to the desired setpoint. After that the error is evaluated with the proportional, integral and deritative component, as well as limit checked with the anti-windup mechansim - forming the ouput value passed on to the acutator.


The actuator also has a transfer function $G_{S}(s)$ modelling its response time  $t_{r}$, which again is transformed into a state space system $y$.
According to the magnitude of the signal given by the PID controller the actuator changes the $K_{L}a$ value for each reactor compartment. This eventually leads to an increase in the DO concentration in the 5th compartment. Furthermore the acutator has a minimum and a maximum value in order to not overshoot, in case the PID signal increases above a ceratain point.


### Equations

#### Components

| $i$ | Component                       | Symbol    | Unit                 |
| --- | ------------------------------- | --------- | -------------------- |
| 1   | Dissolved oxygen                | $S_O$     | g(O~2~)$\cdot$m^-3^  |
| 2   | Mass transfer coefficient       | $K_{L}a$  | d^-1                 | 
| 3   | Original sensor signal          | $u(t)$    | -                    |
| 4   | Delayed sensor signal           | $u_{2}(t)$| -                    |
| 5   | Response time                   | $t_{r}$   | s                    |

**Sensor and Actuator**
| Symbol        | Description                 | Equation                                   |
| ------------- | --------------------------- | ------------------------------------------ |
| $G_{S}(s)$   | Transfer function for class A| $(/frac{1}{1+/tau s})^2$                   |
| $y$          | state space system           | $1-(1+/frax{t}{/tau})exp(-/frac{t}{/tau})$ |


**PID controller**
| Symbol        | Description                     | Equation                        | 
| ------------- | --------------------------------| ------------------------------- |
| $e$           | Error                           | Z^{setpoint}-Z^{meas}           |
| $IAE$         | Integral of Absolute Error      | $/int_{t_{f}}^{t_{0}} |e| \,dt$ |
| $ISE$         | Integral of Squared Error       | $/int_{t_{f}}^{t_{0}} e^2 \,dt$ |
| $Dev^{max}$   | Maxmial deviation from set point| $max(|e|)$                      |
| $Var(e)$      | Error variance                  |                                 |


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [aerationcontrol_bsm2](/reference/bsm2_python/bsm2/aerationcontrol)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [areationcontrolinit_bsm2](/reference/bsm2_python/bsm2/init/aerationcontrolinit)

[^1]: [Benchmarking of Control Strategies for Wastewater Treatment Plants](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf), chap. 4.3 Sensors and Actuators
[^2]: [Benchmarking of Control Strategies for Wastewater Treatment Plants](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf), chap. 5.2 BSM2 Controllers

[^3]: [Benchmark Simulation Model no. 2 (BSM2)](http://iwa-mia.org/wp-content/uploads/2022/09/TR3_BSM_TG_Tech_Report_no_3_BSM2_General_Description.pdf), chap. 13 Sensors and Control Handles
[^4]: [Benchmark Simulation Model no. 2 (BSM2)](http://iwa-mia.org/wp-content/uploads/2022/09/TR3_BSM_TG_Tech_Report_no_3_BSM2_General_Description.pdf), chap. 11 Set-up of a default controller