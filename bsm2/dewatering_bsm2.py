import numpy as np
from numba import float64
from numba.experimental import jitclass


indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components

@jitclass(spec=[('d_par', float64[:])])
class Dewatering:
    def __init__(self, d_par):
        """
        calculates the water and sludge stream concentrations   
        from an 'ideal' dewatering unit based on a fixed percentage of solids in
        the dewatered sludge. A defined amount of total solids are removed from
        the influent sludge stream and goes into the stream of dewatered sludge
        and the remaining will leave with the reject water phase. 
        Soluble concentrations are not affected.
        Temperature is also handled ideally, i.e. T(out)=T(in).

        Parameters
        ----------
        d_par : np.ndarray
            [dewater_perc, TSS_removal_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS]
            dewater_perc: percentage of solids in the dewatered sludge
            TSS_removal_perc: percentage of total solids removed from the influent sludge
            X_I2TSS: ratio of inert particulate COD to TSS
            X_S2TSS: ratio of soluble COD to TSS
            X_BH2TSS: ratio of heterotrophic biomass to TSS
            X_BA2TSS: ratio of autotrophic biomass to TSS
            X_P2TSS: ratio of particulate phosphorus to TSS
        """
        self.d_par = d_par

    def outputs(self, yd_in):
        """
        Returns the sludge and reject concentrations from an 'ideal' dewatering unit.

        Parameters
        ----------
        yd_in : np.ndarray
            dewatering inlet concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        
        Returns
        -------
        yd_s : np.ndarray
            dewatering sludge concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        yd_r : np.ndarray
            dewatering reject concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        """
        # dewater_perc, TSS_removal_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS = d_par
        # y = yd_s, yd_r
        # u = yd_in
        
        yd_s = np.zeros(21)
        yd_r = np.zeros(21)

        TSSin = self.d_par[2]*yd_in[2] + self.d_par[3]*yd_in[3] + self.d_par[4]*yd_in[4] + self.d_par[5]*yd_in[5] + self.d_par[6]*yd_in[6]
        dewater_factor = self.d_par[0]*10000/TSSin
        Qu_factor = self.d_par[1]/(100*dewater_factor)
        reject_factor = (1 - self.d_par[1]/100) / (1-Qu_factor)

        if dewater_factor > 1:
            # sludge
            yd_s[:] = yd_in[:]
            yd_s[XI]=yd_in[XI]*dewater_factor
            yd_s[XS]=yd_in[XS]*dewater_factor
            yd_s[XBH]=yd_in[XBH]*dewater_factor
            yd_s[XBA]=yd_in[XBA]*dewater_factor
            yd_s[XP]=yd_in[XP]*dewater_factor
            yd_s[XND]=yd_in[XND]*dewater_factor
            yd_s[TSS]=TSSin*dewater_factor
            yd_s[Q]=yd_in[Q]*Qu_factor
            yd_s[XD4]=yd_in[XD4]*dewater_factor
            yd_s[XD5]=yd_in[XD5]*dewater_factor

            # reject
            yd_r[:] = yd_in[:]
            yd_r[XI]=yd_in[XI]*reject_factor
            yd_r[XS]=yd_in[XS]*reject_factor
            yd_r[XBH]=yd_in[XBH]*reject_factor
            yd_r[XBA]=yd_in[XBA]*reject_factor
            yd_r[XP]=yd_in[XP]*reject_factor
            yd_r[XND]=yd_in[XND]*reject_factor
            yd_r[TSS]=TSSin*reject_factor
            yd_r[Q]=yd_in[Q]*(1-Qu_factor)
            yd_r[XD4]=yd_in[XD4]*reject_factor
            yd_r[XD5]=yd_in[XD5]*reject_factor
            
        else:
            # the influent is too high on solids to thicken further
            # all the influent leaves with the sludge flow
            yd_s[:] = yd_in[:]
            yd_s[13] = TSSin

            # reject flow is zero
            yd_r[:] = 0



        return yd_s, yd_r