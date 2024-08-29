"""
This calculates the overflow and underflow concentrations
from an 'ideal' thickener unit based on a fixed percentage of sludge in
the underflow flow. A defined amount of total solids are removed from
the water stream and goes into the sludge stream and the remaining will
leave with the water phase. Soluble concentrations are not affected.
Temperature is also handled ideally, i.e. T(out)=T(in).

Copyright (2006):
 Ulf Jeppsson
 Dept. Industrial Electrical Engineering and Automation (IEA), Lund University, Sweden
 https://www.lth.se/iea/

Copyright (2024):
 Jonas Miederer
 Chair of Energy Process Engineering (EVT), FAU Erlangen-Nuremberg, Germany
 https://www.evt.tf.fau.de/
"""

import numpy as np
from numba import float64
from numba.experimental import jitclass

from bsm2_python.bsm2.module import Module

indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components


@jitclass(spec=[('t_par', float64[:])])
class Thickener(Module):
    def __init__(self, t_par):
        """
        Calculates the overflow and underflow concentrations
        from an 'ideal' thickener unit based on a fixed percentage of sludge in
        the underflow flow. A defined amount of total solids are removed from
        the water stream and goes into the sludge stream and the remaining will
        leave with the water phase. Soluble concentrations are not affected.
        Temperature is also handled ideally, i.e. T(out)=T(in).

        Parameters
        ----------
        t_par : np.ndarray(7)
            [thickener_perc, TSS_removal_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS]
            thickener_perc: percentage of sludge in the underflow flow
            TSS_removal_perc: percentage of total solids removed from the water phase
            X_I2TSS: ratio of inert particulate COD to TSS
            X_S2TSS: ratio of soluble COD to TSS
            X_BH2TSS: ratio of heterotrophic biomass to TSS
            X_BA2TSS: ratio of autotrophic biomass to TSS
            X_P2TSS: ratio of particulate phosphorus to TSS
        """
        self.t_par = t_par

    def output(self, yt_in):
        """
        Returns the overflow and underflow concentrations from an 'ideal' thickener unit.

        Parameters
        ----------
        yt_in : np.ndarray
            thickener inlet concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)

        Returns
        -------
        yt_uf : np.ndarray
            thickener underflow concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        yt_of : np.ndarray
            thickener overflow concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
            at the current time step
        """
        # thickener_perc, TSS_removal_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS = t_par
        # y = yt_uf, yt_of
        # u = yt_in

        yt_uf = np.zeros(21)
        yt_of = np.zeros(21)

        tssin = (
            self.t_par[2] * yt_in[2]
            + self.t_par[3] * yt_in[3]
            + self.t_par[4] * yt_in[4]
            + self.t_par[5] * yt_in[5]
            + self.t_par[6] * yt_in[6]
        )
        try:
            thickener_factor = self.t_par[0] * 10000 / tssin
            qu_factor = self.t_par[1] / (100 * thickener_factor)
        except Exception:
            thickener_factor = 0
            qu_factor = 0
        thinning_factor = (1 - self.t_par[1] / 100) / (1 - qu_factor)

        if thickener_factor > 1:
            # underflow
            yt_uf[:] = yt_in[:]
            yt_uf[XI] = yt_in[XI] * thickener_factor
            yt_uf[XS] = yt_in[XS] * thickener_factor
            yt_uf[XBH] = yt_in[XBH] * thickener_factor
            yt_uf[XBA] = yt_in[XBA] * thickener_factor
            yt_uf[XP] = yt_in[XP] * thickener_factor
            yt_uf[XND] = yt_in[XND] * thickener_factor
            yt_uf[TSS] = tssin * thickener_factor
            yt_uf[Q] = yt_in[Q] * qu_factor
            yt_uf[XD4] = yt_in[XD4] * thickener_factor
            yt_uf[XD5] = yt_in[XD5] * thickener_factor

            # overflow
            yt_of[:] = yt_in[:]
            yt_of[XI] = yt_in[XI] * thinning_factor
            yt_of[XS] = yt_in[XS] * thinning_factor
            yt_of[XBH] = yt_in[XBH] * thinning_factor
            yt_of[XBA] = yt_in[XBA] * thinning_factor
            yt_of[XP] = yt_in[XP] * thinning_factor
            yt_of[XND] = yt_in[XND] * thinning_factor
            yt_of[TSS] = tssin * thinning_factor
            yt_of[Q] = yt_in[Q] * (1 - qu_factor)
            yt_of[XD4] = yt_in[XD4] * thinning_factor
            yt_of[XD5] = yt_in[XD5] * thinning_factor

        else:
            # the influent is too high on solids to thicken further
            # all the influent leaves with the underflow
            yt_uf[:] = yt_in[:]
            yt_uf[13] = tssin

            # overflow
            yt_of[:] = 0

        return yt_uf, yt_of
