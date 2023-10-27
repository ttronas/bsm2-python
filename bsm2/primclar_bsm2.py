import numpy as np
from scipy.integrate import odeint
from numba import jit


indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components

@jit(nopython=True)
def primclarequations(t, yp, yp_in, p_par, volume, tempmodel):
    # u = yp_in
    # x = yp
    # dx = dyp
    dyp = np.zeros(21)
    reac = np.zeros(21)

    dyp[0:13] = 1.0 / volume * (yp_in[Q] * (yp_in[0:13] - yp[0:13]))
    dyp[13] = 0.0  # TSS
    dyp[14] = (yp_in[Q] - yp[Q]) / p_par[2]

    if not tempmodel:
        dyp[15] = 0.0
    else:
        dyp[15] = 1.0 / volume * (yp_in[Q] * (yp_in[15] - yp[15]))
    
    dyp[16:21] = 1.0 / volume * (yp_in[Q] * (yp_in[16:21] - yp[16:21]))

    return dyp

class PrimaryClarifier:
    def __init__(self, volume, yp0, p_par, asm1par, x_vector, tempmodel, activate):
        self.volume = volume
        self.yp0 = yp0
        self.p_par = p_par
        self.asm1par = asm1par
        self.x_vector = x_vector
        self.tempmodel = tempmodel
        self.activate = activate
    
    def outputs(self, timestep, step, yp_in):
        # f_corr, f_X, t_m, f_PS = p_par
        # y = yp_out, yp_eff
        # u = yp_int
        # x : yp_in
        
        yp_out = np.zeros(21)
        yp_eff = np.zeros(25)

        t_eval = np.array([step, step+timestep])    # time interval for odeint

        ode = odeint(primclarequations, self.yp0, t_eval, tfirst=True, args=(yp_in, self.p_par, self.volume, self.tempmodel))

        yp_int = ode[1]

        self.yp0 = yp_int

        Qu = self.p_par[3] * yp_in[Q]  # underflow from primary clarifier
        E = yp_in[Q] / Qu  # thickening factor
        tt = self.volume / (yp_in[Q] + 0.001)  # hydraulic retention time

        nCOD = self.p_par[0] * (2.88*self.p_par[1]-0.118) * (1.45+6.15*np.log(tt*24*60))  # Total COD removal efficiency in primary clarifier
        nX = nCOD/self.p_par[1]  # Removal efficiency of particulate COD in %, since assumption that soluble COD is not removed
        nX = max(0, min(100, nX))  # nX is between 0 and 100

        ff = (1-self.x_vector*nX/100)
        # ASM1 state outputs effluent
        yp_eff[0:13] = ff[0:13]*yp_in[0:13]
        yp_eff[yp_eff < 0.0] = 0.0
        # dummy state outputs effluent
        yp_eff[16:21] = ff[16:21]*yp_in[16:21]
        yp_eff[yp_eff < 0.0] = 0.0

        # ASM1 state outputs underflow
        yp_out[0:13] = ((1-ff[0:13])*E + ff[0:13]) * yp_in[0:13]
        yp_out[yp_out < 0.0] = 0.0
        # dummy state outputs underflow
        yp_out[16:21] = ((1-ff[16:21])*E + ff[16:21]) * yp_in[16:21]
        yp_out[yp_out < 0.0] = 0.0

        # TSS outputs effluent
        yp_eff[13] = self.asm1par[19]*yp_eff[XI] + self.asm1par[20]*yp_eff[XS] + self.asm1par[21]*yp_eff[XBH] + self.asm1par[22]*yp_eff[XBA] + self.asm1par[23]*yp_eff[XP]
        yp_eff[14] = yp_int[14] - Qu  # flow rate in effluent

        # TSS outputs underflow
        yp_out[13] = self.asm1par[19]*yp_out[XI] + self.asm1par[20]*yp_out[XS] + self.asm1par[21]*yp_out[XBH] + self.asm1par[22]*yp_out[XBA] + self.asm1par[23]*yp_out[XP]
        yp_out[14] = Qu  # flow rate in underflow

        if not self.tempmodel:
            if step == 0:
                self.yp0[15] = yp_in[15]
                yp_eff[15] = yp_in[15]
                yp_out[15] = yp_in[15]
            else:
                yp_eff[15] = yp_int[15]
                yp_out[15] = yp_int[15]
        else:
            yp_eff[15] = yp_in[15]
            yp_out[15] = yp_in[15]

        # additional values to compare:
        # Kjeldahl N concentration:
        yp_eff[21] = yp_eff[SNH] + yp_eff[SND] + yp_eff[XND] + self.asm1par[17] * (yp_eff[XBH] + yp_eff[XBA]) + self.asm1par[18] * (yp_eff[XP] + yp_eff[XI])
        # total N concentration:
        yp_eff[22] = yp_eff[21] + yp_eff[SNO]
        # total COD concentration:
        yp_eff[23] = yp_eff[SS] + yp_eff[SI] + yp_eff[XS] + yp_eff[XI] + yp_eff[XBH] + yp_eff[XBA] + yp_eff[XP]
        # BOD5 concentration:
        yp_eff[24] = 0.25 * (yp_eff[SS] + yp_eff[XS] + (1-self.asm1par[16]) * (yp_eff[XBH] + yp_eff[XBA]))

        return yp_out, yp_eff
