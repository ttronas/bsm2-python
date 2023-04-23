import numpy as np


def aerationenergy (kla, vol, sosat, sampleinterval, evaltime):
    ae = sum(sum(sosat * vol * kla)*sampleinterval)/(1.8*1000 * (evaltime[1]-evaltime[0]))
    return ae


def pumpingenergy (flows, pumpfactor, sampleinterval, evaltime):
    pe = sum(sum(flows * pumpfactor) * sampleinterval) / (evaltime[1] - evaltime[0])
    return pe


def mixingenergy(kla, vol, sampleinterval, evaltime):
    kla1, kla2, kla3, kla4, kla5 = kla
    me = 0.005 * (len(kla1[kla1 < 20])*vol[0] + len(kla2[kla2 < 20])*vol[1] + len(kla3[kla3 < 20])*vol[2] + len(kla4[kla4 < 20])*vol[3] + len(kla5[kla5 < 20])*vol[4]) * sampleinterval * 24 / (evaltime[1] - evaltime[0])
    # me = sum(sum(0.005 * np.array([np.count_nonzero(i) for i in [i < 20 for i in kla]])*np.transpose(vol))) * sampleinterval * 24 / (evaltime[1] - evaltime[0])
    return me


def violation(array_eff, limit, sampleinterval, evaltime):
    violationtime = len(array_eff[array_eff > limit]) * sampleinterval
    violationperc = len(array_eff[array_eff > limit]) * sampleinterval / (evaltime[1] - evaltime[0]) * 100
    return violationtime, violationperc

