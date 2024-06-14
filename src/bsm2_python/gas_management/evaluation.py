import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bsm2_python.gas_management.boiler import Boiler
from bsm2_python.gas_management.chp import CHP
from bsm2_python.gas_management.cooler import Cooler
from bsm2_python.gas_management.fermenter import Fermenter
from bsm2_python.gas_management.flare import Flare
from bsm2_python.gas_management.heat_net import HeatNet
from bsm2_python.gas_management.init import chp_init
from bsm2_python.gas_management.storage import BiogasStorage


class Evaluation:
    def __init__(
        self,
        total_sim_steps: int,
        chps_count: int,
        boilers_count: int,
        chp_report_shape: int,
        boiler_report_shape: int,
        flare_report_shape: int,
        cooler_report_shape: int,
    ):
        """
        Initializes the Evaluation object.
        Contains initially empty _all-lists to be filled with data during simulation.
        """
        self.total_sim_steps = total_sim_steps
        self.chps_count = chps_count
        self.boilers_count = boilers_count
        self.chp_stat_all = np.empty((total_sim_steps, chps_count, chp_report_shape))
        self.boiler_stat_all = np.empty((total_sim_steps, boilers_count, boiler_report_shape))
        self.flare_stat_all = np.empty((total_sim_steps, flare_report_shape))
        self.cooler_stat_all = np.empty((total_sim_steps, cooler_report_shape))
        self.biogas_storage_all = np.empty((total_sim_steps, 4))  # level, tendency, deficiency, surplus
        self.heatnet_all = np.empty((total_sim_steps, 1))  # temperature
        self.fermenter_all = np.empty((total_sim_steps, 3))  # gas production, heat demand, electricity demand
        self.net_electricity_all = np.empty((total_sim_steps, 2))  # electricity from net to wwtp, from wwtp to net
        self.electrolyzer_status_all = np.empty((total_sim_steps, 1))  # electrolyzer status
        self.methanation_status_all = np.empty((total_sim_steps, 1))  # methanation status
        self.chp_status_all = np.empty((total_sim_steps, chps_count))  # chp status
        self.boiler_status_all = np.empty((total_sim_steps, boilers_count))  # boiler status
        self.economics_all = np.empty((total_sim_steps, 3))  # incomes, expenditures, cumulative cash flow

    def calculate_data(
        self,
        step: int,
        fermenter: Fermenter,
        chps: list[CHP],
        boilers: list[Boiler],
        flare: Flare,
        cooler: Cooler,
        biogas_storage: BiogasStorage,
        heat_net: HeatNet,
        incomes: float,
        expenditures: float,
    ):
        """
        Collects data from all modules and stores it in the respective records.
        """
        self.chp_stat_all[step, :, :] = np.array([chp.report_status() for chp in chps])
        self.boiler_stat_all[step, :, :] = np.array([boiler.report_status() for boiler in boilers])
        self.flare_stat_all[step, :] = flare.report_status()
        self.cooler_stat_all[step, :] = cooler.report_status()
        self.biogas_storage_all[step, :] = np.array(
            [biogas_storage.vol, biogas_storage.tendency, biogas_storage.deficiency, biogas_storage.surplus]
        )
        self.heatnet_all[step] = heat_net.temperature
        self.fermenter_all[step] = np.array(
            [fermenter.gas_production, fermenter.heat_demand, fermenter.electricity_demand]
        )
        electricity_demand_wwtp = fermenter.electricity_demand - np.sum(
            [chp.products[chp_init.ELECTRICITY] for chp in chps]
        )
        electricity_production_chps = np.sum([chp.products[chp_init.ELECTRICITY] for chp in chps])
        electricity_diff = electricity_demand_wwtp - electricity_production_chps
        if electricity_diff >= 0:
            self.net_electricity_all[step] = np.array([electricity_diff, 0])
        else:
            self.net_electricity_all[step] = np.array([0, -electricity_diff])
        if step == 0:
            self.economics_all[step] = np.array([incomes, expenditures, incomes - expenditures])
        else:
            self.economics_all[step] = np.array(
                [incomes, expenditures, self.economics_all[step - 1, 2] + incomes - expenditures]
            )

    def display_data(self):
        """
        Evaluates the collected data, creates plots and saves data in output.csv-file.
        """
        chps_data = []
        for i in range(self.chps_count):
            chp_data = pd.DataFrame(
                self.chp_stat_all[:, i, :], columns=['Load', 'Maintenance', 'Electricity', 'Heat', 'Biogas']
            )
            chps_data.append(chp_data)
        boilers_data = []
        for i in range(self.boilers_count):
            boiler_data = pd.DataFrame(self.boiler_stat_all[:, i, :], columns=['Load', 'Maintenance', 'Heat', 'Biogas'])
            boilers_data.append(boiler_data)
        flare_data = pd.DataFrame(self.flare_stat_all[:, (0, 3)], columns=['Load', 'Biogas'])
        cooler_data = pd.DataFrame(self.cooler_stat_all[:, (0, 3)], columns=['Load', 'Heat'])
        biogas_storage_data = pd.DataFrame(
            self.biogas_storage_all, columns=['Level', 'Tendency', 'Deficiency', 'Surplus']
        )
        heatnet_data = pd.DataFrame(self.heatnet_all, columns=['Temperature'])
        fermenter_data = pd.DataFrame(
            self.fermenter_all, columns=['Gas Production', 'Heat Demand', 'Electricity Demand']
        )
        net_electricity_data = pd.DataFrame(
            self.net_electricity_all, columns=['Electricity Net to WWTP', 'Electricity WWTP tp Net']
        )
        economics_data = pd.DataFrame(self.economics_all, columns=['Incomes', 'Expenditures', 'Cumulative Cash Flow'])

        # plots
        plt.rcParams.update({'font.size': 15})

        axes = heatnet_data.plot(subplots=True, figsize=(10, 10), title='Heatnet')
        axes[0].set_ylabel('°C')

        axes = biogas_storage_data.plot(subplots=True, figsize=(10, 10), title='Biogas Storage')
        axes[0].set_ylabel('Nm³')
        axes[1].set_ylabel('Nm³/h')
        axes[2].set_ylabel('Nm³/h')
        axes[3].set_ylabel('Nm³/h')

        axes = fermenter_data.plot(subplots=True, figsize=(10, 10), title='Fermenter')
        axes[0].set_ylabel('Nm³/h')
        axes[1].set_ylabel('kW')
        axes[2].set_ylabel('kW')

        axes = net_electricity_data.plot(subplots=True, figsize=(10, 10), title='Net Electricity')
        axes[0].set_ylabel('kW')
        axes[1].set_ylabel('kW')

        for i in range(self.chps_count):
            axes = chps_data[i].plot(subplots=True, figsize=(10, 10), title=f'CHP{i + 1}')
            axes[0].set_ylabel('-')
            axes[1].set_ylabel('h')
            axes[2].set_ylabel('kW')
            axes[3].set_ylabel('kW')
            axes[4].set_ylabel('Nm³/h')

        for i in range(self.boilers_count):
            axes = boilers_data[i].plot(subplots=True, figsize=(10, 10), title=f'Boiler{i + 1}')
            axes[0].set_ylabel('-')
            axes[1].set_ylabel('h')
            axes[2].set_ylabel('kW')
            axes[3].set_ylabel('Nm³/h')

        axes = flare_data.plot(subplots=True, figsize=(10, 10), title='Flare')
        axes[0].set_ylabel('-')
        axes[1].set_ylabel('Nm³/h')

        axes = cooler_data.plot(subplots=True, figsize=(10, 10), title='Cooler')
        axes[0].set_ylabel('-')
        axes[1].set_ylabel('kW')

        axes = economics_data.plot(subplots=True, figsize=(10, 10), title='Economics')
        axes[0].set_ylabel('€')
        axes[1].set_ylabel('€')
        axes[2].set_ylabel('€')

        plt.show()

    def save_data(self, data_path_base: str):
        """
        Saves the collected data in output.csv-file.
        """
        chps_data = []
        for i in range(self.chps_count):
            chp_data = pd.DataFrame(self.chp_stat_all[:, i, (2, 3, 4)], columns=['Electricity', 'Heat', 'Biogas'])
            chps_data.append(chp_data)
        boilers_data = []
        for i in range(self.boilers_count):
            boiler_data = pd.DataFrame(self.boiler_stat_all[:, i, (2, 3)], columns=['Heat', 'Biogas'])
            boilers_data.append(boiler_data)
        flare_data = pd.DataFrame(self.flare_stat_all[:, 3], columns=['Biogas'])
        # cooler_data = pd.DataFrame(self.cooler_stat_all[:, (0, 3)], columns=['Load', 'Heat'])
        biogas_storage_data = pd.DataFrame(
            self.biogas_storage_all, columns=['Level', 'Tendency', 'Deficiency', 'Surplus']
        )
        heatnet_data = pd.DataFrame(self.heatnet_all, columns=['Temperature'])
        # fermenter_data = pd.DataFrame(
        #     self.fermenter_all, columns=['Gas Production', 'Heat Demand', 'Electricity Demand']
        # )
        net_electricity_data = pd.DataFrame(
            self.net_electricity_all, columns=['Electricity Net to WWTP', 'Electricity WWTP tp Net']
        )
        # economics_data = pd.DataFrame(self.economics_all, columns=['Incomes', 'Expenditures', 'Cumulative Cash Flow'])

        sep_arr = np.full(self.total_sim_steps, [''], dtype=str)
        # NOTE: can just comment out lines you don't need
        output = pd.concat(
            [
                pd.DataFrame(sep_arr, columns=['Net Electricity']),
                net_electricity_data,
                # pd.DataFrame(sep_arr, columns=['Electricity Price']), elec_price_data,
                pd.DataFrame(sep_arr, columns=['Biogas Storage']),
                biogas_storage_data,
                pd.DataFrame(sep_arr, columns=['Flare']),
                flare_data,
                pd.DataFrame(sep_arr, columns=['Heatnet']),
                heatnet_data,
            ],
            axis=1,
        )

        for i in range(self.chps_count):
            output = pd.concat([output, pd.DataFrame(sep_arr, columns=['CHP ' + str(i + 1)]), chps_data[i]], axis=1)

        for i in range(self.boilers_count):
            output = pd.concat(
                [output, pd.DataFrame(sep_arr, columns=['Boiler ' + str(i + 1)]), boilers_data[i]], axis=1
            )

        # output = pd.concat([output, pd.DataFrame(sep_arr, columns=
        #                                          ['Incomes', 'Expenditures', 'Cumulative Cash Flow']),
        #                                          economics_data], axis=1)

        output.to_csv(data_path_base + 'output.csv', sep=';')
