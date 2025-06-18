---
hide:
  - toc
---

![Aeration control](../../../assets/icons/bsm2python/aerationcontrol.svg){ align=right }

### Introduction and Model
The aeration control system aims to maintain a constant dissolved oxygen (DO) concentration in all sludge reactors using real time feedback. This ensures that microorganisms have enough oxygen for metabolism while avoiding over-aeration, which wastes energy.

The implementation of the aeration system is based on Benchmark Simulation Model no.2 (BSM2) by J.Alex et al. (2008), with only a small deviation ensuring better performance. It consists of a sensor, a PID controller and an actuator. 

Broken down to the key aspects, the sensor measures the DO concentration, passes it on the PID controller which then sends a control signal to the actuator controlling the airflow into the tank. Both sensor and actuator are modeled as dynamic systems.

#### Sensor and Actuator

Both the sensor and the actuators are modelled as realistic and dynamic systems with a set of [equations](#sensor-and-actuator-model) using a state space system and transfer function.
The desired behavior is achieved by transforming the original input signal $u(t)$ into a delayed input signal $u_{2}(t)$ with a desired time response $t_{r}$. This is implemented by using a first-order delay transfer function $G_{S}(s)$. In order to to simulate the components in a time domain, $G_{S}(s)$ is transformed into a state space system $y_1(t)$. 
Further enhancing the realistic behaviour of the sensor noise is modelled with a constant noise level and added to the delayed sensor signal. The noise signal is white noise with a standard deviation of $\delta = 1$ multiplied with the noise level $nl$ and the maximum value of the measurement interval $y_{max}$. Note, that the actuator is not equipped with a noise model.
Lastly, within both components, the signal is checked against a maximum and minimum value resulting in a final output signal $y$.

<figure markdown="span">
  ![Sensor flowchart](../../../assets/images/aerationcontrol_sensor_flowchart.drawio.svg)
  <figcaption markdown="1">Flowchart of the sensor model[^3]<br></figcaption>
</figure>


#### PID controller

The PID controller consists of a proportional, an integral and a derivative term, as well as an anti-windup-mechanism. The primary control objective is to maintain a constant DO concentration within the reactor, for example by manipulating the K~L~a parameter.
This is achieved by calculating the error as the difference of the measured process value and the desired setpoint. The error is then evaluated with the proportional, integral and derivative [component](#pid-controller-model), and subject to limit checking via the anti-windup mechanism - resulting in the final control output $y(t)$.

<figure markdown="span">
  ![Sensor flowchart](../../../assets/images/aerationcontrol_pid_flowchart.drawio.svg)
  <figcaption markdown="1">Flowchart of the PID controller[^4]<br></figcaption>
</figure>


### Equations

#### Components

| $i$ | Component                        | Symbol    | Unit                 |
| --- | -------------------------------- | --------- | -------------------- |
| 1   | Dissolved oxygen                 | $S_O$     | g(O~2~)$\cdot$m^-3^  |
| 2   | Mass transfer coefficient        | $K_{L}a$  | $d^{-1}$             | 
| 3   | Original input signal            | $u(t)$    | -                    |
| 4   | Delayed input signal             | $u_{2}(t)$| -                    |
| 5   | Response time                    | $t_{r}$   | s                    |
| 6   | Maximum value of the measurement | $y_{max}$ | -                    |
| 7   | Noise level                      | $nl$      | -                    |


#### Sensor and Actuator model
| Symbol        | Description                  | Equation                                   |
| ------------- | ---------------------------- | ------------------------------------------ |
| $G_{S}(s)$    | Transfer function for class A| $(\frac{1}{1+\tau s})^2$                   |
| $y_1(t)$      | state space function         | $u_{2}(t) + y_{max}\times nl \times n(t)$  |
| $y(t)$        | state space function         | $y(t) =\begin{cases} y_{max}, & y_1(t) > y_{max} \\ y_1(t), & y_{min} \leq y_1(t) \leq y_{max} \\ y_{min}, & y_1(t) < y_{min} \end{cases}$ |


#### PID controller model
| Symbol                    | Description                       | Equation                                                         | 
| ------------------------- | ----------------------------------| -----------------------------------------------------------------|
| $e$                       | Error                             | $Z^{setpoint} - Z^{meas}$                                        |
| $IAE$                     | Integral of Absolute Error        | $\int_{t_{f}}^{t_{0}}  ∣e∣ \,dt$                                  |
| $ISE$                     | Integral of Squared Error         | $\int_{t_{f}}^{t_{0}} e^2 \,dt$                                  |
| $Dev^{max}$               | Maximal deviation from set point  | $max(∣e∣)$                                                        |
| $Var(e)$                  | Error variance                    | $\overline{e^2} - \left( \overline{e} \right)^2$                 |
| $\overline{e}$            | Mean of $e$                       | $\frac{\int_{t_{f}}^{t_{0}} e \,dt}{t_{obs}}$                    |
| $\overline{e^2}$          | Mean of $e^2$                     | $\frac{\int_{t_{f}}^{t_{0}} e^2 \,dt}{t_{obs}}$                  |
| $Var(\Delta u)$           | Variance of manipulated variable ($u_{i}$) variations| $\overline{(\Delta u)^2} - \left( \overline{\Delta u} \right)^2$ |
| $\Delta u$                | Difference of manipulated variable| $∣u(t + \Delta t) - u(t)∣$                                        |
| $\overline{\Delta u}$     | Mean of $\delta u$                | $\frac{1}{t_{\mathrm{obs}}} \int_{t_0}^{t_r} \Delta u \, dt$     |
| $\overline{(\Delta u)^2}$ | Mean of $(\delta u)^2$            | $\frac{1}{t_{\mathrm{obs}}} \int_{t_0}^{t_r} (\Delta u)^2 \, dt$ |


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