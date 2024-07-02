import numpy as np

import bsm2_python.bsm2.init.reginit_bsm2 as reginit
from bsm2_python.bsm2_base import BSM2Base

SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = np.arange(21)


class BSM2OLPP(BSM2Base):
    def __init__(self, endtime, *, tempmodel=False, activate=False):
        super().__init__(endtime=endtime, tempmodel=tempmodel, activate=activate)
        self.violation_all = np.zeros(len(self.simtime))

        self.y_out1_all = np.zeros((len(self.simtime), 21))
        self.y_out2_all = np.zeros((len(self.simtime), 21))
        self.y_out3_all = np.zeros((len(self.simtime), 21))
        self.y_out4_all = np.zeros((len(self.simtime), 21))
        self.y_out5_all = np.zeros((len(self.simtime), 21))
        self.ys_r_all = np.zeros((len(self.simtime), 21))
        self.ys_was_all = np.zeros((len(self.simtime), 21))
        self.ys_of_all = np.zeros((len(self.simtime), 21))
        self.yp_uf_all = np.zeros((len(self.simtime), 21))
        self.yp_of_all = np.zeros((len(self.simtime), 21))
        self.yi_out2_all = np.zeros((len(self.simtime), 21))
        self.yst_out_all = np.zeros((len(self.simtime), 21))
        self.yst_vol_all = np.zeros((len(self.simtime), 2))
        self.ydw_s_all = np.zeros((len(self.simtime), 21))
        self.yt_uf_all = np.zeros((len(self.simtime), 21))
        self.yp_internal_all = np.zeros((len(self.simtime), 21))
        self.yd_out_all = np.zeros((len(self.simtime), 51))
        self.yt_uf_all = np.zeros((len(self.simtime), 21))

    def step(
        self,
        i: int,
        klas: np.ndarray | None = None,
        *,
        stabilized: bool = False,
    ):
        """
        Simulates one time step of the BSM2 model.

        Parameters
        ----------
        i : int
            Index of the current time step
        klas : np.ndarray, optional
            Array with the values of the oxygen transfer coefficients for the 5 ASM1 reactors.
            Default is (reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5)
        """
        if klas is None:
            self.klas = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])
        else:
            self.klas = klas

        super().step(i)

        step: float = self.simtime[i]

        self.violation_all[i] = self.performance.violation_step(self.y_eff[SNH], 4)[0][0]

        self.y_out1_all[i] = self.y_out1
        self.y_out2_all[i] = self.y_out2
        self.y_out3_all[i] = self.y_out3
        self.y_out4_all[i] = self.y_out4
        self.y_out5_all[i] = self.y_out5
        self.ys_r_all[i] = self.ys_r
        self.ys_was_all[i] = self.ys_was
        self.ys_of_all[i] = self.ys_of
        self.yp_uf_all[i] = self.yp_uf
        self.yp_of_all[i] = self.yp_of
        self.yt_uf_all[i] = self.yt_uf
        self.yd_out_all[i] = self.yd_out
        self.yi_out2_all[i] = self.y_out2
        self.yst_out_all[i] = self.yst_out
        self.yst_vol_all[i] = self.yst_vol, step
        self.ydw_s_all[i] = self.ydw_s
        self.yp_internal_all[i] = self.yp_internal
