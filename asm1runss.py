import numpy as np
import pandas as pd
import time
import asm1init
import asm1
import xlsxwriter

PAR = asm1init.PAR  # in Matlab wird nochmal aufgeteilt in die Reaktoren (aber ist immer gleich)

# definition of the reactors:

reactor1 = asm1.ASM1reactor(asm1init.VOL1, asm1init.KLa1, asm1init.SOSAT1, asm1init.XINIT1)
reactor2 = asm1.ASM1reactor(asm1init.VOL2, asm1init.KLa2, asm1init.SOSAT2, asm1init.XINIT2)
reactor3 = asm1.ASM1reactor(asm1init.VOL3, asm1init.KLa3, asm1init.SOSAT3, asm1init.XINIT3)
reactor4 = asm1.ASM1reactor(asm1init.VOL4, asm1init.KLa4, asm1init.SOSAT4, asm1init.XINIT4)
reactor5 = asm1.ASM1reactor(asm1init.VOL5, asm1init.KLa5, asm1init.SOSAT5, asm1init.XINIT5)

# CONSTINFLUENT:
y_in = np.array([30, 69.5000000000000, 51.2000000000000, 202.320000000000, 28.1700000000000, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 10.5900000000000, 7, 211.267500000000, 18446, 15, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
simtime = np.arange(timestep, 200, timestep)
y_out5 = np.zeros(21)
Qintr = 0

# # Zeitintervall von Matlab:
# df = pd.read_excel('timesteps_matlab_ss.xlsx', 'Tabelle1')
# timeint_list = df.values.tolist()
# timeint = np.array(timeint_list)
# timeint = timeint.transpose()
# simtime = timeint[0]
# laststep = 0


start = time.perf_counter()
wb = xlsxwriter.Workbook('results_ss.xlsx')
ws = wb.add_worksheet()
for step in simtime:
    # timestep = step - laststep
    y_in1 = (y_in*y_in[14]+y_out5*Qintr)/(y_in[14]+Qintr)
    y_in1[14] = y_in[14]+Qintr
    y_out1 = reactor1.output(timestep, step, y_in1, PAR)
    y_out2 = reactor2.output(timestep, step, y_out1, PAR)
    y_out3 = reactor3.output(timestep, step, y_out2, PAR)
    y_out4 = reactor4.output(timestep, step, y_out3, PAR)
    y_out5 = reactor5.output(timestep, step, y_out4, PAR)

    # Interner Rücklauf:
    Qintr = 55338
#     # laststep = step

stop = time.perf_counter()

ws.write_row(0, 0, y_out1)
ws.write_row(1, 0, y_out2)
ws.write_row(2, 0, y_out3)
ws.write_row(3, 0, y_out4)
ws.write_row(4, 0, y_out5)
wb.close()

print('Simulationszeit: ', stop - start)
print('Output bei t = 200 d: ', y_out5)