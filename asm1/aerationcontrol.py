import numpy as np
from scipy.integrate import odeint
from scipy import signal


class Oxygensensor:
    def __init__(self, min_SO, max_SO, T_SO, std_SO):
        self.min_SO = min_SO
        self.max_SO = max_SO
        self.T_SO = T_SO
        self.std_SO = std_SO

    def measureSO(self, SO, step, controlnumber, noise_SO, transferfunction, control):
        num_SO = [1]
        den_SO = [self.T_SO*self.T_SO, 2 * self.T_SO, 1]
        timestep = control/(60*24)
        if step == 0:
            SO_meas = SO[int(transferfunction/control)-1] + noise_SO * self.max_SO * self.std_SO
        elif step <= transferfunction/(60*24):
            t_SO_lower15 = np.arange(0, step+timestep, timestep)
            tout_SO, yout_SO, xout_SO = signal.lsim((num_SO, den_SO), SO[((int(transferfunction/control)+1) - controlnumber):(int(transferfunction/control)+1)], t_SO_lower15[0:controlnumber])
            SO_meas = yout_SO[controlnumber - 1] + noise_SO * self.max_SO * self.std_SO

        else:
            t_SO_15 = np.arange(step-transferfunction/control*timestep, step+timestep, timestep)
            tout_SO, yout_SO, xout_SO = signal.lsim((num_SO, den_SO), SO, t_SO_15[0:(int(transferfunction/control)+1)])
            SO_meas = yout_SO[int(transferfunction/control)] + noise_SO * self.max_SO * self.std_SO

        if SO_meas < self.min_SO:
            SO_meas = self.min_SO
        if SO_meas > self.max_SO:
            SO_meas = self.max_SO

        return SO_meas


class PIaeration:
    def __init__(self, KLa_max, KSO, TiSO, TtSO, SOref, KLaoffset, SOintstate, SOawstate, kla_lim, kla_calc):
        self.KLa_max = KLa_max
        self.KSO = KSO
        self.TiSO = TiSO
        self.TtSO = TtSO
        self.SOref = SOref
        self.KLaoffset = KLaoffset
        self.SOintstate = SOintstate
        self.SOawstate = SOawstate
        self.kla_lim = kla_lim
        self.kla_calc = kla_calc

    def output(self, SO_meas, step, timestep):
        error_SO = (self.SOref - SO_meas) * self.KSO

        def function_ac(t, y):
            y = (self.SOref - SO_meas) * self.KSO / self.TiSO
            return y

        t_ac = np.array([step, step+timestep])
        ode_ac = odeint(function_ac, self.SOintstate, t_ac, tfirst=True)

        integral_ac = float(ode_ac[1])
        self.SOintstate = integral_ac

        def function_aw(t, y):
            y = (self.kla_lim - self.kla_calc) / self.TtSO
            return y

        ode_aw = odeint(function_aw, self.SOawstate, t_ac, tfirst=True)
        antiwindup = float(ode_aw[1])

        self.SOawstate = antiwindup
        self.kla_calc = error_SO + integral_ac + self.KLaoffset + 0 * antiwindup

        kla = float(self.kla_calc)
        if kla < 0:
            kla = 0
        if kla > self.KLa_max:
            kla = self.KLa_max
        self.kla_lim = kla

        return kla


class KLaactuator:
    def __init__(self, T_KLa):
        self.T_KLa = T_KLa

    def real_actuator (self, kla, step, controlnumber, transferfunction, control):
        num_kla = [1]
        den_kla = [self.T_KLa*self.T_KLa, 2*self.T_KLa, 1]
        timestep = control / (60 * 24)
        if step == 0:
            kla = kla[14]
        elif step <= transferfunction / (60 * 24):
            t_kla_lower15 = np.arange(0, step + timestep, timestep)
            tout_kla, yout_kla, xout_kla = signal.lsim((num_kla, den_kla), kla[((int(transferfunction/control)+1) - controlnumber):(int(transferfunction/control)+1)], t_kla_lower15[0:controlnumber])
            kla = yout_kla[controlnumber - 1]

        else:
            t_kla_15 = np.arange(step - transferfunction/control*timestep, step + timestep, timestep)
            tout_kla, yout_kla, xout_kla = signal.lsim((num_kla, den_kla), kla, t_kla_15[0:(int(transferfunction/control)+1)])
            kla = yout_kla[int(transferfunction/control)]

        return kla


