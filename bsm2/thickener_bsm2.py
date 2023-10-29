import numpy as np
from scipy.integrate import odeint
from numba.experimental import jitclass


indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components

# @jitclass(spec=[('t_par', float[:]), ('asm1par', float[:])])
class Thickener:
    def __init__(self, t_par, asm1par):
        self.t_par = t_par
        self.asm1par = asm1par

    def outputs(self, yt_in):
        # thickener_perc, TSS_removal_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS = t_par
        # y = yt_uf, yt_of
        # u = yt_in
        
        yt_uf = np.zeros(21)
        yt_of = np.zeros(25)

        TSSin = self.t_par[2]*yt_in[2] + self.t_par[3]*yt_in[3] + self.t_par[4]*yt_in[4] + self.t_par[5]*yt_in[5] + self.t_par[6]*yt_in[6]
        thickener_factor = self.t_par[0]*10000/TSSin
        Qu_factor = self.t_par[1]/(100*thickener_factor)
        thinning_factor = (1 - self.t_par[1]/100) / (1-Qu_factor)

        if thickener_factor > 1:
            # underflow
            yt_uf[:] = yt_in[:]
            yt_uf[XI]=yt_in[XI]*thickener_factor
            yt_uf[XS]=yt_in[XS]*thickener_factor
            yt_uf[XBH]=yt_in[XBH]*thickener_factor
            yt_uf[XBA]=yt_in[XBA]*thickener_factor
            yt_uf[XP]=yt_in[XP]*thickener_factor
            yt_uf[XND]=yt_in[XND]*thickener_factor
            yt_uf[TSS]=TSSin*thickener_factor
            yt_uf[Q]=yt_in[Q]*Qu_factor
            yt_uf[XD4]=yt_in[XD4]*thickener_factor
            yt_uf[XD5]=yt_in[XD5]*thickener_factor

            # overflow
            yt_of[:21] = yt_in[:]
            yt_of[XI]=yt_in[XI]*thinning_factor
            yt_of[XS]=yt_in[XS]*thinning_factor
            yt_of[XBH]=yt_in[XBH]*thinning_factor
            yt_of[XBA]=yt_in[XBA]*thinning_factor
            yt_of[XP]=yt_in[XP]*thinning_factor
            yt_of[XND]=yt_in[XND]*thinning_factor
            yt_of[TSS]=TSSin*thinning_factor
            yt_of[Q]=yt_in[Q]*(1-Qu_factor)
            yt_of[XD4]=yt_in[XD4]*thinning_factor
            yt_of[XD5]=yt_in[XD5]*thinning_factor
            
            # additional values to compare:
            # Kjeldahl N concentration:
            yt_of[21] = yt_of[SNH] + yt_of[SND] + yt_of[XND] + self.asm1par[17] * (yt_of[XBH] + yt_of[XBA]) + self.asm1par[18] * (yt_of[XP] + yt_of[XI])
            # total N concentration:
            yt_of[22] = yt_of[21] + yt_of[SNO]
            # total COD concentration:
            yt_of[23] = yt_of[SS] + yt_of[SI] + yt_of[XS] + yt_of[XI] + yt_of[XBH] + yt_of[XBA] + yt_of[XP]
            # BOD5 concentration:
            yt_of[24] = 0.25 * (yt_of[SS] + yt_of[XS] + (1-self.asm1par[16]) * (yt_of[XBH] + yt_of[XBA]))

        else:
            # the influent is too high on solids to thicken further
            # all the influent leaves with the underflow
            yt_uf[:] = yt_in[:]
            yt_uf[13] = TSSin

            # overflow
            yt_of[:] = 0



        return yt_uf, yt_of