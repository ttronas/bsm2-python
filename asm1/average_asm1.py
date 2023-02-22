import numpy as np

indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components


# simetime: array der alle Zeitschritte enthält
# y_array enthält alle Werte von z.B. Effluent
# evaltime ist start und endzeit von Intervall, das für Berechnung ist (z.B. 7 bis 14 d)
def averages(y_array, sampleinterval, evaltime):
    y_average = np.zeros(25)
    for n in range(25):
        y_average[n] = np.sum(sampleinterval * y_array[:, Q] * y_array[:, n]) / np.sum(sampleinterval * y_array[:, Q])
    y_average[Q] = np.sum(sampleinterval * y_array[:, Q]) / (evaltime[1] - evaltime[0])
    # print(y_average[Q])
    return y_average
