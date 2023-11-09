import numpy as np
from numba.experimental import jitclass
from numba.typed import List


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
        if args[0][14] == 0:
            args[0][14] = 1e-10

        for i in range(len(args)):
            out[0:14] = (out[0:14]*out[14]+args[i][0:14]*args[i][14])/(out[14]+args[i][14])
            out[15:21] = (out[15:21]*out[14]+args[i][15:21]*args[i][14])/(out[14]+args[i][14])
            out[14] += args[i][14]
        return out


@jitclass
class Splitter():
    def __init__(self):
        """
        Splits an array in ASM1 format into multiple arrays in ASM1 format.
        """
        pass

    def outputs(self, in1, splitratio):
        """
        Splits an array in ASM1 format into multiple arrays in ASM1 format.

        Parameters
        ----------
        in : np.ndarray[21]
            ASM1 array to be split
        splitratio : np.ndarray
            split ratio for each component. Ideally sums up to 1

        Returns
        -------
        outs : Tuple(np.ndarray[21])
            ASM1 arrays with split volume flows
        """
        outs = List()
        for i in range(len(splitratio)):
            if sum(splitratio) != 0:
                actual_splitratio = splitratio[i]/sum(splitratio)
            else:
                actual_splitratio = 0
            out = np.zeros(21)
            out[:] = in1[:]
            out[14] *= actual_splitratio
            if out[14] < 0:
                out[14] = 0
            outs.append(out)
        return outs
