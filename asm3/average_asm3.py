import numpy as np

indices_components = np.arange(24)
SO2, SI, SS, SNH4, SN2, SNOX, SALK, XI, XS, XH, XSTO, XA, XSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5, COD, N2, ION, TSS = indices_components


def averages(y_array, sampleinterval, evaltime):
    """Returns an array containing the average values of the components during a certain evaluation time
    in a certain part of the plant

    Parameters
    ----------
    y_array : np.ndarray
        Values of the components at every time step of the evaluation time
    sampleinterval : int or float
        Time step of the evaluation time in days
    evaltime : np.ndarray
        Starting and end point of the evaluation time in days

    Returns
    -------
    np.ndarray
        Array containing the average values of the components during the evaluation time
    """

    size_array = int(len(y_array[0]))
    y_average = np.zeros(size_array)
    for n in range(size_array):
        y_average[n] = np.sum(sampleinterval * y_array[:, Q] * y_array[:, n]) / np.sum(sampleinterval * y_array[:, Q])
    y_average[Q] = np.sum(sampleinterval * y_array[:, Q]) / (evaltime[1] - evaltime[0])

    return y_average
