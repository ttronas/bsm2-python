"""
Evaluation file to store, export and plot data.
"""

import math

import matplotlib.pyplot as plt
import numpy as np

from bsm2_python.log import logger


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
        self.data_objects: list[DataObject] = []

    def add_new_data(
        self,
        name: str,
        column_names: str | list[str],
        units: str | list[str] | None = None,
        *,
        export: bool = True,
        plot: bool = True,
    ):
        """
        Adds a new DataObject to the data_objects list.

        Parameters
        ----------
        name : str
            Name of the DataObject to be added
        column_names : str or list[str]
            Names of the columns in the DataObject
        units : str or list[str], optional
            Units of the columns in the DataObject, '-' at default, if only one unit is specified it is applied to all
            columns
        export : bool, optional
            If True the data will be exported to the csv file, default is True
        plot : bool, optional
            If True the data will be plotted, default is True

        Returns
        -------
        DataObject
            DataObject that was added
        """
        if any(data_object.name == name for data_object in self.data_objects):
            logger.warning(f'Data object with name {name} already exists')
            return
        if not isinstance(column_names, list):
            column_names = [column_names]
        if units is None:
            units = ['-'] * len(column_names)
        elif units is not None and not isinstance(units, list):
            units = [units] * len(column_names)
        elif len(units) <= len(column_names):
            units = [units[0]] * len(column_names)
        new_data_object = DataObject(name, column_names, units, export=export, plot=plot)
        self.data_objects.append(new_data_object)
        return new_data_object

    def update_data(self, name: str, values: float | list[float] | np.ndarray, timestamp: float):
        """
        Updates the data stored in the DataObject with the specified name.

        Parameters
        ----------
        name : str
            Name of the DataObject whose data is to be updated
        values : float or list[float] or np.ndarray
            Values to be appended to the columns of the DataObject, if only one column exists a single value can be
            used instead of a list
        timestamp : float
            Timestamp to be appended to the timestamps of the DataObject
        """
        if not any(data_object.name == name for data_object in self.data_objects):
            logger.warning(f'No data object with name {name} found')
            return
        for data_object in self.data_objects:
            if data_object.name == name:
                if isinstance(values, np.ndarray):
                    values = values.tolist()
                if not isinstance(values, list) and not isinstance(values, np.ndarray):
                    if len(data_object.column_names) != 1:
                        logger.warning(f'Number of values does not match number of columns in data object {name}')
                        return
                    values = [values]
                elif len(values) != len(data_object.column_names):
                    logger.warning(f'Number of values does not match number of columns in data object {name}')
                    return
                data_object.append(values, timestamp)

    def get_data(self, name: str):
        """
        Returns the DataObject with the specified name.

        Parameters
        ----------
        name : str
            Name of the DataObject to be returned

        Returns
        -------
        DataObject
            DataObject with the specified name
        """
        if not any(data_object.name == name for data_object in self.data_objects):
            logger.warning(f'No data object with name {name} found')
            return
        for data_object in self.data_objects:
            if data_object.name == name:
                return data_object

    def get_index(self, name: str, column_name: str):
        """
        Returns the index of the specified column in the DataObject with the specified name.

        Parameters
        ----------
        name : str
            Name of the DataObject whose column index is to be returned
        column_name : str
            Name of the column whose index is to be returned

        Returns
        -------
        int
            Index of the specified column
        """
        if not any(data_object.name == name for data_object in self.data_objects):
            logger.warning(f'No data object with name {name} found')
            return
        for data_object in self.data_objects:
            if data_object.name == name:
                return data_object.get_index(column_name)

    def get_timestamps(self, name: str):
        """
        Returns the timestamps stored in the DataObject with the specified name.

        Parameters
        ----------
        name : str
            Name of the DataObject whose timestamps are to be returned

        Returns
        -------
        list[float]
            Timestamps of the DataObject
        """
        if not any(data_object.name == name for data_object in self.data_objects):
            logger.warning(f'No data object with name {name} found')
            return
        for data_object in self.data_objects:
            if data_object.name == name:
                return data_object.get_timestamps()

    def export_data(self):
        """
        Exports the data stored in the vars_dicts list to a csv file at the specified filepath.
        """
        if not self.data_objects:
            logger.warning('No data to export')
            return
        with open(self.filepath, 'w', encoding='utf-8') as f:
            header = ''
            for i, data_object in enumerate(self.data_objects):
                if not data_object.export:
                    continue
                # add blank column between data objects
                if i != 0:
                    header += ';'
                # add name and timestamp
                header += data_object.name + ';'
                header += 'timestamp [d];'
                # add column names and units
                for key, value in data_object.data_dict.items():
                    header += key + ' [' + value['unit'] + '];'
            f.write(header + '\n')
            num_rows = max(data_object.num_timestamps for data_object in self.data_objects)
            for row in range(num_rows):
                line = ''
                for i, data_object in enumerate(self.data_objects):
                    if not data_object.export:
                        continue
                    # add blank column underneath data object name
                    line += ';'
                    # add blank column between data objects
                    if i != 0:
                        line += ';'
                    # if current data object still has data write values to the line
                    if row < data_object.num_timestamps:
                        line += str(data_object.timestamps[row]) + ';'
                        for _, value in data_object.data_dict.items():
                            line += str(value['values'][row]) + ';'
                    # if current data object has no data write empty columns to the line
                    else:
                        line += ';;'
                        for _, _ in data_object.data_dict.items():
                            line += ';;'
                f.write(line + '\n')
        logger.info('Data exported to ' + self.filepath)

    def plot_data(self):
        """
        Plots the data stored in the vars_dicts list.
        """
        if not self.data_objects:
            logger.warning('No data to plot')
            return
        for data_object in self.data_objects:
            if not data_object.plot:
                continue
            if data_object.num_timestamps <= 1:
                logger.warning(f'Not enough data to plot for data object {data_object.name}')
                continue
            num_data = data_object.num_columns
            cols = math.ceil(num_data / 4)
            rows = math.ceil(num_data / cols)
            timestamps = data_object.get_timestamps()
            values_list = data_object.get_values()
            fig = plt.figure(1)
            fig.suptitle(data_object.name)
            positions = range(1, num_data + 1)
            for i in range(num_data):
                ax = fig.add_subplot(rows, cols, positions[i])
                ax.plot(timestamps, values_list[i])
                ax.set_xlabel('Timestamp [d]')
                ax.set_ylabel(data_object.column_names[i] + ' [' + data_object.units[i] + ']')
            plt.show()


