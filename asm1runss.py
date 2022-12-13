import numpy as np
import pandas as pd
import time
import asm1init
import settlerinit
import asm1
import settler
import xlsxwriter

PAR = asm1init.PAR  # in Matlab wird nochmal aufgeteilt in die Reaktoren (aber ist immer gleich)

# definition of the reactors:

reactor1 = asm1.ASM1reactor(asm1init.VOL1, asm1init.KLa1, asm1init.SOSAT1, asm1init.XINIT1)
reactor2 = asm1.ASM1reactor(asm1init.VOL2, asm1init.KLa2, asm1init.SOSAT2, asm1init.XINIT2)
reactor3 = asm1.ASM1reactor(asm1init.VOL3, asm1init.KLa3, asm1init.SOSAT3, asm1init.XINIT3)
reactor4 = asm1.ASM1reactor(asm1init.VOL4, asm1init.KLa4, asm1init.SOSAT4, asm1init.XINIT4)
reactor5 = asm1.ASM1reactor(asm1init.VOL5, asm1init.KLa5, asm1init.SOSAT5, asm1init.XINIT5)
settler = settler.Settler(settlerinit.DIM, settlerinit.LAYER, asm1init.Qr, asm1init.Qw, settlerinit.SETTLERINIT)

# CONSTINFLUENT:
y_in = np.array([30, 69.5000000000000, 51.2000000000000, 202.320000000000, 28.1700000000000, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 10.5900000000000, 7, 211.267500000000, 18446, 15, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
simtime = np.arange(timestep, 200, timestep)
y_out5 = asm1init.XINIT5
y_outs = np.array([settlerinit.SI_10, settlerinit.SS_10, settlerinit.XI_10, settlerinit.XS_10, settlerinit.XBH_10, settlerinit.XBA_10, settlerinit.XP_10, settlerinit.SO_10, settlerinit.SNO_10, settlerinit.SNH_10, settlerinit.SND_10, settlerinit.XND_10, settlerinit.SALK_10, settlerinit.TSS_10, asm1init.Qr, settlerinit.T_10, settlerinit.SD1_10, settlerinit.SD2_10, settlerinit.SD3_10, settlerinit.XD4_10, settlerinit.XD5_10])
Qintr = 55338


# # Zeitintervall von Matlab:
# df = pd.read_excel('timesteps_matlab_ss.xlsx', 'mit Qr')
# timeint_list = df.values.tolist()
# timeint = np.array(timeint_list)
# timeint = timeint.transpose()
# simtime = timeint[0]
# laststep = 0

# i = 0
# wb = xlsxwriter.Workbook('results_200_ode_1000Schritte.xlsx')
# ws = wb.add_worksheet('yin1')
# ws1 = wb.add_worksheet('yout1')
# ws2 = wb.add_worksheet('yout2')
# ws3 = wb.add_worksheet('yout3')
# ws4 = wb.add_worksheet('yout4')
# ws5 = wb.add_worksheet('yout5')
# ws6 = wb.add_worksheet('youts')
start = time.perf_counter()

# wb2 = xlsxwriter.Workbook('results_ss.xlsx')
# ws7 = wb2.add_worksheet('mit Qr')

number = 1

for step in simtime:
    # timestep = step - laststep
    if number % 96 == 0.0:
        Zeit = time.ctime()
        print('Aktueller Schritt bei ', Zeit, ':', step)
    y_in_r = (y_in*y_in[14]+y_outs*y_outs[14])/(y_in[14]+y_outs[14])
    y_in_r[14] = y_in[14] + y_outs[14]
    # print('y_in_r:', y_in_r)
    y_in1 = (y_in_r*y_in_r[14]+y_out5*Qintr)/(y_in_r[14]+Qintr)
    y_in1[14] = y_in_r[14]+Qintr
    # print('y_in1:', y_in1)
    # start_asm1 = time.perf_counter()
    y_out1 = reactor1.output(timestep, step, y_in1, PAR)
    y_out2 = reactor2.output(timestep, step, y_out1, PAR)
    y_out3 = reactor3.output(timestep, step, y_out2, PAR)
    y_out4 = reactor4.output(timestep, step, y_out3, PAR)
    y_out5 = reactor5.output(timestep, step, y_out4, PAR)
    # stop_asm1 = time.perf_counter()
    # print('Zeit für ASM1:', stop_asm1 - start_asm1)

    # ws.write_row(i, 0, y_in1)
    # ws1.write_row(i, 0, y_out1)
    # ws2.write_row(i, 0, y_out2)
    # ws3.write_row(i, 0, y_out3)
    # ws4.write_row(i, 0, y_out4)
    # ws5.write_row(i, 0, y_out5)

    # Interner Rücklauf:
    Qintr = 55338
    y_ins = y_out5
    y_ins[14] = y_ins[14] - Qintr
    # start_settler = time.perf_counter()
    y_outs = settler.output(timestep, step, y_ins, settlerinit.SETTLERPAR)
    # stop_settler = time.perf_counter()
    # print('Zeit für Settler:', stop_settler - start_settler)

    # ws6.write_row(i, 0, y_outs)
    # i = i + 1
    # print('y_outs:', y_outs)
    number = number + 1

    # laststep = step

# wb.close()
stop = time.perf_counter()

# ws7.write_row(0, 0, y_out1)
# ws7.write_row(1, 0, y_out2)
# ws7.write_row(2, 0, y_out3)
# ws7.write_row(3, 0, y_out4)
# ws7.write_row(4, 0, y_out5)
# ws7.write_row(5, 0, y_outs)
# wb2.close()

print('Simulationszeit: ', stop - start)
print('Output bei t = 200 d: ', y_outs)
