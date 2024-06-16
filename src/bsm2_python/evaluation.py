"""
Evaluation file to store, export and plot data.
"""

import numpy as np
import matplotlib.pyplot as plt
import math

class Evaluation:
    def __init__(
        self,
        filepath
    ):
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
        for key, args in kwargs.items():
            if not (isinstance(args, tuple) and list(map(type, args)) == [list, list, list, float]):
                raise TypeError("args must be a tuple of (list(str), list(str), list(float), float) representing names,"
                                "units, values and timestamp")
            if not any(dictionary.get("names") == args[0] for dictionary in self.vars_dicts):
                self.vars_dicts.append({"names": args[0], "unit": args[1], "values": [args[2]], "timestamps": [args[3]]})
            else:
                for dictionary in self.vars_dicts:
                    if dictionary["names"] == args[0]:
                        dictionary["values"].append(args[2])
                        dictionary["timestamps"].append(args[3])

    def export_data(self):
        """
        Exports the data stored in the vars_dicts list to a csv file at the specified filepath.
        """
        file = self.filepath + "output_evaluation.csv"
        with open(file, "w") as f:
            header = ""
            for i, dictionary in enumerate(self.vars_dicts):
                num_names = len(dictionary["names"])
                if i != 0:
                    header += ";"
                header += "timestamp [d];"
                for col in range(num_names):
                    header += dictionary["names"][col] + " [" + dictionary["unit"][col] + "];"
            f.write(header + "\n")
            num_rows = max(len(dictionary["values"]) for dictionary in self.vars_dicts)
            for row in range(num_rows):
                line = ""
                for i, dictionary in enumerate(self.vars_dicts):
                    if row < len(dictionary["values"]):
                        num_values = len(dictionary["values"][row])
                        if i != 0:
                            line += ";"
                        line += str(dictionary["timestamps"][row]) + ";"
                        for col in range(num_values):
                            if col < len(dictionary["values"][row]):
                                line += str(dictionary["values"][row][col]) + ";"
                    else:
                        line += ";;"
                f.write(line + "\n")
        print("Data exported to " + file)

    def plot_data(self):
        """
        Plots the data stored in the vars_dicts list.
        """
        for dictionary in self.vars_dicts:
            num_data = len(dictionary["names"])
            cols = math.ceil(num_data / 4)
            rows = math.ceil(num_data / cols)
            timestamps = np.array(dictionary["timestamps"])
            values_list = np.array(dictionary["values"])
            values_transposed = np.transpose(values_list)
            fig = plt.figure(1)
            positions = range(1, num_data + 1)
            for i in range(num_data):
                ax = fig.add_subplot(rows, cols, positions[i])
                ax.plot(timestamps, values_transposed[i])
                ax.set_xlabel("Timestamp [d]")
                ax.set_ylabel(dictionary["names"][i] + " [" + dictionary["unit"][i] + "]")
            plt.show()
