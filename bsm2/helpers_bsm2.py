import numpy as np
from numba.experimental import jitclass
from numba.typed import List
from numba import int32


@jitclass
class Combiner():
    def __init__(self):
        """
        Combines multiple arrays in ASM1 format into one array in ASM1 format.
        """
        pass

    def output(self, *args):
        """
        Combines multiple arrays in ASM1 format into one array in ASM1 format.

        Parameters
        ----------
        *args : np.ndarray[21]
            ASM1 arrays to be combined

        Returns
        -------
        out : np.ndarray[21]
            ASM1 array with combined values
        """
        out = np.zeros(21)
        if args[0][14] == 0:  # if no flow in first array, search for first array with flow
            start_idx = len(args)
            for idx, item in enumerate(args):
                if item[14] != 0:
                    start_idx = idx
                    break
        else:
            start_idx = 0

        for i in range(start_idx, len(args)):
            out[0:14] = (out[0:14]*out[14]+args[i][0:14]*args[i][14])/(out[14]+args[i][14])
            out[15:21] = (out[15:21]*out[14]+args[i][15:21]*args[i][14])/(out[14]+args[i][14])
            out[14] += args[i][14]
        return out


@jitclass(spec=(('sp_type', int32),))
class Splitter():
    def __init__(self, sp_type=1):
        """
        Splits an array in ASM1 format into multiple arrays in ASM1 format.

        Parameters
        ----------
        type : int
            type of splitter (1 or 2)
            1: split ratio is specified in splitratio parameter (default)
            2: split ratio is not specified, but a threshold value is specified in Qthreshold parameter
               everything above Qthreshold is split into the second flow
        """
        self.sp_type = sp_type

    def outputs(self, in1, splitratio=(0., 0.), Qthreshold=0):
        """
        Splits an array in ASM1 format into multiple arrays in ASM1 format.

        Parameters
        ----------
        in : np.ndarray[21]
            ASM1 array to be split
        splitratio : Tuple(float)
            split ratio for each component. Ideally sums up to 1
            (except if sp_type=2, then no split ratio is needed and flow is split into two flows)
        Qthreshold : float
            threshold value for type 2 splitter

        Returns
        -------
        outs : Tuple(np.ndarray[21])
            ASM1 arrays with split volume flows. Tuple of length of splitratio
        """
        outs = List()
        if in1[14] == 0:  # if no flow, all split flows are 0
            for i in range(len(splitratio)):
                out = np.zeros(21)
                out[:] = in1[:]
                out[14] = 0
                outs.append(out)
        else:  # if flow, split flow ratios are calculated
            # if type 2, everything above Qthreshold is split in the second flow. splitratios are overwritten!
            if self.sp_type == 2:
                if len(splitratio) != 2:
                    raise ValueError("Split ratio must be of length 2 for type 2 splitter")
                if splitratio[0] != 0 or splitratio[1] != 0:
                    print("Warning: Split ratio is overwritten for type 2 splitter")
                if in1[14] >= Qthreshold:
                    splitratio = (Qthreshold, in1[14] - Qthreshold)
                else:
                    splitratio = (in1[14], 0)
            for i in range(len(splitratio)):
                actual_splitratio = splitratio[i]/sum(splitratio)
                out = np.zeros(21)
                out[14] = in1[14] * actual_splitratio
                if out[14] > 0:  # if there is a physical flow, out is calculated. Otherwise, out is np.zeros(21)
                    out[:14] = in1[:14]
                    out[15:21] = in1[15:21]
                else:
                    out[14] = 0
                outs.append(out)
        return outs
