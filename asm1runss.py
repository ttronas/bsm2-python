import numpy as np
import pandas as pd
import time
import asm1init
import settlerinit
import asm1
import settler
import xlsxwriter


# definition of the reactors:

reactor1 = asm1.ASM1reactor(asm1init.VOL1, asm1init.KLa1, asm1init.SOSAT1, asm1init.YINIT1, asm1init.PAR1)
reactor2 = asm1.ASM1reactor(asm1init.VOL2, asm1init.KLa2, asm1init.SOSAT2, asm1init.YINIT2, asm1init.PAR2)
reactor3 = asm1.ASM1reactor(asm1init.VOL3, asm1init.KLa3, asm1init.SOSAT3, asm1init.YINIT3, asm1init.PAR3)
reactor4 = asm1.ASM1reactor(asm1init.VOL4, asm1init.KLa4, asm1init.SOSAT4, asm1init.YINIT4, asm1init.PAR4)
reactor5 = asm1.ASM1reactor(asm1init.VOL5, asm1init.KLa5, asm1init.SOSAT5, asm1init.YINIT5, asm1init.PAR5)
settler = settler.Settler(settlerinit.DIM, settlerinit.LAYER, asm1init.Qr, asm1init.Qw, settlerinit.SETTLERINIT, settlerinit.SETTLERPAR)

# CONSTINFLUENT:
y_in = np.array([30, 69.5000000000000, 51.2000000000000, 202.320000000000, 28.1700000000000, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 10.5900000000000, 7, 211.267500000000, 18446, 15, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(timestep, endtime, timestep)

y_out5 = np.zeros(21)
ys_out = np.zeros(21)
Qintr = 0

reactin = np.zeros((int(endtime/timestep), 21))
react1 = np.zeros((int(endtime/timestep), 21))
react2 = np.zeros((int(endtime/timestep), 21))
react3 = np.zeros((int(endtime/timestep), 21))
react4 = np.zeros((int(endtime/timestep), 21))
react5 = np.zeros((int(endtime/timestep), 21))
settlerout = np.zeros((int(endtime/timestep), 21))
settlerall = np.zeros((int(endtime/timestep), 203))

number = 0

# # Zeitintervall von Matlab:
# df = pd.read_excel('timesteps_matlab_ss.xlsx', 'mit Qr')
# timeint = df.to_numpy()
# timeint = timeint.transpose()
# simtime = timeint[0]
# laststep = 0

start = time.perf_counter()

for step in simtime:
    # timestep = step - laststep
    y_in_r = (y_in*y_in[14]+ys_out*ys_out[14])/(y_in[14]+ys_out[14])
    y_in_r[14] = y_in[14] + ys_out[14]
    y_in1 = (y_in_r*y_in_r[14]+y_out5*Qintr)/(y_in_r[14]+Qintr)
    y_in1[14] = y_in_r[14]+Qintr

    reactin[[number]] = y_in1

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)

    react1[[number]] = y_out1
    react2[[number]] = y_out2
    react3[[number]] = y_out3
    react4[[number]] = y_out4
    react5[[number]] = y_out5

    # Interner Rücklauf:
    Qintr = 55338
    ys_in = y_out5
    ys_in[14] = ys_in[14] - Qintr
    if ys_in[14] < 0.0:
        ys_in[14] = 0.0

    ys_out, ys_out_all = settler.outputs(timestep, step, ys_in)
    settlerout[[number]] = ys_out
    settlerall[[number]] = ys_out_all

    number = number + 1

    # laststep = step

stop = time.perf_counter()

print('Simulationszeit: ', stop - start)
print('Output bei t = 200 d: ', ys_out)

start_writer = time.perf_counter()

dfin = pd.DataFrame(reactin)
df1 = pd.DataFrame(react1)
df2 = pd.DataFrame(react2)
df3 = pd.DataFrame(react3)
df4 = pd.DataFrame(react4)
df5 = pd.DataFrame(react5)
dfs = pd.DataFrame(settlerout)
dfs_all = pd.DataFrame(settlerall)
with pd.ExcelWriter('results_ss_all_ode.xlsx') as writer:
    dfin.to_excel(writer, sheet_name='yin', header=False, index=False)
    df1.to_excel(writer, sheet_name='yout1', header=False, index=False)
    df2.to_excel(writer, sheet_name='yout2', header=False, index=False)
    df3.to_excel(writer, sheet_name='yout3', header=False, index=False)
    df4.to_excel(writer, sheet_name='yout4', header=False, index=False)
    df5.to_excel(writer, sheet_name='yout5', header=False, index=False)
    dfs.to_excel(writer, sheet_name='ysout', header=False, index=False)
    dfs_all.to_excel(writer, sheet_name='ysout_all', header=False, index=False)

output_all = np.zeros((7, 21))
output_all = [react1[number-1], react2[number-1], react3[number-1], react4[number-1], react5[number-1], settlerout[number-1], settler.ys0]

df_all = pd.DataFrame(output_all)
df_all.to_excel("results_ss_ode.xlsx", header=False, index=False)

stop_writer = time.perf_counter()

print('Zeit für Excel: ', stop_writer - start_writer)

