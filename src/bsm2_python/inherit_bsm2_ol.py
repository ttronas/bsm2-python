from bsm2_python.bsm2_base import BSM2BASE


class BSM2OL(BSM2BASE):
    def __init__(self, endtime, *, tempmodel=False, activate=False):
        super().__init__(endtime=endtime, tempmodel=tempmodel, activate=activate)