class DataObject:
    def __init__(
        self,
        name: str,
        column_names: list[str],
        units: list[str] | None = None,
        *,
        export: bool = True,
        plot: bool = True,
    ):
        """
        Creates a DataObject.

        Parameters
        ----------
        name : str
            Name of the data object
        column_names : list[str]
            Names of the columns in the data object
        units : list[str], optional
            Units of the columns in the data object, '-' at default
        export : bool, optional
            If True the data will be exported to the csv file, default is True
        plot : bool, optional
            If True the data will be plotted, default is True
        """
        self.name = name
        self.column_names = column_names
        if units is None:
            self.units = ['-'] * len(column_names)
        else:
            self.units = units
        self.export = export
        self.plot = plot
        self.data_dict = {}
        for i, column_name in enumerate(column_names):
            self.data_dict[column_name] = {'unit': self.units[i], 'values': []}
        self.timestamps: list[float] = []
        self.num_columns = len(column_names)
        self.num_timestamps = 0

    def __repr__(self):
        """
        Returns the string representation of the DataObject.
        Formats data in columns with headers for each column.

        Returns
        -------
        str
            String representation of the DataObject
        """
        output = '\n' + self.name + ':\n'
        headers = ['timestamp [d]']
        for key, _ in self.data_dict.items():
            headers.append(key + ' [' + self.data_dict[key]['unit'] + ']')
        num_chars = max(13, *(len(header) for header in headers))
        header_format = '{:>' + str(num_chars) + '}\t'
        value_format = '{:>' + str(num_chars) + '.5f}\t'
        for header in headers:
            output += header_format.format(header)
        i = 0
        lim_i = 4
        lim_ts = 9
        while i < self.num_timestamps:
            if i == lim_i and self.num_timestamps > lim_ts:
                output += '\n'
                for _ in headers:
                    output += header_format.format('...')
                i = self.num_timestamps - lim_i
                continue
            output += '\n'
            values = [self.timestamps[i]]
            for _, value in self.data_dict.items():
                values.append(value['values'][i])
            for value in values:
                output += value_format.format(value)
            i += 1
        return output + '\n'

    def append(self, values, timestamp):
        """
        Appends values and timestamp to the data object.

        Parameters
        ----------
        values : list[float]
            Values to be appended to the columns of the data object
        timestamp : float
            Timestamp to be appended to the timestamps of the data object
        """
        for i, column_name in enumerate(self.column_names):
            self.data_dict[column_name]['values'].append(values[i])
        self.timestamps.append(timestamp)
        self.num_timestamps += 1

    def get_values(self, column_name: str | None = None):
        """
        Returns the values stored in the data object.

        Parameters
        ----------
        column_name : str, optional
            Name of the column whose values are to be returned, if not specified all values are returned

        Returns
        -------
        2D list
            list over columns containing the values at each timestamp
        """
        if column_name is not None:
            return [self.data_dict[column_name]['values']]
        else:
            values = [value['values'] for _, value in self.data_dict.items()]
            return values

    def get_index(self, column_name: str):
        """
        Returns the index of the specified column in the data object.

        Parameters
        ----------
        column_name : str
            Name of the column whose index is to be returned

        Returns
        -------
        int
            Index of the specified column
        """
        return self.column_names.index(column_name)

    def get_timestamps(self):
        """
        Returns the timestamps stored in the data object.
        """
        return self.timestamps
