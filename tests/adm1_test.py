"""
test adm1_bsm2.py
"""

import csv
import os
import time

import numpy as np
from tqdm import tqdm

from bsm2_python.bsm2.adm1_bsm2 import ADM1Reactor
from bsm2_python.bsm2.init import adm1init_bsm2 as adm1init
from bsm2_python.log import logger

path_name = os.path.dirname(__file__)


def test_adm1():
    # definition of the tested Reactor:
    adm1_reactor = ADM1Reactor(adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, adm1init.DIM_D)

    # Constant influent based on digester input from BSM2:
    y_in = np.array(
        [
            28.0665048629843,
            48.9525780251450,
            10361.7145189587,
            20375.0163964256,
            10210.0695779898,
            553.280744847661,
            3204.66026217631,
            0.252251384955929,
            1.68714307465010,
            28.9098125063162,
            4.68341082328394,
            906.093288634802,
            7.15490225533614,
            33528.5561252986,
            178.467454963180,
            14.8580800598190,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    timestep = 15 / (60 * 24)
    endtime = 200
    simtime = np.arange(0, endtime, timestep, dtype=float)

    y_out2 = np.zeros(21)
    yd_out = np.zeros(51)
    y_out1 = np.zeros(33)

    start = time.perf_counter()

    for step in simtime:
        y_out2, yd_out, y_out1 = adm1_reactor.output(timestep, step, y_in, adm1init.t_op)

    stop = time.perf_counter()

    logger.info('Steady state simulation completed after: %s seconds', stop - start)
    logger.info('ADM2ASM output at t = %s d: \n%s', endtime, y_out2)
    logger.info('Digester output at t = %s d: \n%s', endtime, yd_out)
    logger.info('ASM2ADM output at t = %s d: \n%s', endtime, y_out1)

    y_out2_matlab = np.array(
        [
            130.867001078133,
            258.578914793426,
            17216.2478731405,
            2611.48424246013,
            0,
            0,
            626.065138722631,
            0,
            0,
            1442.78815835554,
            0.543228909106423,
            100.866844640246,
            97.8458714891164,
            15340.3479407424,
            178.467454963180,
            14.8580800598190,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    yd_out_matlab = np.array(
        [
            0.0123944540338264,
            0.00554315213373901,
            0.107407118608287,
            0.0123325315421625,
            0.0140030377920409,
            0.0175839207665506,
            0.0893146999168201,
            2.50549777288567e-07,
            0.0554902093079791,
            0.0951488198572130,
            0.0944681760448266,
            0.130867001078133,
            0.107920876567876,
            0.0205168227093124,
            0.0842203718393935,
            0.0436287447203153,
            0.312223303455366,
            0.931671731353629,
            0.338391073383190,
            0.335772103995433,
            0.101120511564948,
            0.677244256936046,
            0.284839584657251,
            17.2162478731405,
            1.16889929774943e-47,
            0.00521009910400889,
            178.467454963180,
            35,
            0,
            0,
            0,
            0,
            0,
            7.26311153039051,
            5.45617723984313e-08,
            0.0122839772671708,
            0.0139527401096076,
            0.0175114420688465,
            0.0890351560336280,
            0.0856799511249895,
            0.00946886873222357,
            0.00188401070049740,
            0.0925841653443292,
            1.10324138525859e-05,
            1.65349847338113,
            0.0135401278075039,
            1.76664330523517e-05,
            0.661945347420652,
            0.346913398467896,
            1.06454415739659,
            2708.34311966784,
        ]
    )
    y_out1_matlab = np.array(
        [
            0,
            0.0438799178554745,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.00793259060582358,
            0.00197207150628461,
            0.0280665048629843,
            0,
            3.72359464281321,
            15.9235202884012,
            8.04697968474064,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            17.0106468844430,
            0,
            0.00521009943508387,
            178.467454963180,
            35,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    logger.info('ASM2ADM output difference to MatLab solution: \n%s', y_out1_matlab - y_out1)
    logger.info('Digester output difference to MatLab solution: \n%s', yd_out_matlab - yd_out)
    logger.info('ADM2ASM output difference to MatLab solution: \n%s', y_out2_matlab - y_out2)

    assert np.allclose(y_out1, y_out1_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(yd_out, yd_out_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(y_out2, y_out2_matlab, rtol=1e0, atol=1e0)


test_adm1()


def test_adm1_dyn():
    # definition of the tested Reactor:
    adm1_reactor = ADM1Reactor(adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, adm1init.DIM_D)

    # dynsludge from BSM2 open loop (digesterinpreinterface):
    with open(path_name + '/../src/bsm2_python/data/dynsludge_bsm2.csv', encoding='utf-8-sig') as f:
        data_in = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)

    timestep = 15 / 24 / 60  # 15 minutes in days
    endtime = 50  # data_in[-1, 0]
    data_time = data_in[:, 0]
    simtime = np.arange(0, endtime, timestep, dtype=float)
    y_in = data_in[:, 1:]
    del data_in

    y_out2 = np.zeros(21)
    yd_out = np.zeros(51)
    y_out1 = np.zeros(33)
    y_out2_all = np.zeros((len(simtime), 21))
    yd_out_all = np.zeros((len(simtime), 51))
    y_out1_all = np.zeros((len(simtime), 33))

    start = time.perf_counter()

    for i, step in enumerate(tqdm(simtime)):
        # get influent data that is smaller than and closest to current time step
        y_in_timestep = y_in[np.where(data_time <= step)[0][-1], :]
        y_out2, yd_out, y_out1 = adm1_reactor.output(timestep, step, y_in_timestep, adm1init.t_op)
        y_out2_all[i] = y_out2
        yd_out_all[i] = yd_out
        y_out1_all[i] = y_out1

    stop = time.perf_counter()

    # np.savetxt(path_name + '/../data/test_y_out2_all.csv', y_out2_all, delimiter=',')
    # np.savetxt(path_name + '/../data/test_yd_out_all.csv', yd_out_all, delimiter=',')
    # np.savetxt(path_name + '/../data/test_y_out1_all.csv', y_out1_all, delimiter=',')

    logger.info('Dynamic simulation completed after: %s seconds', stop - start)
    logger.info('ADM2ASM output at t = %s d: \n%s', endtime, y_out2)
    logger.info('Digester output at t = %s d: \n%s', endtime, yd_out)
    logger.info('ASM2ADM output at t = ' + str(endtime) + ' d: \n' + str(y_out1))

    # Values from 50 days dynamic simulation in Matlab (adm1_test_dyn.slx):
    y_out2_matlab = np.array(
        [
            122.169323380570,
            373.819450900786,
            15930.3791334305,
            2822.74629212716,
            0,
            0,
            665.913555821979,
            0,
            0,
            1581.71826254710,
            0.732389244776215,
            110.886490448848,
            107.708499534225,
            14564.2792360348,
            190.028282672942,
            11.4654536074904,
            4.97422833876973e-34,
            0,
            0,
            0,
            0,
        ]
    )  # digesteroutpostinterface
    yd_out_matlab = np.array(
        [
            0.0158644223707781,
            0.00747335964057362,
            0.138824881686416,
            0.0176573708846501,
            0.0198384849638407,
            0.0249402261818895,
            0.149220705172638,
            3.26680461508383e-07,
            0.0577837065506474,
            0.103470184862751,
            0.103918103489806,
            0.122169323380570,
            0.114066916584948,
            0.0250245607222834,
            0.126588647170418,
            0.0519627909858718,
            0.303447749802400,
            1.05545615546113,
            0.317773301465617,
            0.376186696159895,
            0.109378471573500,
            0.713690358370099,
            0.295084199652976,
            15.9303791334305,
            1.73935058975725e-44,
            0.00527377296718055,
            190.028282672942,
            35,
            4.97422833876973e-34,
            0,
            0,
            0,
            0,
            7.28818980923129,
            5.15003512121235e-08,
            0.0175917951195153,
            0.0197712730703650,
            0.0248431163672957,
            0.148779350145835,
            0.0936962837777589,
            0.00977390108499217,
            0.00219305732331866,
            0.101725046166488,
            1.37500807578888e-05,
            1.66550298144290,
            0.0139535611488069,
            2.20182894169380e-05,
            0.666751114336974,
            0.357506028575264,
            1.07994690627664,
            3568.56388540252,
        ]
    )  # digesterout
    y_out1_matlab = np.array(
        [
            0,
            0.0394668990016461,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.00825744707032862,
            0.00177734136409946,
            0.0332152509553435,
            0,
            4.22325080273907,
            18.4073469364402,
            8.91874892350877,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            17.0175264624461,
            0,
            0.00573744057971372,
            190.028282672942,
            35,
            4.97422833876973e-34,
            0,
            0,
            0,
            0,
        ]
    )  # digesterin

    logger.info('ASM2ADM output difference to MatLab solution: \n' + str(y_out1_matlab - y_out1))
    logger.info('Digester output difference to MatLab solution: \n' + str(yd_out_matlab - yd_out))
    logger.info('ADM2ASM output difference to MatLab solution: \n' + str(y_out2_matlab - y_out2))

    assert np.allclose(y_out1, y_out1_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(yd_out, yd_out_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(y_out2, y_out2_matlab, rtol=1e-2, atol=1e-2)


test_adm1_dyn()
