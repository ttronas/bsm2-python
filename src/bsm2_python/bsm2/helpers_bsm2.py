import warnings

import numpy as np
from numba import int32
from numba.experimental import jitclass
from numba.typed import List

from bsm2_python.bsm2.module import Module


@jitclass
class Combiner(Module):
    def __init__(self):
        """
        Combines multiple arrays in ASM1 format into one array in ASM1 format.
        """
        pass

    @staticmethod
    def output(*args):
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
            out[0:14] = (out[0:14] * out[14] + args[i][0:14] * args[i][14]) / (out[14] + args[i][14])
            out[15:21] = (out[15:21] * out[14] + args[i][15:21] * args[i][14]) / (out[14] + args[i][14])
            out[14] += args[i][14]
        return out


@jitclass(spec=(('sp_type', int32),))
class Splitter(Module):
    def __init__(self, sp_type=1):
        """
        Splits an array in ASM1 format into multiple arrays in ASM1 format.

        Parameters
        ----------
        type : int
            type of splitter (1 or 2)
            1: split ratio is specified in splitratio parameter (default)
            2: split ratio is not specified, but a threshold value is specified in qthreshold parameter
               everything above qthreshold is split into the second flow
        """
        self.sp_type = sp_type

    def output(self, in1, splitratio=(0.0, 0.0), qthreshold=0):
        """
        Splits an array in ASM1 format into multiple arrays in ASM1 format.

        Parameters
        ----------
        in : np.ndarray[21]
            ASM1 array to be split
        splitratio : Tuple(float)
            split ratio for each component. Ideally sums up to 1
            (except if sp_type=2, then no split ratio is needed and flow is split into two flows)
        qthreshold : float
            threshold value for type 2 splitter

        Returns
        -------
        outs : Tuple(np.ndarray[21])
            ASM1 arrays with split volume flows. Tuple of length of splitratio
        """
        outs = List()
        if in1[14] == 0:  # if no flow, all split flows are 0
            for _ in range(len(splitratio)):
                out = np.zeros(21)
                out[:] = in1[:]
                out[14] = 0
                outs.append(out)
        else:  # if flow, split flow ratios are calculated
            # if type 2, everything above qthreshold is split in the second flow. splitratios are overwritten!
            threshold_split_mode = 2
            if self.sp_type == threshold_split_mode:
                needed_len = 2
                if len(splitratio) != needed_len:
                    err = 'Split ratio must be of length 2 for type 2 splitter'
                    raise ValueError(err)
                if splitratio[0] != 0 or splitratio[1] != 0:
                    err = 'splitratio[0] and splitratio[1] must be 0 for type 2 splitter'
                    raise ValueError(err)
                splitratio = (qthreshold, in1[14] - qthreshold) if in1[14] >= qthreshold else (in1[14], 0)
            for i, _ in enumerate(splitratio):
                actual_splitratio = splitratio[i] / sum(splitratio)
                out = np.zeros(21)
                out[14] = in1[14] * actual_splitratio
                if out[14] > 0:  # if there is a physical flow, out is calculated. Otherwise, out is np.zeros(21)
                    out[:14] = in1[:14]
                    out[15:21] = in1[15:21]
                else:
                    out[14] = 0
                outs.append(out)
        return outs


def reduce_asm1(asm1_arr, reduce_to=('SI', 'SS', 'XI', 'XS', 'XBH', 'SNH', 'SND', 'XND', 'TSS', 'Q', 'TEMP')):
    """
    Reduces ASM1 array to selected components.

    Parameters
    ----------
    asm1_arr : np.ndarray[21]
        ASM1 array to be reduced. Needs to contain all ASM1 components:
        ["SI", "SS", "XI", "XS", "XBH", "XBA", "XP", "SO", "SNO", "SNH","SND",
         "XND", "SALK", "TSS", "Q", "TEMP", "SD1", "SD2", "SD3", "XD4", "XD5"]
    reduce_to : Tuple(str)
        components to be included in the reduced array. Defaults to all changing components in BSM2 influent file.

    Returns
    -------
    out : np.ndarray
        reduced ASM1 array
    """
    asm1_components = (
        'SI',
        'SS',
        'XI',
        'XS',
        'XBH',
        'XBA',
        'XP',
        'SO',
        'SNO',
        'SNH',
        'SND',
        'XND',
        'SALK',
        'TSS',
        'Q',
        'TEMP',
        'SD1',
        'SD2',
        'SD3',
        'XD4',
        'XD5',
    )
    # raise error if asm1_arr is not of shape (:,21)
    if len(asm1_arr.shape) == 1:
        is_1d = True
        asm1_arr = np.expand_dims(asm1_arr, axis=0)
    num_cols = 21
    if asm1_arr.shape[1] != num_cols:
        err = 'ASM1 array must have 21 columns'
        raise ValueError(err)

    out = np.zeros((len(asm1_arr[:, 0]), len(reduce_to)))
    for idx, component in enumerate(reduce_to):
        out[:, idx] = asm1_arr[:, asm1_components.index(component)]

    if is_1d:
        out = out[0]
    return out


def expand_asm1(
    red_arr,
    red_components=('SI', 'SS', 'XI', 'XS', 'XBH', 'SNH', 'SND', 'XND', 'TSS', 'Q', 'TEMP'),
    expand_by=None,
):
    """
    Expands reduced ASM1 array to full ASM1 array.

    Parameters
    ----------
    red_arr : np.ndarray
        reduced ASM1 array to be expanded.
    red_components : Tuple(str)
        components in the reduced array. Defaults to all changing components in BSM2 influent file:
        ["SI", "SS", "XI", "XS", "XBH", "SNH", "SND", "XND", "TSS", "Q", "TEMP"]
    expand_by : Dict(str:int)
        components to be added to the reduced array.
        Defaults to all non-changing components in BSM2 influent file and their default values:
        {"XBA": 0, "XP": 0, "SO": 0, "SNO": 0, "SALK": 7, "SD1": 0, "SD2": 0, "SD3": 0, "XD4": 0, "XD5": 0}

    Returns
    -------
    out : np.ndarray[21]
        expanded ASM1 array
    """
    if expand_by is None:
        expand_by = {'XBA': 0, 'XP': 0, 'SO': 0, 'SNO': 0, 'SALK': 7, 'SD1': 0, 'SD2': 0, 'SD3': 0, 'XD4': 0, 'XD5': 0}

    asm1_components = (
        'SI',
        'SS',
        'XI',
        'XS',
        'XBH',
        'XBA',
        'XP',
        'SO',
        'SNO',
        'SNH',
        'SND',
        'XND',
        'SALK',
        'TSS',
        'Q',
        'TEMP',
        'SD1',
        'SD2',
        'SD3',
        'XD4',
        'XD5',
    )
    # raise error if red_arr is not of shape (:,len(red_components))
    if len(red_arr.shape) == 1:
        is_1d = True
        red_arr = np.expand_dims(red_arr, axis=0)

    if red_arr.shape[1] != len(red_components):
        err = 'Reduced ASM1 array must have the same number of columns as red_components'
        raise ValueError(err)

    out = np.zeros((len(red_arr[:, 0]), len(asm1_components)))
    for idx, component in enumerate(asm1_components):
        if component in red_components:
            out[:, idx] = red_arr[:, red_components.index(component)]
        elif component in expand_by:
            out[:, idx] = expand_by[component]
        else:
            warnings.warn(
                f'Component {component} is not in red_components or expand_by. \
                    Component {component} is set to 0',
                stacklevel=1,
            )
            out[:, idx] = 0

    if is_1d:
        out = out[0]
    return out
