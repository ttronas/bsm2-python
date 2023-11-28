"""
test adm1_bsm2.py
"""


def test_adm1():
    import sys
    import os
    path_name = os.path.dirname(__file__)
    sys.path.append(path_name + '/..')
    import numpy as np
    import time
    from bsm2 import adm1init_bsm2 as adm1init
    from bsm2.adm1_bsm2 import ADM1Reactor

    # definition of the tested Reactor:
    adm1Reactor = ADM1Reactor(adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, adm1init.DIM_D)

    # Constant influent based on digester input from BSM2:
    y_in = np.array([28.0665048629843, 48.9525780251450, 10361.7145189587, 20375.0163964256, 10210.0695779898, 553.280744847661, 3204.66026217631, 0.252251384955929, 1.68714307465010, 28.9098125063162, 4.68341082328394, 906.093288634802, 7.15490225533614, 33528.5561252986, 178.467454963180, 14.8580800598190, 0, 0, 0, 0, 0])

    timestep = 15/(60*24)
    endtime = 200
    simtime = np.arange(0, endtime, timestep)

    y_out2 = np.zeros(21)
    yd_out = np.zeros(51)
    y_out1 = np.zeros(33)

    start = time.perf_counter()

    for step in simtime:

        y_out2, yd_out, y_out1 = adm1Reactor.outputs(timestep, step, y_in, adm1init.T_op)

    stop = time.perf_counter()

    print('Steady state simulation completed after: ', stop - start, 'seconds')
    print('ADM2ASM output at t = 200 d: \n', y_out2)
    print('Digester output at t = 200 d: \n', yd_out)
    print('ASM2ADM output at t = 200 d: \n', y_out1)

    y_out2_matlab = np.array([130.867001078133, 258.578914793426, 17216.2478731405, 2611.48424246013, 0, 0, 626.065138722631, 0, 0, 1442.78815835554, 0.543228909106423, 100.866844640246, 97.8458714891164, 15340.3479407424, 178.467454963180, 14.8580800598190, 0, 0, 0, 0, 0])
    yd_out_matlab = np.array([0.0123944540338264, 0.00554315213373901, 0.107407118608287, 0.0123325315421625, 0.0140030377920409, 0.0175839207665506, 0.0893146999168201, 2.50549777288567e-07, 0.0554902093079791, 0.0951488198572130, 0.0944681760448266, 0.130867001078133, 0.107920876567876, 0.0205168227093124, 0.0842203718393935, 0.0436287447203153, 0.312223303455366, 0.931671731353629, 0.338391073383190, 0.335772103995433, 0.101120511564948, 0.677244256936046, 0.284839584657251, 17.2162478731405, 1.16889929774943e-47, 0.00521009910400889, 178.467454963180, 35, 0, 0, 0, 0, 0, 7.26311153039051, 5.45617723984313e-08, 0.0122839772671708, 0.0139527401096076, 0.0175114420688465, 0.0890351560336280, 0.0856799511249895, 0.00946886873222357, 0.00188401070049740, 0.0925841653443292, 1.10324138525859e-05, 1.65349847338113, 0.0135401278075039, 1.76664330523517e-05, 0.661945347420652, 0.346913398467896, 1.06454415739659, 2708.34311966784])
    y_out1_matlab = np.array([0, 0.0438799178554745, 0, 0, 0, 0, 0, 0, 0, 0.00793259060582358, 0.00197207150628461, 0.0280665048629843, 0, 3.72359464281321, 15.9235202884012, 8.04697968474064, 0, 0, 0, 0, 0, 0, 0, 17.0106468844430, 0, 0.00521009943508387, 178.467454963180, 35, 0, 0, 0, 0, 0])

    print('ASM2ADM output difference to MatLab solution: \n', y_out1_matlab - y_out1)
    print('Digester output difference to MatLab solution: \n', yd_out_matlab - yd_out)
    print('ADM2ASM output difference to MatLab solution: \n', y_out2_matlab - y_out2)

    # indices_names = ["S_su", "S_aa", "S_fa", "S_va", "S_bu", "S_pro", "S_ac", "S_h2", "S_ch4", "S_IC", "S_IN", "S_I", "X_xc", "X_ch", "X_pr", "X_li", "X_su", "X_aa", "X_fa", "X_c4", "X_pro", "X_ac", "X_h2", "X_I", "S_cat", "S_an", "Q_D", "T_D", "S_D1_D", "S_D2_D", "S_D3_D", "X_D4_D", "X_D5_D", "pH", "S_H_ion", "S_hva", "S_hbu", "S_hpro", "S_hac", "S_hco3", "S_CO2", "S_nh3", "S_NH4+", "S_gas_h2", "S_gas_ch4", "S_gas_co2", "p_gas_h2", "p_gas_ch4", "p_gas_co2", "P_gas", "q_gas"]
    # print("Deviation of Digester in percent: ")
    # for i, name in enumerate(indices_names):
    #     difference = (yd_out_matlab[i] - yd_out[i])/(yd_out_matlab[i] + 1e-20) * 100
    #     rounded_difference = round(difference, 2)
    #     print(name, ":", rounded_difference, "%")

    # for i, name in enumerate(indices_names):
    #     round_matlab = round(yd_out_matlab[i], 2)
    #     round_python = round(yd_out[i], 2)
    #     print(name, ":", round_matlab, round_python)

    assert np.allclose(y_out1, y_out1_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(yd_out, yd_out_matlab, rtol=1e-5, atol=1e-5)
    # assert np.allclose(y_out2, y_out2_matlab, rtol=1e0, atol=1e0)


test_adm1()
