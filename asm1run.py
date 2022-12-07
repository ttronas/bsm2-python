import numpy as np
import pandas as pd
import time
import asm1init
import asm1
import xlsxwriter

PAR = asm1init.PAR  # in Matlab wird nochmal aufgeteilt in die Reaktoren (aber ist immer gleich)

# Anfangswerte aus Matlab für Dynamische Simulation:

df_init = pd.read_excel('results_ss.xlsx', header=None)
XINIT1_list = df_init.loc[0].values.tolist()
XINIT1 = np.array(XINIT1_list)
XINIT2_list = df_init.loc[1].values.tolist()
XINIT2 = np.array(XINIT2_list)
XINIT3_list = df_init.loc[2].values.tolist()
XINIT3 = np.array(XINIT3_list)
XINIT4_list = df_init.loc[3].values.tolist()
XINIT4 = np.array(XINIT4_list)
XINIT5_list = df_init.loc[4].values.tolist()
XINIT5 = np.array(XINIT5_list)

# definition of the reactors:

reactor1 = asm1.ASM1reactor(asm1init.VOL1, asm1init.KLa1, asm1init.SOSAT1, XINIT1)
reactor2 = asm1.ASM1reactor(asm1init.VOL2, asm1init.KLa2, asm1init.SOSAT2, XINIT2)
reactor3 = asm1.ASM1reactor(asm1init.VOL3, asm1init.KLa3, asm1init.SOSAT3, XINIT3)
reactor4 = asm1.ASM1reactor(asm1init.VOL4, asm1init.KLa4, asm1init.SOSAT4, XINIT4)
reactor5 = asm1.ASM1reactor(asm1init.VOL5, asm1init.KLa5, asm1init.SOSAT5, XINIT5)

# Dynamic Influent (Dryinfluent):
df = pd.read_excel('dryinfluent.xlsx', 'Tabelle1', header=None)
df2 = pd.read_excel('sensornoise.xlsx', 'Tabelle1', header = None)

timestep = 1/(60*24)
simtime = np.arange(timestep, 14, timestep)
y_out5 = XINIT5
Qintr = 55338
number = 1

start = time.perf_counter()
row = 0
row2 = 1
y_in_list = df.loc[row, 1:21].values.tolist()
y_in = np.array(y_in_list)

# i = 0
# wb = xlsxwriter.Workbook('results_14.xlsx')
# ws = wb.add_worksheet('yin1')
# ws1 = wb.add_worksheet('yout1')
# ws2 = wb.add_worksheet('yout2')
# ws3 = wb.add_worksheet('yout3')
# ws4 = wb.add_worksheet('yout4')
# ws5 = wb.add_worksheet('yout5')
for step in simtime:
    if number % 15 == 0.0:
        row = row + 1
        y_in_list = df.loc[row, 1:21].values.tolist()
        y_in = np.array(y_in_list)
    y_in1 = (y_in*y_in[14]+y_out5*Qintr)/(y_in[14]+Qintr)
    y_in1[14] = y_in[14]+Qintr
    y_out1 = reactor1.output(timestep, step, y_in1, PAR)
    y_out2 = reactor2.output(timestep, step, y_out1, PAR)
    y_out3 = reactor3.output(timestep, step, y_out2, PAR)
    y_out4 = reactor4.output(timestep, step, y_out3, PAR)
    y_out5 = reactor5.output(timestep, step, y_out4, PAR)
    number = number + 1
    row2 = row2 + 1
    # row = row + 1
#     ws.write_row(i, 0, y_in1)
#     ws1.write_row(i, 0, y_out1)
#     ws2.write_row(i, 0, y_out2)
#     ws3.write_row(i, 0, y_out3)
#     ws4.write_row(i, 0, y_out4)
#     ws5.write_row(i, 0, y_out5)
#     i = i + 1
# wb.close()
stop = time.perf_counter()

print('Simulationszeit: ', stop - start)
print('Output bei t = 200 d: ', y_out5)
