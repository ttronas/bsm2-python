"""
Evaluation file to store, export and plot data.
"""

import math

import matplotlib.pyplot as plt
import numpy as np

from bsm2_python.log import logger


# TODO: I basically like this class. However, I would like it to be a little more convenient.
# For example, you could create a DataStore class that, after being initialised with units and names, can store data.
# The DataStore class could e.g. have an append() method, or a __repr__() method to get a nice string representation.
# Further on, you could also have getters and setters for the data... Be creative!
# You can then pass one or more DataStore objects to the Evaluation class
# and it will give you aggregation and plotting methods.
# This way, you have the procedure a little more atomic and flexible - at the moment it is very hard to get
# the data back out of the Evaluation class if you do not want to export/plot it.
class Evaluation:
    def __init__(self, filepath):
        """
        Creates an Evaluation object.

        Parameters
        ----------
        filepath : str
            Path to the file where the data will be exported.
        """
        self.filepath = filepath
        self.vars_dicts = []

    def update_data(self, **kwargs):
        """
        Takes any data of the right format and stores it as a dictionary in the vars_dicts list.
        Data format always has to be a tuple of (list(str), list(str), list(float), float) representing names, units,
        values and timestamp.
        Multiple data tuples can be passed as keyword arguments at once.
        An example of a data tuple would be:
        data = (["a", "b"], ["m3", "kg"], [1.0, 2.0], 0.0)
        """
        for _, args in kwargs.items():
            if not (isinstance(args, tuple) and list(map(type, args)) == [list, list, list, float]):
                raise TypeError(
                    'args must be a tuple of (list(str), list(str), list(float), float) representing names,'
                    'units, values and timestamp'
                )
            if not any(dictionary.get('names') == args[0] for dictionary in self.vars_dicts):
                self.vars_dicts.append(
                    {'names': args[0], 'unit': args[1], 'values': [args[2]], 'timestamps': [args[3]]}
                )
            else:
                for dictionary in self.vars_dicts:
                    if dictionary['names'] == args[0]:
                        dictionary['values'].append(args[2])
                        dictionary['timestamps'].append(args[3])

    def export_data(self):
        """
        Exports the data stored in the vars_dicts list to a csv file at the specified filepath.
        """
        if not self.vars_dicts:
            logger.warning('No data to export')
            return
        with open(self.filepath, 'w', encoding='utf-8') as f:
            header = ''
            for i, dictionary in enumerate(self.vars_dicts):
                num_names = len(dictionary['names'])
                if i != 0:
                    header += ';'
                header += 'timestamp [d];'
                for col in range(num_names):
                    header += dictionary['names'][col] + ' [' + dictionary['unit'][col] + '];'
            f.write(header + '\n')
            num_rows = max(len(dictionary['values']) for dictionary in self.vars_dicts)
            for row in range(num_rows):
                line = ''
                for i, dictionary in enumerate(self.vars_dicts):
                    if row < len(dictionary['values']):
                        num_values = len(dictionary['values'][row])
                        if i != 0:
                            line += ';'
                        line += str(dictionary['timestamps'][row]) + ';'
                        for col in range(num_values):
                            line += str(dictionary['values'][row][col]) + ';'
                    else:
                        line += ';;'
                f.write(line + '\n')
        logger.info('Data exported to ' + self.filepath)

    # TODO: Implement a get_data method to elegantly return the data stored in the vars_dicts list

    def plot_data(self):
        """
        Plots the data stored in the vars_dicts list.
        """
        if not self.vars_dicts:
            logger.warning('No data to plot')
            return
        for dictionary in self.vars_dicts:
            num_data = len(dictionary['names'])
            cols = math.ceil(num_data / 4)
            rows = math.ceil(num_data / cols)
            timestamps = np.array(dictionary['timestamps'])
            values_list = np.array(dictionary['values'])
            values_transposed = np.transpose(values_list)
            fig = plt.figure(1)
            positions = range(1, num_data + 1)
            for i in range(num_data):
                ax = fig.add_subplot(rows, cols, positions[i])
                ax.plot(timestamps, values_transposed[i])
                ax.set_xlabel('Timestamp [d]')
                ax.set_ylabel(dictionary['names'][i] + ' [' + dictionary['unit'][i] + ']')
            plt.show()
